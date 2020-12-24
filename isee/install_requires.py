#!/usr/bin/env python3
import sys
import configparser
import pip

from common import get_env_var, get_file_path


def main():
    root_path = get_env_var('GITHUB_WORKSPACE')
    path = get_file_path('setup.cfg', root_path)
    config = configparser.ConfigParser()
    config.read(path)
    pkgs = [x for x in config['options']['install_requires'].split('\n') if x]
    pip.main(['install'] + pkgs)

    return 0


if __name__ == "__main__":
    sys.exit(main())
