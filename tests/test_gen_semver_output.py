"""gen_semver output modes: the 'github' mode writes step outputs instead of printing (#28)."""

import pytest

import isee.generation_utils as gu


@pytest.fixture(autouse=True)
def _fixed_version(monkeypatch):
    monkeypatch.setattr(gu, "get_new_version", lambda **kw: "1.2.3")


def test_github_mode_writes_output_and_env_files_and_returns(
    tmp_path, monkeypatch, capsys
):
    out, env = tmp_path / "out", tmp_path / "env"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setenv("GITHUB_ENV", str(env))
    assert gu.gen_semver(dir_path=str(tmp_path), output_mode="github") == "1.2.3"
    assert out.read_text() == "version=1.2.3\n" and env.read_text() == "VERSION=1.2.3\n"
    assert capsys.readouterr().out == ""


def test_github_mode_outside_actions_says_so(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    monkeypatch.delenv("GITHUB_ENV", raising=False)
    with pytest.raises(RuntimeError, match="GITHUB_OUTPUT"):
        gu.gen_semver(dir_path=str(tmp_path), output_mode="github")


def test_print_and_return_modes_unchanged(tmp_path, capsys):
    assert gu.gen_semver(dir_path=str(tmp_path), output_mode="print") is None
    assert capsys.readouterr().out == "1.2.3\n"
    assert gu.gen_semver(dir_path=str(tmp_path), output_mode="return") == "1.2.3"
