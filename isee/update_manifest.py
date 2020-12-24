#!/usr/bin/env python3
import sys

from common import get_env_var, update_file


def update_chart_version(manifest_path):
    app_name = get_env_var('APP_NAME')
    chart_version = get_env_var('CHART_VERSION')
    pattern = rf'("chartName":"adi\/{app_name}",(\n\s*)?"chartVersion":")[\d.]+'
    update_file(manifest_path, pattern, rf'\g<1>{chart_version}')


def main():
    if len(sys.argv) == 1:
        raise RuntimeError('No manifest file to update!')
    manifest_path = sys.argv[1]
    update_chart_version(manifest_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())