import re
import os

from isee.common import get_env_var, get_file_path


def update_helm_tpl():
    def update_helpers_tpl(root_path):
        hostname = get_env_var('AWS_HOSTNAME')
        repository = get_env_var('AWS_REPOSITORY')
        image_version = get_env_var('IMAGE_VERSION')
        path = get_file_path('_helpers.tpl', root_path)
        pattern = rf'({{{{- define "{repository}.image" }}}}{hostname}\/{repository}:).+({{{{- end -}}}})'
        _update_file(path, pattern, rf'\g<1>{image_version}\g<2>')

    def update_chart_config(root_path):
        chart_version = get_env_var('CHART_VERSION')
        path = get_file_path('Chart.yaml', root_path)
        _update_file(path, r'version: [\d.]+', f'version: {chart_version}')

    root_path = get_env_var('HELM_TPL_DIR')
    update_helpers_tpl(root_path)
    update_chart_config(root_path)


def update_manifest(manifest_path: str):
    repository = get_env_var('AWS_REPOSITORY')
    chart_version = get_env_var('CHART_VERSION')
    pattern = rf'("chartName":"adi\/{repository}",(\n\s*)?"chartVersion":")[\d.]+'
    _update_file(manifest_path, pattern, rf'\g<1>{chart_version}')


def update_setup_cfg(project_dir=None, version=None):
    path = _get_setup_filepath('setup.cfg', project_dir)
    version = version or get_env_var('VERSION')
    _update_file(path, r'version\s=\s.+', f'version = {version}')


def update_setup_py(project_dir=None, version=None):
    path = _get_setup_filepath('setup.py', project_dir)
    version = version or get_env_var('VERSION')
    _update_file(path, r"version='.+',", f"version='{version}',")


def replace_git_urls_from_requirements_file(requirements_filepath):
    pattern = r'git\+(https{0,1}:\/\/.*?\.git)@{0,1}(.*){0,1}#egg=(.*)'
    return _replace_git_urls(requirements_filepath, pattern, -1)


def replace_git_urls_from_setup_cfg_file(setup_cfg_filepath):
    pattern = r'([^\t\s\n]*)\s@\sgit\+(https{0,1}:\/\/.*?\.git)@{0,1}(.*){0,1}'
    return _replace_git_urls(setup_cfg_filepath, pattern)


def _replace_git_urls(filepath, pattern, group_idx_offset=0):
    def _get_idx(raw_idx):
        return (raw_idx + group_idx_offset) % 3

    with open(filepath, 'r') as file:
        content = file.read()
        git_info = [
            {'name': t[_get_idx(0)], 'url': t[_get_idx(1)], 'branch': t[_get_idx(2)]}
            for t in re.findall(pattern, content)
        ]
    name_group_idx = _get_idx(0) + 1
    if git_info:
        _update_file(filepath, pattern, rf'\g<{name_group_idx}>')
    return git_info


def _get_setup_filepath(filename, project_dir):
    project_dir = project_dir or get_env_var('GITHUB_WORKSPACE')
    return os.path.join(project_dir, filename)


def _update_file(path, pattern, replace):
    with open(path, 'r+') as file:
        content = file.read()
        content_new = re.sub(pattern, replace, content, flags=re.M)
        if content_new == content:
            raise RuntimeError(f'Failed to update file "{path}"!')
        file.seek(0)
        file.write(content_new)
        file.truncate()
