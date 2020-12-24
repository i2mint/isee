#!/usr/bin/env python3
import sys

from common import get_env_var, update_file, get_file_path


def update_helpers_tpl(root_path):
    aws_hostname = get_env_var('AWS_HOSTNAME')
    app_name = get_env_var('APP_NAME')
    image_version = get_env_var('IMAGE_VERSION')
    path = get_file_path('_helpers.tpl', root_path)
    pattern = rf'({{{{- define "{app_name}.image" }}}}{aws_hostname}\/{app_name}:)[\d.]+({{{{- end -}}}})'
    update_file(path, pattern, rf'\g<1>{image_version}\g<2>')


def update_chart_config(root_path):
    chart_version = get_env_var('CHART_VERSION')
    path = get_file_path('Chart.yaml', root_path)
    update_file(path, r'version: [\d.]+', f'version: {chart_version}')


def main():
    root_path = get_env_var('HELM_TPL_DIR')
    update_helpers_tpl(root_path)
    update_chart_config(root_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
