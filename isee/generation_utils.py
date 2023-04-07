import glob
import os
import re
import subprocess
import sys
from distutils.version import LooseVersion

import semver
from epythet.autogen import make_autodocs
from epythet.setup_docsrc import make_docsrc

from isee.common import get_env_var, git
from isee.file_modification_utils import (
    replace_git_urls_from_requirements_file,
    replace_git_urls_from_setup_cfg_file,
)
from isee.git_utils import clone_repository

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


def generate_project_wheels(project_dir, wheel_generation_dir, github_credentails):
    current_dir = os.getcwd()
    clone_repositories_dir = os.path.join(wheel_generation_dir, 'repositories')
    os.mkdir(clone_repositories_dir)
    wheelhouse_dir = os.path.join(wheel_generation_dir, 'wheelhouse')
    os.mkdir(wheelhouse_dir)
    git_info = _generate_repository_wheels(
        project_dir, clone_repositories_dir, wheelhouse_dir, github_credentails
    )
    os.chdir(current_dir)
    return git_info


def _generate_repository_wheels(
    current_repository, clone_repositories_dir, wheelhouse_dir, github_credentails
):
    requirements_filepath = os.path.join(current_repository, 'requirements.txt')
    setup_cfg_filepath = os.path.join(current_repository, 'setup.cfg')
    git_info = []

    if os.path.isfile(requirements_filepath):
        git_info.extend(
            _generate_wheels_from_requirements_file(
                requirements_filepath,
                clone_repositories_dir,
                wheelhouse_dir,
                github_credentails,
            )
        )
    if os.path.isfile(setup_cfg_filepath):
        git_info.extend(
            _generate_wheels_from_setup_cfg_file(
                setup_cfg_filepath,
                clone_repositories_dir,
                wheelhouse_dir,
                github_credentails,
            )
        )
    return git_info


def _generate_wheels_from_requirements_file(
    requirements_filepath, clone_repositories_dir, wheelhouse_dir, github_credentails
):
    git_info = replace_git_urls_from_requirements_file(
        requirements_filepath, github_credentails
    )
    _generation_sub_repositories_wheels(
        git_info, clone_repositories_dir, wheelhouse_dir, github_credentails
    )
    return git_info


def _generate_wheels_from_setup_cfg_file(
    setup_cfg_filepath, clone_repositories_dir, wheelhouse_dir, github_credentails
):
    git_info = replace_git_urls_from_setup_cfg_file(
        setup_cfg_filepath, github_credentails
    )
    _generation_sub_repositories_wheels(
        git_info, clone_repositories_dir, wheelhouse_dir, github_credentails
    )
    return git_info


def _generation_sub_repositories_wheels(
    git_info, clone_repositories_dir, wheelhouse_dir, github_credentails
):
    def get_existing_wheel_names():
        def extract_wheel_name(filepath):
            filename = os.path.basename(filepath)
            wheel_name_search = re.search(pattern, filename)
            if not wheel_name_search:
                raise RuntimeError(
                    f'Failed to extract the wheel name from "{filename}"'
                )
            return wheel_name_search.group(1)

        pattern = r'(.+)-[0-9]*\.[0-9]*\.[0-9]*.*\.whl'
        filepaths = glob.glob(f'{wheelhouse_dir}/*.whl')
        return [extract_wheel_name(filepath) for filepath in filepaths]

    for dep_git_info in git_info:
        dep_name = dep_git_info['name']
        existing_wheel_names = get_existing_wheel_names()
        if not dep_name in existing_wheel_names:
            target_dir = os.path.join(clone_repositories_dir, dep_name)
            clone_repository(
                url=dep_git_info['url'],
                branch=dep_git_info['branch'],
                target_dir=target_dir,
                quiet=True,
            )
            _generate_repository_wheels(
                target_dir, clone_repositories_dir, wheelhouse_dir, github_credentails
            )
            _run_setup_bdist_wheel(target_dir, wheelhouse_dir)


def _run_setup_bdist_wheel(cwd, dist_dir):
    return subprocess.check_output(
        [sys.executable, 'setup.py', 'bdist_wheel', f'--dist-dir={dist_dir}'], cwd=cwd
    )
