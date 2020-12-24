import subprocess
import os
import re
import glob


def git(*args):
    return subprocess.check_output(["git"] + list(args))


def get_env_var(key):
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f'{key} is not defined or is empty!')
    return value


def update_file(path, pattern, replace):
    with open(path, 'r+') as file:
        content = file.read()
        content_new = re.sub(pattern, replace, content, flags=re.M)
        if content_new == content:
            raise RuntimeError(f'Failed to update file "{path}"!')
        file.seek(0)
        file.write(content_new)


def prepare_to_push(git_dir=None):
    if git_dir:
        os.chdir(git_dir)
    # Transforms the repository URL to the SSH URL if needed
    url = git("remote", "get-url", "--push", "origin").decode().strip()
    http_url_regex = r'https?:\/\/(.*:.*@)?([^\/]+)\/'
    ssh_url = re.sub(http_url_regex, r'git@\2:', url)
    if url != ssh_url:
        git("remote", "set-url", "--push", "origin", ssh_url)


def get_file_path(filename, root_path):
    result = glob.glob(root_path + f'/**/{filename}', recursive=True)
    if len(result) == 0:
        raise RuntimeError(f'No file with name "{filename}" exist into the directory "{root_path}"!')
    if len(result) > 1:
        raise RuntimeError(f'More than one file with name "{filename}" exist into the directory "{root_path}"!')
    return result[0]