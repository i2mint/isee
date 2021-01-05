import os
import re

from isee.common import git


def push_formatted_code():
    _prepare_to_push()
    current_changes = git("status", "--porcelain=v1").decode().strip()
    if current_changes:
        branch = os.environ['CI_COMMIT_REF_NAME']
        git("commit", "-a", "-m", "**CI** Formatted code. [skip ci]")
        git("push", "origin", f"HEAD:{branch}")
    else:
        print('Nothing to commit.')


def tag_repo(tag: str, git_dir: str = None):
    _prepare_to_push(git_dir)
    git("tag", tag)
    git("push", "origin", tag)


def _prepare_to_push(git_dir=None):
    if git_dir:
        os.chdir(git_dir)
    # Transforms the repository URL to the SSH URL if needed
    url = git("remote", "get-url", "--push", "origin").decode().strip()
    http_url_regex = r'https?:\/\/(.*:.*@)?([^\/]+)\/'
    ssh_url = re.sub(http_url_regex, r'git@\2:', url)
    if url != ssh_url:
        git("remote", "set-url", "--push", "origin", ssh_url)