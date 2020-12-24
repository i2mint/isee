#!/usr/bin/env python3
import sys
import re
import semver
import os
from distutils.version import LooseVersion

from common import git


def bump(latest):
    commit_message = git("show-branch", "--no-name", "HEAD").decode().strip()
    if re.search(r'\[bump major\]', commit_message):
        return semver.bump_major(latest)
    if re.search(r'\[bump minor\]', commit_message):
        return semver.bump_minor(latest)
    return semver.bump_patch(latest)


def get_version():
    tags_str = git("tag").decode().strip()
    versions = sorted(
        [x for x in tags_str.split('\n') if re.match(r'^(\d+.){2}\d+$', x)],
        key=LooseVersion
    )
    nb_versions = len(versions)
    if nb_versions > 0:
        latest_version = versions[nb_versions - 1]
    else:
        # No tags in the repository
        return "0.1.0"
    return bump(latest_version)


def main():
    dir_path = sys.argv[1] if len(sys.argv) > 1 else None
    if dir_path:
        os.chdir(dir_path)
    version = get_version()
    print(version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
