"""The upload wrapper fails a run that published nothing (i2mint/isee#26).

``twine upload --skip-existing`` exits 0 when every file already exists on
PyPI, so CI looked green while no release happened. The shared wrapper the
publishing actions call turns that into an error annotation, a job-summary
line and a non-zero exit. These tests drive it with a fake ``twine``.
"""

import os
import stat
import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "actions"
    / "_shared"
    / "twine-upload-checked.sh"
)

_SKIPPED = (
    "Uploading distributions to https://upload.pypi.org/legacy/\n"
    "WARNING  Skipping graze-0.1.9-py3-none-any.whl because it appears to already exist\n"
    "WARNING  Skipping graze-0.1.9.tar.gz because it appears to already exist\n"
)
_UPLOADED = "Uploading graze-0.1.10.tar.gz\n100% done\n"


def _fake_twine(tmp_path, output, status=0):
    fake = tmp_path / "twine"
    (tmp_path / "out.txt").write_text(output)
    fake.write_text(
        f'#!/usr/bin/env bash\necho "$@" > "{tmp_path}/args.txt"\n'
        f'cat "{tmp_path}/out.txt"\nexit {status}\n'
    )
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    return str(fake)


def _run(tmp_path, output, *, status=0, allow_skip=None):
    summary = tmp_path / "summary.md"
    env = {
        **os.environ,
        "ISEE_TWINE_CMD": _fake_twine(tmp_path, output, status),
        "GITHUB_STEP_SUMMARY": str(summary),
    }
    if allow_skip is not None:
        env["ALLOW_SKIP"] = allow_skip
    proc = subprocess.run(
        ["bash", str(SCRIPT), "dist/*", "--skip-existing"],
        env=env,
        capture_output=True,
        text=True,
    )
    return proc, summary.read_text() if summary.exists() else ""


def test_a_real_upload_passes(tmp_path):
    proc, summary = _run(tmp_path, _UPLOADED)
    assert proc.returncode == 0
    assert "Uploading graze-0.1.10.tar.gz" in proc.stdout
    assert summary == ""
    assert (tmp_path / "args.txt").read_text().split() == ["upload", "dist/*", "--skip-existing"]


def test_skipped_files_fail_the_step_and_say_so(tmp_path):
    proc, summary = _run(tmp_path, _SKIPPED)
    assert proc.returncode == 1
    assert "::error title=Nothing new published to PyPI::" in proc.stdout
    assert "graze-0.1.9-py3-none-any.whl graze-0.1.9.tar.gz" in proc.stdout
    assert "nothing new published to PyPI" in summary
    assert "WARNING  Skipping" in proc.stdout, "twine's own output stays in the log"


def test_allow_skip_warns_instead(tmp_path):
    proc, summary = _run(tmp_path, _SKIPPED, allow_skip="true")
    assert proc.returncode == 0
    assert "::warning title=Nothing new published to PyPI::" in proc.stdout
    assert summary.startswith("### Warning")


def test_a_failing_twine_still_fails(tmp_path):
    proc, _ = _run(tmp_path, "HTTPError: 400 Bad Request\n", status=1)
    assert proc.returncode == 1
    assert "::error title=PyPI upload failed::" in proc.stdout


@pytest.mark.parametrize("action", ["publish", "pypi-upload", "publish-job"])
def test_every_publishing_action_uploads_through_the_wrapper(action):
    yaml = pytest.importorskip("yaml")
    path = SCRIPT.parent.parent / action / "action.yml"
    spec = yaml.safe_load(path.read_text())
    # pypi-upload follows its skip-existing input; the others fail by default
    assert spec["inputs"]["allow-skip"]["default"] in ("false", "")
    runs = [step.get("run", "") for step in spec["runs"]["steps"]]
    assert any('"$GITHUB_ACTION_PATH/../_shared/twine-upload-checked.sh"' in r for r in runs)
    assert not any("twine upload" in r for r in runs), "a bare twine upload remains"


# The issue's own log: rich wrapped the message at 80 columns, in colour.
_WRAPPED = (
    "\x1b[33mWARNING \x1b[0m Skipping some_longer_package_name-1.2.3-py3-none-any.whl because it\n"
    "         appears to already exist\n"
    "\x1b[33mWARNING \x1b[0m Skipping graze-0.1.9.tar.gz because it appears to already    \n"
    "         exist\n"
)


def test_a_wrapped_coloured_skip_message_still_fails(tmp_path):
    proc, _ = _run(tmp_path, _WRAPPED)
    assert proc.returncode == 1
    error = next(l for l in proc.stdout.splitlines() if l.startswith("::error"))
    assert "some_longer_package_name-1.2.3-py3-none-any.whl" in error
    assert "graze-0.1.9.tar.gz" in error


def test_a_filename_split_mid_word_still_fails(tmp_path):
    split = "WARNING  Skipping a_very_long_name-1.0-py3-no\nne-any.whl because it appears to already exist\n"
    proc, _ = _run(tmp_path, split)
    assert proc.returncode == 1
    assert "::error title=Nothing new published to PyPI::" in proc.stdout


def test_twine_gets_room_not_to_wrap(tmp_path):
    fake = tmp_path / "twine"
    fake.write_text('#!/usr/bin/env bash\necho "COLUMNS=$COLUMNS"\n')
    fake.chmod(0o755)
    proc = subprocess.run(
        ["bash", str(SCRIPT)],
        env={**os.environ, "ISEE_TWINE_CMD": str(fake)},
        capture_output=True,
        text=True,
    )
    assert "COLUMNS=500" in proc.stdout


def test_allow_skip_is_case_insensitive(tmp_path):
    proc, _ = _run(tmp_path, _SKIPPED, allow_skip="True")
    assert proc.returncode == 0


def test_unrelated_skipping_and_already_lines_do_not_fail(tmp_path):
    output = "INFO Skipping nothing\n" + _UPLOADED + "this appears to already be configured\n"
    proc, _ = _run(tmp_path, output)
    assert proc.returncode == 0


def test_a_tab_after_skipping_still_fails(tmp_path):
    proc, _ = _run(tmp_path, "WARNING Skipping\tx-1.0.tar.gz because it appears to already exist\n")
    assert proc.returncode == 1
