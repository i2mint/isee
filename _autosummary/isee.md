# isee

Tools for CI

### Module Attributes

| [`COMMANDS`](#isee.COMMANDS)   | The commands `isee` exposes, in the order they appear in `isee --help`.   |
|-------------------------------------------------------------|---------------------------------------------------------------------------|

### Functions

| [`main`](#isee.main)()   | Entry point of the `isee` console script.   |
|-----------------------------------------------------------|---------------------------------------------|

### isee.COMMANDS *= [<function update_helm_tpl>, <function update_manifest>, <function update_pyproject_toml>, <function update_setup_cfg>, <function update_setup_py>, <function gen_semver>, <function tag_repo>, <function install_requires>, <function tests_require>]*

The commands `isee` exposes, in the order they appear in `isee --help`.
Eight GitHub Action definitions in this repo invoke them by name, so this
list – and every flag these functions’ signatures imply – is a public
interface, pinned by `tests/test_cli_surface.py`.

### isee.main()

Entry point of the `isee` console script.

### Modules

| [`common`](isee.common.md#module-isee.common)                                   | This module contains common functions that are used in multiple modules.     |
|--------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| [`file_modification_utils`](isee.file_modification_utils.md#module-isee.file_modification_utils) | This module provides utilities for updating files.                           |
| [`generation_utils`](isee.generation_utils.md#module-isee.generation_utils)               | Generation utils for the isee package.                                       |
| [`git_utils`](isee.git_utils.md#module-isee.git_utils)                             | Utilities for working with git repositories.                                 |
| [`local_cli`](isee.local_cli.md#module-isee.local_cli)                             | Run GitHub Actions workflows locally using act.                              |
| [`pip_utils`](isee.pip_utils.md#module-isee.pip_utils)                             | Utilities for reading a project's declared dependencies and installing them. |
| [`pylint_log_synopsis`](isee.pylint_log_synopsis.md#module-isee.pylint_log_synopsis)         | This module provides utilities for working with pylint logs.                 |
