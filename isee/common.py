import subprocess
import os
import glob


def git(*args):
    """
    Execute a git command and return the output.
    """
    try:
        # Attempt to execute the git command and decode the output
        return subprocess.check_output(['git'] + list(args)).decode().strip()
    except subprocess.CalledProcessError as e:
        # Print the error message and return the output
        print(f'Error executing git command: {e}')
        print(f'Standard output: {e.output.decode().strip()}')
        print(f'Exit code: {e.returncode}')
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
        raise RuntimeError(f'{key} is not defined or is empty!')
    return value


def get_file_path(filename, root_path):
    result = glob.glob(root_path + f'/**/{filename}', recursive=True)
    if len(result) == 0:
        raise RuntimeError(
            f'No file with name "{filename}" exist into the directory "{root_path}"!'
        )
    if len(result) > 1:
        raise RuntimeError(
            f'More than one file with name "{filename}" exist into the directory "{root_path}"!'
        )
    return result[0]
