import configparser
import pip

from isee.common import get_env_var, get_file_path


def install_requires(project_dir=None):
    if not project_dir:
        project_dir = get_env_var('GITHUB_WORKSPACE')
    path = get_file_path('setup.cfg', project_dir)
    config = configparser.ConfigParser()
    config.read(path)
    pkgs = [x for x in config['options']['install_requires'].split('\n') if x]
    pip.main(['install'] + pkgs)
