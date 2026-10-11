import subprocess
import sys
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "session.jsonl"
CLEAN_POLICY = Path(__file__).parent / "fixtures" / "policy_clean.yaml"
VIOLATIONS_FIXTURE = Path(__file__).parent / "fixtures" / "session_violations.jsonl"
VIOLATIONS_POLICY = Path(__file__).parent / "fixtures" / "policy_violations.yaml"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tracewright.cli", *args],
        capture_output=True,
        text=True,
    )


def test_audit_reports_violations_and_exits_nonzero() -> None:
    result = _run("audit", str(VIOLATIONS_FIXTURE), "--policy", str(VIOLATIONS_POLICY))

    assert result.returncode == 1
    assert "write-outside-repo" in result.stdout
    assert "network-call-denied" in result.stdout


def test_audit_clean_session_exits_zero() -> None:
    result = _run("audit", str(FIXTURE), "--policy", str(CLEAN_POLICY))

    assert result.returncode == 0
    assert "no violations" in result.stdout.lower()


def test_audit_missing_policy_file_exits_nonzero_with_stderr_message() -> None:
    result = _run("audit", str(FIXTURE), "--policy", "/nonexistent/policy.yaml")

    assert result.returncode != 0
    assert "error" in result.stderr.lower()
