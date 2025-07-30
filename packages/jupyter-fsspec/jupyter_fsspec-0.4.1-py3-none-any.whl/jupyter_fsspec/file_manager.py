from jupyter_core.paths import jupyter_config_dir
from .models import Source, Config
from fsspec.utils import infer_storage_options
from fsspec.core import strip_protocol
from fsspec.implementations.asyn_wrapper import AsyncFileSystemWrapper
import fsspec
import os
import sys
import yaml
import hashlib
import urllib.parse
import logging

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FileSystemManager:
    def __init__(self, config_file, allow_absolute_paths=True):
        self.allow_absolute_paths = allow_absolute_paths
        self.filesystems = {}
        self.name_to_prefix = {}
        self.base_dir = jupyter_config_dir()
        logger.info(f"Using Jupyter config directory: {self.base_dir}")
        self.config_path = os.path.join(self.base_dir, config_file)
        self.config = self.load_config(handle_errors=True)
        self.initialize_filesystems()

    def _safe_join(self, base, path):
        final_path = os.path.abspath(os.path.join(base, path))
        base_path = os.path.abspath(base)
        if not final_path.startswith(base_path):
            raise ValueError("Resolved path escapes the root directory")
        return final_path

    def _encode_key(self, fs_config):
        # fs_path = fs_config['path'].strip('/')
        fs_name = fs_config["name"]
        # combined = f"{fs_config['protocol']}|{fs_path}"
        # combined = f"{fs_name}"
        # encoded_key = urllib.parse.quote(combined, safe='')
        return fs_name

    def _decode_key(self, encoded_key):
        combined = urllib.parse.unquote(encoded_key)
        # fs_protocol, fs_path = combined.split('|', 1)
        fs_name = combined
        # return fs_protocol, fs_path
        return fs_name

    @staticmethod
    def create_default(allow_absolute_paths=True):
        return FileSystemManager(
            config_file="jupyter-fsspec.yaml", allow_absolute_paths=allow_absolute_paths
        )

    @staticmethod
    def validate_config(config_loaded):
        Config.model_validate(config_loaded)

    def retrieve_config_content(self):
        config_path = self.config_path

        with open(config_path, "r") as file:
            config_content = yaml.safe_load(file)

        if not config_content:
            return {}

        self.validate_config(config_content)

        return config_content

    def load_config(self, handle_errors=False):
        config_path = self.config_path

        try:
            if not os.path.exists(config_path):
                logger.debug(
                    f"Config file not found at {config_path}. Creating default file."
                )
                self.create_config_file()
            config_content = self.retrieve_config_content()
            return config_content
        except Exception as e:
            if handle_errors:
                logger.error(f"Error loading configuration file: {e}")
                return {}
            raise

    @staticmethod
    def hash_config(config_content):
        yaml_str = yaml.dump(config_content)
        hash = hashlib.md5(yaml_str.encode("utf-8")).hexdigest()
        return hash

    def create_config_file(self):
        config_path = self.config_path
        config_dir = os.path.dirname(config_path)

        logger.debug(f"Ensuring config directory exists: {config_dir}.")
        os.makedirs(config_dir, exist_ok=True)

        config_path = self.config_path
        placeholder_config = {
            "sources": [
                {"name": "test", "path": "memory://"},
                {"name": "test1", "path": "memory://testing"},
            ]
        }

        config_documentation = """# This file is in you JUPYTER_CONFIG_DIR.\n# Multiple filesystem sources can be configured\n# with a unique `name` field, the `path` which\n# can include the protocol, or can omit it and\n# provide it as a seperate field `protocol`. \n# You can also provide `args` such as `key` \n# and `kwargs` such as `client_kwargs` to\n# the filesystem. More details can be found at https://jupyter-fsspec.readthedocs.io/en/latest/#config-file."""

        yaml_content = yaml.dump(placeholder_config, default_flow_style=False)
        commented_yaml = "\n".join(f"# {line}" for line in yaml_content.splitlines())

        full_content = config_documentation + "\n\n" + commented_yaml
        with open(config_path, "w") as config_file:
            config_file.write(full_content)

        logger.info(f"Configuration file created at {config_path}")

    @staticmethod
    def _get_protocol_from_path(path):
        storage_options = infer_storage_options(path)
        protocol = storage_options.get("protocol", "file")
        return protocol

    @staticmethod
    def construct_fs(fs_protocol, asynchronous, *args, **kwargs):
        return fsspec.filesystem(
            fs_protocol, asynchronous=asynchronous, *args, **kwargs
        )

    def construct_named_fs(self, fs_name, asynchronous=False):
        if fs_name in self.filesystems:
            fs_info = self.filesystems[fs_name]
            fs_protocol = fs_info["protocol"]
            return FileSystemManager.construct_fs(
                fs_protocol, asynchronous, *fs_info["args"], **fs_info["kwargs"]
            )
        return None

    def initialize_filesystems(self):
        new_filesystems = {}
        name_to_prefix = {}

        # Init filesystem
        for fs_config in self.config.get("sources", []):
            config = Source(**fs_config)
            fs_name = config.name
            fs_path = config.path  # path should always be a URL
            args = config.args
            kwargs = config.kwargs

            fs_protocol = self._get_protocol_from_path(fs_path)
            split_path_list = fs_path.split("://", 1)
            protocol_path = fs_protocol + "://"
            prefix_path = "" if len(split_path_list) <= 1 else split_path_list[1]
            if len(split_path_list) == 1 and split_path_list[0] != fs_protocol:
                prefix_path = split_path_list[0]
            name_to_prefix[fs_name] = prefix_path
            key = self._encode_key(fs_config)

            absolute_path = None
            if fs_protocol == "file" and not self.allow_absolute_paths:
                if os.path.isabs(prefix_path):
                    logger.error(
                        f"Failed to initialized filesystem '{fs_name}' at path '{fs_path}', relative path is required."
                    )
                    continue
                try:
                    root_dir = os.getcwd() if not self.allow_absolute_paths else ""
                    absolute_path = self._safe_join(root_dir, prefix_path)
                except ValueError:
                    logger.error(
                        f"Failed to initialize filesystem '{fs_name}' at path '{fs_path}'. Path escapes the root directory."
                    )
                    continue
            if absolute_path:
                self.absolute_path = absolute_path

            canonical_path = protocol_path + key
            logger.debug("fs_protocol: %s", fs_protocol)
            logger.debug("prefix_path: %s", prefix_path)
            logger.debug("canonical_path: %s", canonical_path)

            if fs_protocol == "file" and not os.path.exists(prefix_path):
                logger.error(
                    f"Failed to initialize filesystem '{fs_name}' at path '{fs_path}'. Local filepath not found."
                )
                continue

            # Store the filesystem instance
            fs_info = {
                "instance": None,
                "name": fs_name,
                "protocol": fs_protocol,
                "path": prefix_path,
                "path_url": fs_path,
                "canonical_path": canonical_path,
                "args": args,
                "kwargs": kwargs,
            }
            try:
                fs_class = fsspec.get_filesystem_class(fs_protocol)

                if fs_class.async_impl:
                    fs = FileSystemManager.construct_fs(
                        fs_protocol, True, *args, **kwargs
                    )
                    fs_info["instance"] = fs
                else:
                    sync_fs = FileSystemManager.construct_fs(
                        fs_protocol, False, *args, **kwargs
                    )
                    fs = AsyncFileSystemWrapper(sync_fs)
                    fs_info["instance"] = fs

                logger.debug(
                    f"Initialized filesystem '{fs_name}' with protocol '{fs_protocol}' at path '{fs_path}'"
                )
            except Exception:
                fs_info["instance"] = None
                logger.error(
                    f"Failed to initialize filesystem '{fs_name}' at path '{fs_path}'."
                )

                import traceback

                traceback.print_exc()

                exc_type, exc_value, exc_tb = sys.exc_info()
                error_info = {
                    "type": exc_type.__name__,
                    "message": str(exc_value),
                    "short_traceback": traceback.format_exception_only(
                        exc_type, exc_value
                    )[-1].strip(),
                    "traceback_list": traceback.format_tb(exc_tb),
                }
                fs_info["error"] = error_info

            new_filesystems[key] = fs_info

        self.filesystems = new_filesystems
        self.name_to_prefix = name_to_prefix

    # Same as client.py
    def split_path(self, path):
        key, *relpath = path.split("/", 1)
        return key, relpath[0] if relpath else ""

    def map_paths(self, root_path, key, file_obj_list):
        protocol = self.get_filesystem_protocol(key)
        logger.debug("protocol: %s", protocol)
        logger.debug("initial root path: %s", root_path)

        if not root_path and not (protocol == "file://"):
            return file_obj_list

        if protocol == "file://":
            root = strip_protocol(root_path)
        else:
            root = self.name_to_prefix[key]
        logger.debug("filesystem root: %s", root)

        # TODO: error handling for relative_path
        for item in file_obj_list:
            if "name" in item:
                file_name = item["name"]
                split_paths = file_name.split(root, 1)
                logger.debug("split file name: %s", split_paths)
                relative_path = (
                    split_paths[1] if len(split_paths) > 1 else split_paths[0]
                )
                item["name"] = key + relative_path
        return file_obj_list

    def check_reload_config(self):
        new_config_content = self.load_config()
        hash_new_content = self.hash_config(new_config_content)
        current_config_hash = self.hash_config(self.config)

        if current_config_hash != hash_new_content:
            self.config = new_config_content
            self.initialize_filesystems()

        return new_config_content

    def validate_fs(self, request_type, key, item_path):
        if not key:
            raise ValueError("Missing required parameter `key`")

        fs = self.get_filesystem(key)

        if fs is None:
            raise ValueError(f"No filesystem found for key: {key}")

        # TODO: Add test for empty item_path => root
        if item_path == "":
            if request_type == "get":
                item_path = "" if fs["protocol"] == "file://" else fs["path"]
                return fs, item_path
            else:
                raise ValueError("Missing required parameter `item_path`")

        # fs has prefix_path and name(key)
        # prefix_path is the path URL without the protocol
        prefix_path = fs["path"]

        # check item_path includes name(key) => remove it
        key_slash = key + "/"
        if key_slash in item_path:
            item_path = item_path.replace(key_slash, "")
        elif key in item_path:
            item_path = item_path.replace(key, "")

        # check item_path includes prefix_path
        if prefix_path not in item_path:
            item_path = prefix_path + "/" + item_path

        return fs, item_path

    def get_filesystem(self, key):
        return self.filesystems.get(key)

    def get_filesystem_protocol(self, key):
        filesystem_rep = self.filesystems.get(key)
        return filesystem_rep["protocol"] + "://"
