"""Characterization test pinning the ``isee`` command line.

``isee`` was dispatched by ``argh`` up to 0.2.77 and is dispatched by :mod:`cw`
from 0.2.78 on. The golden in ``cli_goldens/isee.json`` was recorded from the
**argh** implementation, so what it asserts is not "cw does what cw does" but
"the command line did not move when the dispatcher underneath it was replaced".

That distinction matters more here than almost anywhere in the fleet: eight
GitHub Action definitions in this repository invoke ``isee`` by name with
hand-written argument strings (``isee gen-semver --output-mode=print``,
``isee update-setup-cfg --version="$VERSION"``, ``isee tag-repo $VERSION``,
``isee install-requires``, ``isee tests-require``), and those actions are
consumed by the whole fleet. A renamed flag here is a fleet-wide CI outage that
nothing else in this suite would catch.

The console script is resolved beside ``sys.executable`` rather than through
``PATH``, because ``PATH`` answers a question about the developer's machine and
not about the interpreter running the tests.

What is asserted, per :mod:`cw.testing`'s tier rule: exit code and both streams
in full for every non-``--help`` case, and exit code plus the normalised
``usage:`` line for the ``--help`` cases -- which names every option every
parser has, so a lost flag, a lost short flag or a changed ``nargs`` all show
up. The ``--help`` *body* is compared but reported non-fatally, because CPython
rewrites argparse's own option column between versions. The bodies were verified
byte-identical under ``--strict-help`` on CPython 3.12 at migration time.

Re-record with::

    python -m cw.testing characterize isee --cases <cases-file> \
        -o tests/cli_goldens/isee.json

and only ever alongside a deliberate, documented change to the CLI.
"""

import json
import os
import re
import sys
from pathlib import Path

import pytest

cw_testing = pytest.importorskip(
    "cw.testing", reason="cw is a runtime dependency; skip only in a partial install"
)

GOLDEN = Path(__file__).parent / "cli_goldens" / "isee.json"
ACTIONS_DIR = Path(__file__).parent.parent / "actions"

#: A ``#`` comment, so that prose mentioning a command is not mistaken for a
#: call to it.
_YAML_COMMENT = re.compile(r"#.*$", re.M)

#: ``isee <subcommand>`` where ``isee`` starts a command -- at the start of a
#: line, right after ``run:``, after a pipe/``&&``/``;``, or inside ``$(...)``
#: or backticks. Anchoring on the prefix is what keeps prose like
#: ``echo "Installing isee from pip"`` out of the results.
_ISEE_INVOCATION = re.compile(
    r"(?:^|run:|[|&;(`]|\$\()\s*isee\s+([a-z][a-z0-9-]*)", re.M
)


def _subcommands_invoked_by_this_repos_actions():
    """Every ``isee <subcommand>`` the ``actions/`` definitions actually run.

    Reading them off the YAML rather than maintaining a list by hand is the
    point: a hand-maintained list drifts silently, and drift here is exactly
    the bug this test exists to catch.
    """
    invoked = {}
    for action_yml in sorted(ACTIONS_DIR.glob("*/action.yml")):
        script = _YAML_COMMENT.sub("", action_yml.read_text(encoding="utf-8"))
        for match in _ISEE_INVOCATION.finditer(script):
            invoked.setdefault(match.group(1), set()).add(action_yml.parent.name)
    return invoked


def _console_script(name):
    """The installed console script ``name``, resolved beside ``sys.executable``."""
    bin_dir = Path(sys.executable).parent
    candidates = [bin_dir / name]
    if os.name == "nt":
        candidates = [bin_dir / f"{name}.exe", bin_dir / "Scripts" / f"{name}.exe"]
    return next((c for c in candidates if c.exists()), None)


def test_the_command_line_did_not_move():
    """MUTATION: rename a flag, change a command name, change an exit code.

    Including the no-argument case: argh printed usage to STDOUT and exited 0
    there, where a plain argparse parser with a required subparser exits 2 to
    STDERR. Any CI step that runs bare ``isee`` would flip from pass to fail on
    that difference alone.
    """
    script = _console_script("isee")
    if script is None:
        pytest.skip("console script 'isee' is not installed in this environment")
    cw_testing.assert_replay(GOLDEN, prog=[str(script)])


def test_the_golden_carries_no_machine_specific_prog():
    """MUTATION: re-record and commit without rewriting ``prog``.

    ``characterize`` stores the command it was given, which on the machine that
    records is an absolute path under somebody's home directory. Committing that
    leaks a local path into a public repo AND makes the golden replay against a
    path that exists on exactly one computer.
    """
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert golden["prog"] == ["isee"], (
        f"isee.json records prog={golden['prog']!r}; rewrite it to ['isee'] "
        "before committing (see this module's docstring)"
    )


def test_every_command_the_repo_s_own_actions_invoke_still_exists():
    """MUTATION: drop a command from `isee.COMMANDS`; add an action that calls
    a command that does not exist.

    The golden above would catch a dropped command too, but only as an opaque
    `--help` diff. This says which name went missing, and it reads *both* sides
    of the contract off their sources -- the exposed names off the same list
    `main()` dispatches, the invoked names off the action definitions -- so
    neither side can drift without this failing.

    Both directions of drift have already happened once: `gen_semver` and
    friends were preserved across the argh-to-cw migration only because the
    golden pinned them, and `actions/generate-documentation` went on invoking
    `isee generate-documentation` for ten months after the command was removed
    (i2mint/isee#43).
    """
    import isee

    exposed = {f.__name__.replace("_", "-") for f in isee.COMMANDS}
    invoked = _subcommands_invoked_by_this_repos_actions()
    assert invoked, (
        f"no `isee <cmd>` invocations found under {ACTIONS_DIR}; the scanner "
        "has stopped scanning and this test is no longer guarding anything"
    )

    missing = {
        cmd: sorted(where) for cmd, where in invoked.items() if cmd not in exposed
    }
    assert not missing, (
        "actions/ invoke commands that `isee` does not expose: "
        + "; ".join(
            f"{cmd} (in {', '.join(where)})" for cmd, where in sorted(missing.items())
        )
    )
