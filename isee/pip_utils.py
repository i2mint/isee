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


def tests_require(project_dir=None):
    """Install from tests_require in setup.cfg options"""
    if not project_dir:
        project_dir = get_env_var('GITHUB_WORKSPACE')
    path = get_file_path('setup.cfg', project_dir)
    config = configparser.ConfigParser()
    config.read(path)
    pkgs = [x for x in config['options']['tests_require'].split('\n') if x]
    pip.main(['install'] + pkgs)


def build_dependency_wheels(repository_dir, wheelhouse, requirements_filepath=None):
    args = ['wheel', '--wheel-dir', wheelhouse, '--find-links', wheelhouse]
    if requirements_filepath:
        args.extend(['--requirement', requirements_filepath])
    args.extend(['--editable', repository_dir])
    pip.main(args)
