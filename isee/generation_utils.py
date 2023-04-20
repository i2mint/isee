import os
import re
from distutils.version import LooseVersion

import semver
from epythet.autogen import make_autodocs
from epythet.setup_docsrc import make_docsrc

from isee.common import get_env_var, git

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
