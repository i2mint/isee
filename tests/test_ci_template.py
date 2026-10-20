"""The modern CI template must not hardcode the user's branch name (issue 31)."""

from pathlib import Path

import yaml

TEMPLATE = Path(__file__).resolve().parents[1] / "resources" / "ci-modern.yml"
GATE = "format('refs/heads/{0}', github.event.repository.default_branch)"


def _jobs():
    return yaml.safe_load(TEMPLATE.read_text())["jobs"]


def test_publishing_jobs_gate_on_the_default_branch_not_a_name():
    jobs = _jobs()
    gated = {
        name: job["if"]
        for name, job in jobs.items()
        if "refs/heads" in str(job.get("if", ""))
    }
    assert gated, "expected the publish jobs to be gated on a branch"
    for name, condition in gated.items():
        assert GATE in condition, f"{name} must gate on the default branch"
        assert (
            "'refs/heads/master'" not in condition
            and "'refs/heads/main'" not in condition
        )
