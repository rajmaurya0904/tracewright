import subprocess
import sys
from pathlib import Path

from tracewright.guardrail import check_events
from tracewright.loader import load_session
from tracewright.policy import load_policy

FIXTURE = Path(__file__).parent / "fixtures" / "session.jsonl"
VIOLATIONS_FIXTURE = Path(__file__).parent / "fixtures" / "session_violations.jsonl"
VIOLATIONS_POLICY = Path(__file__).parent / "fixtures" / "policy_violations.yaml"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tracewright.cli", *args],
        capture_output=True,
        text=True,
    )


def test_replay_prints_one_line_per_event() -> None:
    result = _run("replay", str(FIXTURE))

    assert result.returncode == 0
    lines = result.stdout.splitlines()
    assert len(lines) == 3
    assert "TOOL" in lines[0]
    assert "SHELL" in lines[1]
    assert "NET" in lines[2]


def test_replay_missing_file_exits_nonzero_with_stderr_message() -> None:
    result = _run("replay", "/nonexistent/path/session.jsonl")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "error" in result.stderr.lower()


def test_replay_only_violations_prints_one_line_per_violation() -> None:
    violations = check_events(
        load_session(VIOLATIONS_FIXTURE), load_policy(VIOLATIONS_POLICY)
    )

    result = _run(
        "replay",
        str(VIOLATIONS_FIXTURE),
        "--policy",
        str(VIOLATIONS_POLICY),
        "--only-violations",
    )

    assert result.returncode == 0
    lines = result.stdout.splitlines()
    assert len(lines) == len(violations) == 2
    for line in lines:
        assert any(f"[VIOLATION: {v.rule}]" in line for v in violations)
    assert "TOOL" not in result.stdout
