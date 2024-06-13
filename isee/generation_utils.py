"""Generation utils for the isee package.

Has two main functions:
- gen_semver: Generate a new semantic version based on git commit messages and tags.
- generate_documentation: Generate documentation for the project.

"""

import os
import re
from packaging.version import parse
import semver
from epythet.autogen import make_autodocs
from epythet.setup_docsrc import make_docsrc

from isee.common import get_env_var, git

DFLT_NEW_VERSION = '0.1.0'  # Default version if no tags are found


def get_version(version_patch_prefix: str = ''):
    """
    Get the latest version from git tags and determine the new version based on
    the commit message.
    """

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

    # Get all tags from the git repository
    tags = git('tag').split('\n')
    # Pattern to match versions with the patch prefix
    pattern = rf'^(\d+.){{2}}{version_patch_prefix}\d+$'
    # Filter and sort the versions in descending order
    sorted_versions = sorted(
        [
            x.replace(f'{version_patch_prefix}', '')
            for x in tags
            if re.match(pattern, x)
        ],
        key=parse,
        reverse=True,
    )
    if len(sorted_versions) > 0:
        # If there are existing versions, bump the latest version
        new_version = bump(sorted_versions[0])
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
    - dir_path (str): The directory path where the git repository is located. If None, uses the current directory.
    - version_patch_prefix (str): A prefix to be added to the patch version.

    Returns:
    - None: Prints the new version.
    """

    if dir_path:
        os.chdir(dir_path)  # Change to the specified directory
    version = get_version(version_patch_prefix)  # Generate the new version
    if verbose:
        print(version)  # Print the new version


def generate_documentation(*, project_dir=None):
    if not project_dir:
        project_dir = get_env_var('GITHUB_WORKSPACE')
    if not os.path.exists(project_dir + '/docsrc'):
        make_docsrc(project_dir)
    make_autodocs(project_dir)
