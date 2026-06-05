"""
Utilities for reading a project's declared dependencies and installing them.

These functions back the ``isee install-requires`` and ``isee tests-require``
CLI commands (and therefore the ``install-packages`` action). They understand
both modern ``pyproject.toml`` (PEP 621 ``[project]``) and legacy ``setup.cfg``
projects, preferring ``pyproject.toml`` whenever it declares a ``[project]``
table.

Functions:
- install_requires: Install the project's runtime dependencies.
- tests_require: Install the project's test dependencies.
- resolve_install_requires: Resolve (without installing) the runtime deps.
- resolve_tests_require: Resolve (without installing) the test deps.
- read_setup_config: (legacy) Read the setup.cfg file in the project directory.
- build_dependency_wheels: Build dependency wheels for the project.
- extras_require / install_extras: (legacy) setup.cfg extras_require helpers.

"""

import configparser
import os
import pip

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.10 (pyproject declares tomli as fallback)
    import tomli as tomllib

from isee.common import get_env_var, get_file_path

# Extras (in priority order) treated as the project's "test" dependencies when
# reading [project.optional-dependencies] from a pyproject.toml. The first one
# present wins. Override via the ``test_extras`` argument of tests_require.
DFLT_TEST_EXTRAS = ("testing", "test", "tests", "dev")


# --------------------------------------------------------------------------- #
# Metadata source resolution (pyproject.toml preferred, setup.cfg fallback)
# --------------------------------------------------------------------------- #


def _resolve_project_dir(project_dir=None):
    return project_dir or get_env_var("GITHUB_WORKSPACE")


def _find_file(filename, project_dir):
    """Return the path to ``filename`` within ``project_dir``.

    The project root is preferred; failing that we fall back to a recursive
    search (matching the legacy ``get_file_path`` behaviour). Returns ``None``
    when no such file is found.
    """
    root_candidate = os.path.join(project_dir, filename)
    if os.path.isfile(root_candidate):
        return root_candidate
    try:
        return get_file_path(filename, project_dir)
    except RuntimeError:
        return None


def _load_toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def _metadata_source(project_dir):
    """Detect the project's dependency-metadata source.

    Returns one of:
    - ``("pyproject", data)`` when a ``pyproject.toml`` with a ``[project]``
      table is present (``data`` is the parsed toml dict),
    - ``("setup_cfg", config)`` when only a ``setup.cfg`` is present
      (``config`` is a parsed ``ConfigParser``),
    - ``(None, None)`` when neither is found.
    """
    pyproject_path = _find_file("pyproject.toml", project_dir)
    if pyproject_path:
        data = _load_toml(pyproject_path)
        if "project" in data:
            return "pyproject", data
    setup_cfg_path = _find_file("setup.cfg", project_dir)
    if setup_cfg_path:
        config = configparser.ConfigParser()
        config.read(setup_cfg_path)
        return "setup_cfg", config
    return None, None


def _no_metadata_error(project_dir):
    return RuntimeError(
        f'No dependency metadata found in "{project_dir}": expected a '
        f"pyproject.toml with a [project] table or a setup.cfg with an "
        f"[options] section. If this project genuinely declares no "
        f"dependencies, drop the dependency-files step from your CI."
    )


def _cfg_option_list(config, section, key):
    """Return the newline-separated list under ``config[section][key]``."""
    if section not in config:
        return []
    raw = config[section].get(key)
    if not raw:
        return []
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _pyproject_test_deps(data, test_extras):
    optional = data.get("project", {}).get("optional-dependencies", {})
    for name in test_extras:
        if name in optional:
            return list(optional[name])
    return []


# --------------------------------------------------------------------------- #
# Public resolvers (no side effects) and installers
# --------------------------------------------------------------------------- #


def resolve_install_requires(*, project_dir=None):
    """Return the project's runtime dependencies as a list of requirement strings.

    Reads ``[project].dependencies`` from ``pyproject.toml`` when present,
    otherwise ``[options] install_requires`` from ``setup.cfg``. Raises a
    ``RuntimeError`` only when neither metadata file exists.
    """
    project_dir = _resolve_project_dir(project_dir)
    source, meta = _metadata_source(project_dir)
    if source == "pyproject":
        return list(meta.get("project", {}).get("dependencies", []))
    if source == "setup_cfg":
        return _cfg_option_list(meta, "options", "install_requires")
    raise _no_metadata_error(project_dir)


