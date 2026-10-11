from pathlib import Path

from tracewright.events import (
    NetworkCallEvent,
    ShellCommandEvent,
    ToolCallEvent,
)
from tracewright.loader import load_session

FIXTURE = Path(__file__).parent / "fixtures" / "session.jsonl"


def test_load_session_returns_events_in_file_order() -> None:
    events = load_session(FIXTURE)

    assert len(events) == 3
    assert isinstance(events[0], ToolCallEvent)
    assert isinstance(events[1], ShellCommandEvent)
    assert isinstance(events[2], NetworkCallEvent)
    assert events[0].tool_name == "Read"
    assert events[1].command == "ls -la"
    assert events[2].host == "api.example.com"


def test_load_session_skips_blank_lines(tmp_path: Path) -> None:
    session_file = tmp_path / "session.jsonl"
    session_file.write_text(
        '{"type": "network_call", "timestamp": "t", "actor": "a", '
        '"host": "h", "method": "GET"}\n'
        "\n"
        "   \n"
        '{"type": "network_call", "timestamp": "t2", "actor": "a", '
        '"host": "h2", "method": "POST"}\n'
    )

    events = load_session(session_file)

    assert len(events) == 2
    assert events[0].timestamp == "t"
    assert events[1].timestamp == "t2"


def test_load_session_empty_file(tmp_path: Path) -> None:
    session_file = tmp_path / "session.jsonl"
    session_file.write_text("")

    events = load_session(session_file)

    assert events == []


def test_load_session_malformed_json_raises_with_line_number(
    tmp_path: Path,
) -> None:
    session_file = tmp_path / "session.jsonl"
    session_file.write_text(
        '{"type": "network_call", "timestamp": "t", "actor": "a", '
        '"host": "h", "method": "GET"}\n'
        '{"malformed": json}\n'
        '{"type": "network_call", "timestamp": "t2", "actor": "a", '
        '"host": "h2", "method": "POST"}\n'
    )

    import pytest

    with pytest.raises(ValueError, match=r"malformed JSON on line 2"):
        load_session(session_file)


def test_load_session_missing_file_raises_file_not_found_error() -> None:
    import pytest

    with pytest.raises(FileNotFoundError):
        load_session("/nonexistent/path/session.jsonl")
