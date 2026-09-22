# isee.file_modification_utils

This module provides utilities for updating files.

Functions:

- update_helm_tpl: Update the Helm chart template files.
- update_manifest: Update the manifest file.
- update_setup_cfg: Update the setup.cfg file.
- update_setup_py: Update the setup.py file.
- \_get_setup_filepath: Get the setup file path.
- \_update_file: Update the file content.

### Functions

| `update_helm_tpl`()                                                                              |                                            |
|--------------------------------------------------------------------------------------------------|--------------------------------------------|
| `update_manifest`(manifest_path)                                                                 |                                            |
| [`update_pyproject_toml`](#isee.file_modification_utils.update_pyproject_toml)(\*[, file_path, ...])     | Update the version in pyproject.toml file. |
| [`update_setup_cfg`](#isee.file_modification_utils.update_setup_cfg)(\*[, file_path, version, ...]) | Update the version in setup.cfg file.      |
| `update_setup_py`(\*[, project_dir, version])                                                    |                                            |

### isee.file_modification_utils.update_pyproject_toml(, file_path=None, version=None, pkg_dir='.')

Update the version in pyproject.toml file.

* **Parameters:**
  * **file_path** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – (Deprecated) Path to the config file. Use pkg_dir instead.
  * **version** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The version to set. If None, tries to get it from the VERSION environment variable.
  * **pkg_dir** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Directory containing the package config files (default: current directory)

### isee.file_modification_utils.update_setup_cfg(, file_path=None, version=None, pkg_dir='.')

Update the version in setup.cfg file.

#### NOTE
This function is deprecated. For new projects using pyproject.toml,
use update_pyproject_toml instead. This function is kept for backward compatibility.

* **Parameters:**
  * **file_path** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – (Deprecated) Path to the config file. Use pkg_dir instead.
  * **version** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The version to set. If None, tries to get it from the VERSION environment variable.
  * **pkg_dir** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Directory containing the package config files (default: current directory)
