"""Tools for CI"""

from isee.file_modification_utils import (
    update_helm_tpl,
    update_manifest,
    update_setup_cfg,
    update_setup_py,
)
from isee.generation_utils import (
    gen_semver,
    generate_documentation,
)
from isee.git_utils import tag_repo
from isee.pip_utils import install_requires, tests_require
from isee.pylint_log_synopsis import print_report_followed_by_log


argh_kwargs = {
    "namespace": "isee",
    "functions": [
        update_helm_tpl,
        update_manifest,
        update_setup_cfg,
        update_setup_py,
        gen_semver,
        generate_documentation,
        tag_repo,
        install_requires,
        tests_require,
    ],
    "namespace_kwargs": {
        "title": "CI support utils",
        "description": "Provide a bunch of useful CI utils.",
    },
}


def main():
    import argh  # pip install argh

    argh.dispatch_commands(argh_kwargs.get("functions", None))


if __name__ == "__main__":
    main()
