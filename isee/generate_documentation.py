#!/usr/bin/env python3
import sys
from os import path

from common import get_env_var
from epythet.setup_docsrc import make_docsrc
from epythet.autogen import make_autodocs


def main():
    root_path = get_env_var('GITHUB_WORKSPACE')
    if not path.exists(root_path + '/docsrc'):
        make_docsrc(root_path)
    make_autodocs(root_path)


if __name__ == "__main__":
    sys.exit(main())
