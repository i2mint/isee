"""
This module provides utilities for updating files.

Functions:
- update_helm_tpl: Update the Helm chart template files.
- update_manifest: Update the manifest file.
- update_setup_cfg: Update the setup.cfg file.
- update_setup_py: Update the setup.py file.
- _get_setup_filepath: Get the setup file path.
- _update_file: Update the file content.

"""

import re
import os

from isee.common import get_env_var, get_file_path
import os


def update_helm_tpl():
    def update_helpers_tpl(root_path):
        hostname = get_env_var("AWS_HOSTNAME")
        repository = get_env_var("AWS_REPOSITORY")
        image_version = get_env_var("IMAGE_VERSION")
        path = get_file_path("_helpers.tpl", root_path)
        pattern = rf'({{{{- define "{repository}.image" }}}}{hostname}\/{repository}:).+({{{{- end -}}}})'
        _update_file(path, pattern, rf"\g<1>{image_version}\g<2>")

    def update_chart_config(root_path):
        chart_version = get_env_var("CHART_VERSION")
        path = get_file_path("Chart.yaml", root_path)
        _update_file(path, r"version: [\d.]+", f"version: {chart_version}")

    root_path = get_env_var("HELM_TPL_DIR")
    update_helpers_tpl(root_path)
    update_chart_config(root_path)


def update_manifest(manifest_path: str):
    repository = get_env_var("AWS_REPOSITORY")
    chart_version = get_env_var("CHART_VERSION")
    pattern = rf'("chartName":"adi\/{repository}",(\n\s*)?"chartVersion":")[\d.]+'
    _update_file(manifest_path, pattern, rf"\g<1>{chart_version}")


# NOTE: Deprecating setup.cfg
# def update_setup_cfg(*, project_dir=None, version=None):
#     path = _get_setup_filepath("setup.cfg", project_dir)
#     version = version or get_env_var("VERSION")
#     _update_file(path, r"version\s=\s.+", f"version = {version}")


# NOTE: Deprecating setup.cfg - use update_pyproject_toml for new projects
def update_setup_cfg(
    *,
    file_path: str = None,
    version: str = None,
    pkg_dir: str = ".",
):
    """
    Update the version in setup.cfg file.

    NOTE: This function is deprecated. For new projects using pyproject.toml,
    use update_pyproject_toml instead. This function is kept for backward compatibility.

    Args:
        file_path: (Deprecated) Path to the config file. Use pkg_dir instead.
        version: The version to set. If None, tries to get it from the VERSION environment variable.
        pkg_dir: Directory containing the package config files (default: current directory)
    """
    # NOTE: Deprecating setup.cfg
    version = version or get_env_var("VERSION")

    # If file_path is provided (deprecated usage), extract the directory
    if file_path and file_path != "setup.cfg":
        pkg_dir = os.path.dirname(file_path) or "."

    setup_cfg_path = os.path.join(pkg_dir, "setup.cfg")

    if not os.path.exists(setup_cfg_path):
        print(f"No setup.cfg found in {pkg_dir}, skipping update")
        return

    print(f"Updating setup.cfg version to {version} in {pkg_dir}")
    _update_file(setup_cfg_path, r"version\s=\s.+", f"version = {version}")
    print(f"Successfully updated setup.cfg version to {version}")


def update_pyproject_toml(
    *,
    file_path: str = None,
    version: str = None,
    pkg_dir: str = ".",
):
    """
    Update the version in pyproject.toml file.

    Args:
        file_path: (Deprecated) Path to the config file. Use pkg_dir instead.
        version: The version to set. If None, tries to get it from the VERSION environment variable.
        pkg_dir: Directory containing the package config files (default: current directory)
    """
    version = version or get_env_var("VERSION")

    # If file_path is provided (deprecated usage), extract the directory
    if file_path and file_path != "pyproject.toml":
        pkg_dir = os.path.dirname(file_path) or "."

    pyproject_path = os.path.join(pkg_dir, "pyproject.toml")

    if not os.path.exists(pyproject_path):
        print(f"No pyproject.toml found in {pkg_dir}, skipping update")
        return

    print(f"Updating pyproject.toml version to {version} in {pkg_dir}")

    # Update version in [project] section
    _update_file(
        pyproject_path,
        r'(\[project\][\s\S]*?version\s*=\s*")[^"]*(")',
        rf"\g<1>{version}\g<2>",
    )

    print(f"Successfully updated pyproject.toml version to {version}")


def update_setup_py(*, project_dir=None, version=None):
    path = _get_setup_filepath("setup.py", project_dir)
    version = version or get_env_var("VERSION")
    _update_file(path, r"version='.+',", f"version='{version}',")


# NOTE: Deprecating setup.cfg
def _get_setup_filepath(filename, project_dir):
    project_dir = project_dir or get_env_var("GITHUB_WORKSPACE")
    return os.path.join(project_dir, filename)


def _update_file(path, pattern, replace, content_must_change=False):
    with open(path, "r+") as file:
        content = file.read()
        content_new = re.sub(pattern, replace, content, flags=re.M)
        if content_new == content and content_must_change:
            raise RuntimeError(
                f'File content unchanged. Failed to update file "{path}"!'
            )
        file.seek(0)
        file.write(content_new)
        file.truncate()
