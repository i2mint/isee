#!/usr/bin/env python3
import sys

from common import get_env_var, update_file, get_file_path


def main():
    root_path = get_env_var('GITHUB_WORKSPACE')
    version = get_env_var('VERSION')
    path = get_file_path('setup.cfg', root_path)
    update_file(path, r"version\s=\s[\d.]+", f"version = {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
