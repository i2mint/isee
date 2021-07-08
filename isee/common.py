import subprocess
import os
import glob


def git(*args):
    return subprocess.check_output(['git'] + list(args)).decode().strip()


def get_env_var(key):
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
