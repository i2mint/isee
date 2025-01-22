"""
Utilities for working with git repositories.

Functions:
- tag_repo: Tag the git repository with a new tag and push it to the remote repository.

"""

import os

from isee.common import git


def tag_repo(tag: str, *, git_dir: str = "."):
    # if git_dir:
    #     os.chdir(git_dir)
    git("tag", tag, work_tree=git_dir)
    git("push", "origin", tag, work_tree=git_dir)