def resolve_tests_require(*, project_dir=None, test_extras=DFLT_TEST_EXTRAS):
    """Return the project's test dependencies as a list of requirement strings.

    Reads ``[project.optional-dependencies]`` from ``pyproject.toml`` (the first
    of ``test_extras`` that is present) when a ``[project]`` table exists,
    otherwise ``[options] tests_require`` from ``setup.cfg``. Raises a
    ``RuntimeError`` only when neither metadata file exists.
    """
    project_dir = _resolve_project_dir(project_dir)
    source, meta = _metadata_source(project_dir)
    if source == "pyproject":
        return _pyproject_test_deps(meta, test_extras)
    if source == "setup_cfg":
        return _cfg_option_list(meta, "options", "tests_require")
    raise _no_metadata_error(project_dir)


def _pip_install(pkgs, *, label):
    pkgs = [p for p in pkgs if p]
    if pkgs:
        pip.main(["install"] + pkgs)
    else:
        print(f"No {label} packages to install")


def install_requires(*, project_dir=None):
    """Install the project's runtime dependencies.

    Reads them from ``pyproject.toml`` ``[project].dependencies`` when present,
    otherwise ``setup.cfg`` ``[options] install_requires``.
    """
    _pip_install(resolve_install_requires(project_dir=project_dir), label="install_requires")


def tests_require(*, project_dir=None, test_extras=DFLT_TEST_EXTRAS):
    """Install the project's test dependencies.

    Reads them from ``pyproject.toml`` ``[project.optional-dependencies]`` (the
    first present of ``test_extras``) when present, otherwise ``setup.cfg``
    ``[options] tests_require``.
    """
    _pip_install(
        resolve_tests_require(project_dir=project_dir, test_extras=test_extras),
        label="tests_require",
    )


def build_dependency_wheels(repository_dir, wheelhouse, requirements_filepath=None):
    args = ["wheel", "--wheel-dir", wheelhouse, "--find-links", wheelhouse]
    if requirements_filepath:
        args.extend(["--requirement", requirements_filepath])
    args.extend(["--editable", repository_dir])
    pip.main(args)


# --------------------------------------------------------------------------- #
# Legacy setup.cfg helpers (kept for backward compatibility)
# --------------------------------------------------------------------------- #


def read_setup_config(project_dir=None):
    """(legacy) Read and return the ``setup.cfg`` ConfigParser for the project.

    Prefer :func:`resolve_install_requires` / :func:`resolve_tests_require`,
    which also understand ``pyproject.toml``.
    """
    if not project_dir:
        project_dir = get_env_var("GITHUB_WORKSPACE")
    path = get_file_path("setup.cfg", project_dir)
    config = configparser.ConfigParser()
    config.read(path)
    return config


def install_packages_from_options(config_options, key):
    if _p := config_options.get(key):
        pkgs = [x for x in _p.split("\n") if x]
        pip.main(["install"] + pkgs)
    else:
        print(f"No {key} packages to install")


def extras_require(name="testing", *, project_dir=None):
    """Return a list of packages for the given extras_require key (e.g. 'testing').

    If setup.cfg or the section/key is missing return an empty list instead of
    raising so callers can safely act on the result.
    """
    try:
        config = read_setup_config(project_dir)
    except RuntimeError:
        return []

    section = "options.extras_require"
    if section not in config:
        return []

    raw = config[section].get(name)
    if not raw:
        return []

    pkgs = [line.strip() for line in raw.splitlines() if line.strip()]
    return pkgs


def install_extras(name="testing", *, project_dir=None):
    """Install packages listed under extras_require[name] in setup.cfg.

    This is a convenience wrapper used by CI when present. If no packages are
    found the function prints a message and does nothing.
    """
    pkgs = extras_require(name, project_dir=project_dir)
    if pkgs:
        pip.main(["install"] + pkgs)
    else:
        print(f"No extras_require[{name}] packages to install")
