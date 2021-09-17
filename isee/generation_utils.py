from isee.pip_utils import build_dependency_wheels
from isee.git_utils import clone_repository
import os
import re
import semver
from distutils.version import LooseVersion
from epythet.setup_docsrc import make_docsrc
from epythet.autogen import make_autodocs
from distutils.core import run_setup
import glob

from isee.common import get_env_var, git
from isee.file_modification_utils import (
    replace_git_urls_from_requirements_file,
    replace_git_urls_from_setup_cfg_file,
)

DFLT_NEW_VERSION = '0.1.0'


def gen_semver(
    dir_path: str = None, version_patch_prefix: str = '',
):
    def get_version():
        def bump(latest):
            commit_message = git('show-branch', '--no-name', 'HEAD')
            if re.search(r'\[bump major\]', commit_message):
                return semver.bump_major(latest)
            if re.search(r'\[bump minor\]', commit_message):
                return semver.bump_minor(latest)
            return semver.bump_patch(latest)

        def format_version(version):
            version_parts = version.split('.')
            version_parts[2] = f'{version_patch_prefix}{version_parts[2]}'
            return '.'.join(version_parts)

        tags = git('tag').split('\n')
        pattern = rf'^(\d+.){{2}}{version_patch_prefix}\d+$'
        sorted_versions = sorted(
            [
                x.replace(f'{version_patch_prefix}', '')
                for x in tags
                if re.match(pattern, x)
            ],
            key=LooseVersion,
            reverse=True,
        )
        if len(sorted_versions) > 0:
            new_version = bump(sorted_versions[0])
        else:
            # No tags in the repository
            new_version = DFLT_NEW_VERSION
        return format_version(new_version)

    if dir_path:
        os.chdir(dir_path)
    version = get_version()
    print(version)


def generate_documentation(project_dir=None):
    if not project_dir:
        project_dir = get_env_var('GITHUB_WORKSPACE')
    if not os.path.exists(project_dir + '/docsrc'):
        make_docsrc(project_dir)
    make_autodocs(project_dir)


def generate_project_wheels(project_dir, wheel_generation_dir):
    current_dir = os.getcwd()
    clone_repositories_dir = os.path.join(wheel_generation_dir, 'repositories')
    os.mkdir(clone_repositories_dir)
    wheelhouse_dir = os.path.join(wheel_generation_dir, 'wheelhouse')
    os.mkdir(wheelhouse_dir)
    _generate_repository_wheels(project_dir, clone_repositories_dir, wheelhouse_dir)
    os.chdir(current_dir)


def _generate_repository_wheels(
    current_repository, clone_repositories_dir, wheelhouse_dir
):
    requirements_filepath = os.path.join(current_repository, 'requirements.txt')
    setup_cfg_filepath = os.path.join(current_repository, 'setup.cfg')
    if os.path.isfile(requirements_filepath):
        _generate_wheels_from_requirements_file(
            requirements_filepath,
            current_repository,
            clone_repositories_dir,
            wheelhouse_dir,
        )
    elif os.path.isfile(setup_cfg_filepath):
        _generate_wheels_from_setup_cfg_file(
            setup_cfg_filepath,
            current_repository,
            clone_repositories_dir,
            wheelhouse_dir,
        )


def _generate_wheels_from_requirements_file(
    requirements_filepath, current_repository, clone_repositories_dir, wheelhouse_dir
):
    git_info = replace_git_urls_from_requirements_file(requirements_filepath)
    _generation_sub_repositories_wheels(
        git_info, clone_repositories_dir, wheelhouse_dir
    )


def _generate_wheels_from_setup_cfg_file(
    setup_cfg_filepath, current_repository, clone_repositories_dir, wheelhouse_dir
):
    git_info = replace_git_urls_from_setup_cfg_file(setup_cfg_filepath)
    _generation_sub_repositories_wheels(
        git_info, clone_repositories_dir, wheelhouse_dir
    )


def _generation_sub_repositories_wheels(
    git_info, clone_repositories_dir, wheelhouse_dir
):
    for dep_git_info in git_info:
        dep_name = dep_git_info['name']
        existing_wheel_names = glob.glob(f'{wheelhouse_dir}/*.whl')
        if not any(dep_name in wheel_name for wheel_name in existing_wheel_names):
            target_dir = os.path.join(clone_repositories_dir, dep_name)
            clone_repository(
                url=dep_git_info['url'],
                branch=dep_git_info['branch'],
                target_dir=target_dir,
                quiet=True,
            )
            _generate_repository_wheels(
                target_dir, clone_repositories_dir, wheelhouse_dir
            )
            os.chdir(target_dir)
            run_setup('setup.py', ['bdist_wheel', f'--dist-dir={wheelhouse_dir}'])
