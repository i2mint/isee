import os

from isee.common import git


def tag_repo(tag: str, *, git_dir: str = None):
    if git_dir:
        os.chdir(git_dir)
    git('tag', tag)
    git('push', 'origin', tag)
