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


# def update_setup_cfg(*, project_dir=None, version=None):
#     path = _get_setup_filepath("setup.cfg", project_dir)
#     version = version or get_env_var("VERSION")
#     _update_file(path, r"version\s=\s.+", f"version = {version}")


def update_setup_cfg(
    *,
    file_path: str = "setup.cfg",
    version: str = None,
):
    """
    Update the version in setup.cfg file.

    Args:
        file_path: Path to the setup.cfg file
        version: The version to set. If None, tries to get it from the VERSION environment variable.
    """
    from configparser import ConfigParser
    import os
    from pathlib import Path

    def get_env_var(key):
        """Get an environment variable and ensure it's not empty."""
        value = os.environ.get(key, "").strip()
        if not value:
            raise RuntimeError(f"{key} is not defined or is empty!")
        return value

    # Get version from arg or environment
    version = version or get_env_var("VERSION")

    print(f"Updating setup.cfg with version: {version}")

    # Load the config file
    config = ConfigParser()
    config.read(file_path)

    # Update the version
    if "metadata" not in config:
        config["metadata"] = {}

    config["metadata"]["version"] = version

    # Save the updated config
    with open(file_path, "w") as f:
        config.write(f)

    print(f"Updated {file_path} with version {version}")


def update_setup_py(*, project_dir=None, version=None):
    path = _get_setup_filepath("setup.py", project_dir)
    version = version or get_env_var("VERSION")
    _update_file(path, r"version='.+',", f"version='{version}',")


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
