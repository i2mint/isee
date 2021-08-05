import os
import re

from isee.common import git


def check_in(commit_message='No commit message.'):
    current_changes = git('status', '--porcelain=v1')
    if current_changes:
        branch = os.environ['CI_COMMIT_REF_NAME']
        git('add', '-A')
        git('commit', '-m', f'**CI** {commit_message} [skip ci]')
        git('push', 'origin', f'HEAD:{branch}')
    else:
        print('Nothing to commit.')


def tag_repo(tag: str, git_dir: str = None):
    if git_dir:
        os.chdir(git_dir)
    git('tag', tag)
    git('push', 'origin', tag)


def clone_repository(url, branch=None, target_dir=None, quiet=False):
    args = ['clone', '--depth', '1']
    if quiet:
        args.append('--quiet')
    if branch:
        args.extend(['--branch', branch])
    args.append(url)
    if target_dir:
        args.append(target_dir)
    git(*args)
