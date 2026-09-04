"""Tools for CI"""

from isee.file_modification_utils import (
    update_helm_tpl,
    update_manifest,
    update_pyproject_toml,
    update_setup_cfg,
    update_setup_py,
)
from isee.generation_utils import gen_semver
from isee.git_utils import tag_repo
from isee.pip_utils import install_requires, tests_require
from isee.pylint_log_synopsis import print_report_followed_by_log

#: The commands ``isee`` exposes, in the order they appear in ``isee --help``.
#: Eight GitHub Action definitions in this repo invoke them by name, so this
#: list -- and every flag these functions' signatures imply -- is a public
#: interface, pinned by ``tests/test_cli_surface.py``.
COMMANDS = [
    update_helm_tpl,
    update_manifest,
    update_pyproject_toml,
    update_setup_cfg,  # NOTE: Deprecating setup.cfg
    update_setup_py,
    gen_semver,
    tag_repo,
    install_requires,
    tests_require,
]


def main():
    """Entry point of the ``isee`` console script."""
    import cw

    raise SystemExit(cw.dispatch(COMMANDS))


if __name__ == "__main__":
    main()
