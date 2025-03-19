"""Generation utils for the isee package.

Has two main functions:
- gen_semver: Generate a new semantic version based on git commit messages and tags.
- generate_documentation: Generate documentation for the project.

"""

import os
import re
from functools import partial
from warnings import warn

import semver
from epythet.autogen import make_autodocs
from epythet.setup_docsrc import make_docsrc

from wads.pack import versions_from_different_sources, validate_versions
from isee.common import get_env_var, git as _git

DFLT_NEW_VERSION = "0.1.0"  # Default version if no tags are found


def get_new_version(
    *,
    work_tree=".",
    version_patch_prefix: str = "",
    action_when_versions_not_valid=warn,
):
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
        commit_message = git("show-branch", "--no-name", "HEAD")
        # Check if the commit message contains bump directives
        if re.search(r"\[bump major\]", commit_message):
            return semver.bump_major(latest)
        if re.search(r"\[bump minor\]", commit_message):
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
        version_parts = version.split(".")
        version_parts[2] = f"{version_patch_prefix}{version_parts[2]}"
        return ".".join(version_parts)

    versions = versions_from_different_sources(work_tree)

    validate_versions(versions, action_when_not_valid=action_when_versions_not_valid)

    # Take the highest version from the different sources to be the latest version
    latest_version = max(filter(None, versions.values()), key=semver.VersionInfo.parse)

    if latest_version:
        # If there are existing versions, bump the latest version
        new_version = bump(latest_version)
    else:
        # No versions found so, use the default version
        new_version = DFLT_NEW_VERSION
    return format_version(new_version)


def gen_semver(
    *, dir_path: str = None, version_patch_prefix: str = "", output_mode: str = "auto"
):
    """
    Generate a new semantic version based on git commit messages and tags.

    Args:
    - dir_path (str): The directory path where the git repository is located.
        If None, uses the current directory.
    - version_patch_prefix (str): A prefix to be added to the patch version.
    - output_mode (str): How to output the version:
        - "auto": Detect if running in GitHub Actions and adjust accordingly
        - "print": Only print to stdout (for shell capture)
        - "return": Only return (for Python API use)
        - "both": Both print and return

    Returns:
    - str: The new version string if output_mode is "return" or "both".
    - None: If output_mode is "print".
    """
    import os

    # Determine if running in GitHub Actions
    in_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"

    if output_mode == "auto":
        # Auto-detect the best output mode
        output_mode = "print" if in_github_actions else "return"

    work_tree = dir_path or os.path.abspath(".")

    # Generate the new version:
    version = get_new_version(
        work_tree=work_tree, version_patch_prefix=version_patch_prefix
    )

    if version is None:
        raise ValueError("No version found")

    # Handle output based on the mode
    if output_mode in ("print", "both"):
        # Print clean version string with no extra characters
        print(version.strip())

    if output_mode in ("return", "both"):
        return version

    return None


def generate_documentation(*, project_dir=None):
    if not project_dir:
        project_dir = get_env_var("GITHUB_WORKSPACE")
    if not os.path.exists(project_dir + "/docsrc"):
        make_docsrc(project_dir)
    make_autodocs(project_dir)
