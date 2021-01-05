import os
import re
import semver
from distutils.version import LooseVersion
from epythet.setup_docsrc import make_docsrc
from epythet.autogen import make_autodocs

from isee.common import get_env_var, git


def gen_semver(dir_path: str = None):
    def get_version():
        def bump(latest):
            commit_message = (
                git('show-branch', '--no-name', 'HEAD').decode().strip()
            )
            if re.search(r'\[bump major\]', commit_message):
                return semver.bump_major(latest)
            if re.search(r'\[bump minor\]', commit_message):
                return semver.bump_minor(latest)
            return semver.bump_patch(latest)

        tags_str = git('tag').decode().strip()
        versions = sorted(
            [
                x
                for x in tags_str.split('\n')
                if re.match(r'^(\d+.){2}\d+$', x)
            ],
            key=LooseVersion,
        )
        nb_versions = len(versions)
        if nb_versions > 0:
            latest_version = versions[nb_versions - 1]
        else:
            # No tags in the repository
            return '0.1.0'
        return bump(latest_version)

    if dir_path:
        os.chdir(dir_path)
    version = get_version()
    print(version)


def generate_documentation():
    root_path = get_env_var('GITHUB_WORKSPACE')
    if not os.path.exists(root_path + '/docsrc'):
        make_docsrc(root_path)
    make_autodocs(root_path)
