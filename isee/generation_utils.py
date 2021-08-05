from isee.pip_utils import build_wheel
from isee.git_utils import clone_repository
import os
import re
import semver
from distutils.version import LooseVersion
from epythet.setup_docsrc import make_docsrc
from epythet.autogen import make_autodocs

from isee.common import get_env_var, git
from isee.file_modification_utils import replace_git_urls_from_requirements_file, replace_git_urls_from_setup_cfg_file


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
            new_version = '0.1.0'
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


def generate_git_dependency_wheels(project_dir, wheel_generation_dir):
    repositories_dir = os.path.join(wheel_generation_dir, 'repositories')
    os.mkdir(repositories_dir)
    wheelhouse_dir = os.path.join(wheel_generation_dir, 'wheelhouse')
    os.mkdir(wheelhouse_dir)
    _generate_repository_wheels(project_dir, repositories_dir, wheelhouse_dir)


def _generate_repository_wheels(repository_dir, repositories_dir, wheelhouse_dir):
    requirements_filepath = os.path.join(repository_dir, 'requirements.txt')
    setup_cfg_filepath = os.path.join(repository_dir, 'setup.cfg')
    if os.path.isfile(requirements_filepath):
        _generate_wheels_from_requirements_file(requirements_filepath, repositories_dir, wheelhouse_dir)
    elif os.path.isfile(setup_cfg_filepath):
        _generate_wheels_from_setup_cfg_file(setup_cfg_filepath, repositories_dir, wheelhouse_dir)


def _generate_wheels_from_requirements_file(requirements_filepath, repositories_dir, wheelhouse_dir):
    git_info = replace_git_urls_from_requirements_file(requirements_filepath)
    _generate_wheels(git_info, repositories_dir, wheelhouse_dir)


def _generate_wheels_from_setup_cfg_file(setup_cfg_filepath, repositories_dir, wheelhouse_dir):
    git_info = replace_git_urls_from_setup_cfg_file(setup_cfg_filepath)
    _generate_wheels(git_info, repositories_dir, wheelhouse_dir)


def _generate_wheels(git_info, repositories_dir, wheelhouse_dir):
    for dep_git_info in git_info:
        target_dir = os.path.join(repositories_dir, dep_git_info['name'])
        clone_repository(
            url=dep_git_info['url'],
            branch=dep_git_info['version'],
            target_dir=target_dir,
            quiet=True
        )
        _generate_repository_wheels(target_dir, repositories_dir, wheelhouse_dir)
        build_wheel(target_dir, wheelhouse_dir)
