"""Tests for :mod:`isee.file_modification_utils`.

The one thing worth pinning here is the *encoding* the single write path
(``_update_file``) uses. Every version bump in the fleet goes through it, via
``actions/bump-version-number`` and ``actions/version-bump``, and the files it
edits -- ``pyproject.toml``, ``setup.cfg``, ``Chart.yaml`` -- are UTF-8 by their
own specs. Reading them with the *locale* default instead crashes on any
non-ASCII byte under a C/POSIX locale, and mojibakes or crashes under Windows
cp1252.

The locale has to be forced in a child process: ``mock.patch`` on
``locale.getpreferredencoding`` does not reach CPython's C-level ``open()``.
"""

import os
import subprocess
import sys
import textwrap

import pytest

#: A description exercising both a 2-byte (U+00E9) and two 3-byte (U+201C,
#: U+201D) UTF-8 sequences. The curly quotes matter twice over: 0x9D is
#: undefined in cp1252, so a Windows runner hard-fails on them too.
NON_ASCII_DESCRIPTION = "Café “smart” quotes"

PYPROJECT_TEMPLATE = textwrap.dedent(f"""\
    [project]
    name = "encoding-probe"
    version = "0.1.0"
    description = "{NON_ASCII_DESCRIPTION}"
    """)

#: Force the child onto an ASCII-only locale default. ``PYTHONUTF8=0`` and
#: ``PYTHONCOERCECLOCALE=0`` are both needed: without them CPython quietly
#: promotes a C locale back to UTF-8 and the probe proves nothing.
ASCII_LOCALE_ENV = {
    "LC_ALL": "C",
    "LANG": "C",
    "PYTHONUTF8": "0",
    "PYTHONCOERCECLOCALE": "0",
}

BUMP_SCRIPT = textwrap.dedent("""\
    import sys
    from isee.file_modification_utils import update_pyproject_toml
    update_pyproject_toml(pkg_dir=sys.argv[1], version=sys.argv[2])
    """)


def _bump_in_ascii_locale(pkg_dir, version):
    """Run a version bump in a child interpreter whose default encoding is ASCII."""
    return subprocess.run(
        [sys.executable, "-c", BUMP_SCRIPT, str(pkg_dir), version],
        capture_output=True,
        text=True,
        env={**os.environ, **ASCII_LOCALE_ENV},
    )


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="LC_ALL/LANG do not select the ANSI codepage that Windows would use",
)
def test_version_bump_survives_a_non_utf8_locale(tmp_path):
    """MUTATION: drop ``encoding="utf-8"`` from ``_update_file``'s ``open()``.

    Without it the read blows up with ``UnicodeDecodeError: 'ascii' codec can't
    decode byte 0xc3`` before any substitution happens, so the bump fails and
    the file is left at its old version.
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(PYPROJECT_TEMPLATE, encoding="utf-8")

    result = _bump_in_ascii_locale(tmp_path, "9.9.9")

    assert (
        result.returncode == 0
    ), f"version bump failed under an ASCII locale:\n{result.stderr}"
    updated = pyproject.read_text(encoding="utf-8")
    assert 'version = "9.9.9"' in updated
    assert (
        NON_ASCII_DESCRIPTION in updated
    ), "non-ASCII text was corrupted by the round trip"


def test_version_bump_preserves_non_ascii_bytes(tmp_path):
    """The bytes outside the version line come back byte-for-byte unchanged."""
    from isee.file_modification_utils import update_pyproject_toml

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(PYPROJECT_TEMPLATE, encoding="utf-8")

    update_pyproject_toml(pkg_dir=str(tmp_path), version="9.9.9")

    expected = PYPROJECT_TEMPLATE.replace('version = "0.1.0"', 'version = "9.9.9"')
    assert pyproject.read_bytes() == expected.encode("utf-8")
