#!/usr/bin/env python3
import sys
import subprocess
import os

from common import git, prepare_to_push


def main():
    prepare_to_push()
    current_changes = git("status", "--porcelain=v1").decode().strip()
    if current_changes:
        branch = os.environ['CI_COMMIT_REF_NAME']
        git("commit", "-a", "-m", "**CI** Formatted code. [skip ci]")
        git("push", "origin", f"HEAD:{branch}")
    else:
        print('Nothing to commit.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
