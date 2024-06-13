"""Generation utils for the isee package.

Has two main functions:
- gen_semver: Generate a new semantic version based on git commit messages and tags.
- generate_documentation: Generate documentation for the project.

"""

import os
import re
from functools import partial
from packaging.version import parse
import semver
from epythet.autogen import make_autodocs
from epythet.setup_docsrc import make_docsrc

from wads.pack import versions_from_different_sources, validate_versions
from isee.common import get_env_var, git as _git

DFLT_NEW_VERSION = '0.1.0'  # Default version if no tags are found


def get_new_version(*, work_tree='.', version_patch_prefix: str = ''):
    """
    Get the latest version from git tags and determine the new version based on
    the commit message.
    """

    work_tree = os.path.expanduser(os.path.abspath(work_tree))

    git = partial(_git, work_tree=work_tree)

    def bump(latest):
        """
        Bump the version based on the commit message.

        Args:
        - latest (str): The latest version.

        Returns:
        - str: The new bumped version.
        """
        # Get the latest commit message
        commit_message = git('show-branch', '--no-name', 'HEAD')
        # Check if the commit message contains bump directives
        if re.search(r'\[bump major\]', commit_message):
            return semver.bump_major(latest)
        if re.search(r'\[bump minor\]', commit_message):
            return semver.bump_minor(latest)
        # Default to bumping the patch version
        return semver.bump_patch(latest)

    def format_version(version):
        """
        Format the version by adding the patch prefix.

        Args:
        - version (str): The version to format.

        Returns:
        - str: The formatted version.
        """
        version_parts = version.split('.')
        version_parts[2] = f'{version_patch_prefix}{version_parts[2]}'
        return '.'.join(version_parts)

    versions = versions_from_different_sources(work_tree)
    validate_versions(versions)
    current_version = versions.get('current_pypi')

    if current_version:
        # If there are existing versions, bump the latest version
        new_version = bump(current_version)
    else:
        # No tags in the repository, use the default version
        new_version = DFLT_NEW_VERSION
    return format_version(new_version)


def gen_semver(
    *,
    dir_path: str = None,
    version_patch_prefix: str = '',
    verbose=True,
):
    """
    Generate a new semantic version based on git commit messages and tags.

    Args:
    - dir_path (str): The directory path where the git repository is located.
        If None, uses the current directory.
    - version_patch_prefix (str): A prefix to be added to the patch version.

    Returns:
    - None: Prints the new version.
    """

    # if dir_path:
    #     os.chdir(dir_path)  # Change to the specified directory
    work_tree = dir_path or os.path.abspath('.')
    # Generate the new version:
    version = get_new_version(
        work_tree=work_tree, version_patch_prefix=version_patch_prefix
    )
    if version is None:
        raise ValueError('No version found')
    print(version)
    # if verbose:
    #     print(f"New version: {version}")  # Print the new version


def generate_documentation(*, project_dir=None):
    if not project_dir:
        project_dir = get_env_var('GITHUB_WORKSPACE')
    if not os.path.exists(project_dir + '/docsrc'):
        make_docsrc(project_dir)
    make_autodocs(project_dir)
