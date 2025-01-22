"""
This module contains common functions that are used in multiple modules.

Functions:
- git: Execute a git command and return the output.
- get_env_var: Get the value of an environment variable.
- get_file_path: Get the file path of a file in a directory.

"""

import subprocess
import os
import glob
from wads.util import git as wads_git


def git(*args, work_tree=".", git_dir=None):
    """
    Execute a git command and return the output.

    >>> git('status')  # doctest: +SKIP
    On branch master
    Your branch is up to date with 'origin/master'.
    <BLANKLINE>
    nothing to commit, working tree clean

    """

    try:
        # return subprocess.check_output(['git'] + list(args)).decode().strip()  # OLD
        return wads_git(" ".join(args), work_tree=work_tree, git_dir=git_dir)
    except subprocess.CalledProcessError as e:
        # Print the error message and return the output
        print(f"Error executing git command: {e}")
        print(f"Standard output: {e.output.decode().strip()}")
        print(f"Exit code: {e.returncode}")
        return e.output.decode().strip()


def get_env_var(key):
    """
    Get the value of an environment variable.
    If the variable is not defined or is empty, raise a RuntimeError.

    :param key: The name of the environment variable.
    :return: The value of the environment variable.

    :raise RuntimeError: If the environment variable is not defined or is empty.

    >>> import os
    >>> os.environ['TEST'] = 'test'
    >>> get_env_var('TEST')
    'test'

    >>> get_env_var('TEST2')
    Traceback (most recent call last):
    ...
    RuntimeError: TEST2 is not defined or is empty!

    >>> os.environ['TEST3'] = ''
    >>> get_env_var('TEST3')
    Traceback (most recent call last):
    ...
    RuntimeError: TEST3 is not defined or is empty!
    """
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"{key} is not defined or is empty!")
    return value


def get_file_path(filename, root_path):
    result = glob.glob(root_path + f"/**/{filename}", recursive=True)
    if len(result) == 0:
        raise RuntimeError(
            f'No file with name "{filename}" exist into the directory "{root_path}"!'
        )
    if len(result) > 1:
        raise RuntimeError(
            f'More than one file with name "{filename}" exist into the directory "{root_path}"!'
        )
    return result[0]
