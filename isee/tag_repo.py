#!/usr/bin/env python3
import sys
import os

from common import git, prepare_to_push


def tag_repo(tag, git_dir):
    prepare_to_push(git_dir)
    git("tag", tag)
    git("push", "origin", tag)


def main():
    if len(sys.argv) == 1:
        raise RuntimeError('No tag provided!')
    tag = sys.argv[1]
    git_dir = sys.argv[2] if len(sys.argv) > 2 else None
    tag_repo(tag, git_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
