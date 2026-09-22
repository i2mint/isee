# isee.pip_utils

Utilities for reading a project’s declared dependencies and installing them.

These functions back the `isee install-requires` and `isee tests-require`
CLI commands (and therefore the `install-packages` action). They understand
both modern `pyproject.toml` (PEP 621 `[project]`) and legacy `setup.cfg`
projects, preferring `pyproject.toml` whenever it declares a `[project]`
table.

Functions:

- install_requires: Install the project’s runtime dependencies.
- tests_require: Install the project’s test dependencies.
- resolve_install_requires: Resolve (without installing) the runtime deps.
- resolve_tests_require: Resolve (without installing) the test deps.
- read_setup_config: (legacy) Read the setup.cfg file in the project directory.
- build_dependency_wheels: Build dependency wheels for the project.
- extras_require / install_extras: (legacy) setup.cfg extras_require helpers.

### Module Attributes

| [`SETUP_CFG_ENCODING`](#isee.pip_utils.SETUP_CFG_ENCODING)   | `setup.cfg` is read as UTF-8, whatever the locale says -- the same reasoning as `_update_file`'s explicit encoding: otherwise a non-ASCII byte crashes the read under a C/POSIX locale, or (e.g. U+0141 in cp1252) on a Windows runner.   |
|-----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### Functions

| `build_dependency_wheels`(repository_dir, ...)                                                 |                                                                              |
|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| [`extras_require`](#isee.pip_utils.extras_require)([name, project_dir])           | Return a list of packages for the given extras_require key (e.g. 'testing'). |
| [`install_extras`](#isee.pip_utils.install_extras)([name, project_dir])           | Install packages listed under extras_require[name] in setup.cfg.             |
| `install_packages_from_options`(...)                                                           |                                                                              |
| [`install_requires`](#isee.pip_utils.install_requires)(\*[, project_dir])           | Install the project's runtime dependencies.                                  |
| [`read_setup_config`](#isee.pip_utils.read_setup_config)([project_dir])              | (legacy) Read and return the `setup.cfg` ConfigParser for the project.       |
| [`resolve_install_requires`](#isee.pip_utils.resolve_install_requires)(\*[, project_dir])   | Return the project's runtime dependencies as a list of requirement strings.  |
| [`resolve_tests_require`](#isee.pip_utils.resolve_tests_require)(\*[, project_dir, ...]) | Return the project's test dependencies as a list of requirement strings.     |
| [`tests_require`](#isee.pip_utils.tests_require)(\*[, project_dir, test_extras]) | Install the project's test dependencies.                                     |

### isee.pip_utils.SETUP_CFG_ENCODING *= 'utf-8'*

`setup.cfg` is read as UTF-8, whatever the locale says – the same reasoning
as `_update_file`’s explicit encoding: otherwise a non-ASCII byte crashes the
read under a C/POSIX locale, or (e.g. U+0141 in cp1252) on a Windows runner.

### isee.pip_utils.extras_require(name='testing', , project_dir=None)

Return a list of packages for the given extras_require key (e.g. ‘testing’).

If setup.cfg or the section/key is missing return an empty list instead of
raising so callers can safely act on the result.

### isee.pip_utils.install_extras(name='testing', , project_dir=None)

Install packages listed under extras_require[name] in setup.cfg.

This is a convenience wrapper used by CI when present. If no packages are
found the function prints a message and does nothing.

### isee.pip_utils.install_requires(, project_dir=None)

Install the project’s runtime dependencies.

Reads them from `pyproject.toml` `[project].dependencies` when present,
otherwise `setup.cfg` `[options] install_requires`.

### isee.pip_utils.read_setup_config(project_dir=None)

(legacy) Read and return the `setup.cfg` ConfigParser for the project.

Prefer [`resolve_install_requires()`](#isee.pip_utils.resolve_install_requires) / [`resolve_tests_require()`](#isee.pip_utils.resolve_tests_require),
which also understand `pyproject.toml`.

### isee.pip_utils.resolve_install_requires(, project_dir=None)

Return the project’s runtime dependencies as a list of requirement strings.

Reads `[project].dependencies` from `pyproject.toml` when present,
otherwise `[options] install_requires` from `setup.cfg`. Raises a
`RuntimeError` only when neither metadata file exists.

### isee.pip_utils.resolve_tests_require(, project_dir=None, test_extras=('testing', 'test', 'tests', 'dev'))

Return the project’s test dependencies as a list of requirement strings.

Reads `[project.optional-dependencies]` from `pyproject.toml` (the first
of `test_extras` that is present) when a `[project]` table exists,
otherwise `[options] tests_require` from `setup.cfg`. Raises a
`RuntimeError` only when neither metadata file exists.

### isee.pip_utils.tests_require(, project_dir=None, test_extras=('testing', 'test', 'tests', 'dev'))

Install the project’s test dependencies.

Reads them from `pyproject.toml` `[project.optional-dependencies]` (the
first present of `test_extras`) when present, otherwise `setup.cfg`
`[options] tests_require`.
