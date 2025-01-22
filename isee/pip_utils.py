"""
This module provides utilities for working with pip and setup.cfg files.

Functions:
- read_setup_config: Read the setup.cfg file in the project directory.
- install_packages_from_options: Install packages from the options in setup.cfg.
- install_requires: Install packages from the install_requires option in setup.cfg.
- tests_require: Install packages from the tests_require option in setup.cfg.
- build_dependency_wheels: Build dependency wheels for the project.

"""

import configparser
import pip

from isee.common import get_env_var, get_file_path


def read_setup_config(project_dir=None):
    if not project_dir:
        project_dir = get_env_var("GITHUB_WORKSPACE")
    path = get_file_path("setup.cfg", project_dir)
    config = configparser.ConfigParser()
    config.read(path)
    return config


def install_packages_from_options(config_options, key):
    if _p := config_options.get(key):
        pkgs = [x for x in _p.split("\n") if x]
        pip.main(["install"] + pkgs)
    else:
        print(f"No {key} packages to install")


def install_requires(*, project_dir=None):
    config = read_setup_config(project_dir)
    install_packages_from_options(config["options"], "install_requires")


def tests_require(*, project_dir=None):
    """Install from tests_require in setup.cfg options"""
    config = read_setup_config(project_dir)
    install_packages_from_options(config["options"], "tests_require")


def build_dependency_wheels(repository_dir, wheelhouse, requirements_filepath=None):
    args = ["wheel", "--wheel-dir", wheelhouse, "--find-links", wheelhouse]
    if requirements_filepath:
        args.extend(["--requirement", requirements_filepath])
    args.extend(["--editable", repository_dir])
    pip.main(args)
