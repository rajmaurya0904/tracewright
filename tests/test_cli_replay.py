import subprocess
import sys
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "session.jsonl"


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
