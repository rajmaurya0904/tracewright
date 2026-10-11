import pytest

from tracewright.events import (
    FileEditEvent,
    NetworkCallEvent,
    ShellCommandEvent,
    ToolCallEvent,
    parse_event,
)

SAMPLES = [
    (
        {
            "type": "tool_call",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "tool_name": "Read",
            "arguments": {"path": "foo.py"},
        },
        ToolCallEvent,
    ),
    (
        {
            "type": "shell_command",
            "timestamp": "2026-01-01T00:00:01Z",
            "actor": "agent-1",
            "command": "ls -la",
            "cwd": "/tmp",
        },
        ShellCommandEvent,
    ),
    (
        {
            "type": "file_edit",
            "timestamp": "2026-01-01T00:00:02Z",
            "actor": "agent-1",
            "path": "foo.py",
            "diff": "-old\n+new",
        },
        FileEditEvent,
    ),
    (
        {
            "type": "network_call",
            "timestamp": "2026-01-01T00:00:03Z",
            "actor": "agent-1",
            "host": "api.example.com",
            "method": "GET",
        },
        NetworkCallEvent,
    ),
]


@pytest.mark.parametrize("data,expected_cls", SAMPLES)
def test_parse_event_dispatches_to_expected_class(data, expected_cls) -> None:
    """Valid dict for each event kind parses to the right class."""
    event = parse_event(data)
    assert isinstance(event, expected_cls)


@pytest.mark.parametrize("data,_expected_cls", SAMPLES)
def test_round_trip_to_dict(data, _expected_cls) -> None:
    """Round-trip test: to_dict after parse_event reproduces the input."""
    assert parse_event(data).to_dict() == data


def test_tool_call_event_round_trip() -> None:
    data = {
        "type": "tool_call",
        "timestamp": "2026-01-01T12:34:56Z",
        "actor": "agent-test",
        "tool_name": "Bash",
        "arguments": {"command": "ls", "timeout": 30},
    }
    event = parse_event(data)
    assert isinstance(event, ToolCallEvent)
    assert event.to_dict() == data


def test_shell_command_event_round_trip() -> None:
    data = {
        "type": "shell_command",
        "timestamp": "2026-01-01T12:34:57Z",
        "actor": "agent-test",
        "command": "cd /tmp && echo test",
        "cwd": "/home/user",
    }
    event = parse_event(data)
    assert isinstance(event, ShellCommandEvent)
    assert event.to_dict() == data


def test_file_edit_event_round_trip() -> None:
    data = {
        "type": "file_edit",
        "timestamp": "2026-01-01T12:34:58Z",
        "actor": "agent-test",
        "path": "/src/main.py",
        "diff": "--- a/main.py\n+++ b/main.py\n@@ -1 +1 @@\n-old\n+new",
    }
    event = parse_event(data)
    assert isinstance(event, FileEditEvent)
    assert event.to_dict() == data


def test_network_call_event_round_trip() -> None:
    data = {
        "type": "network_call",
        "timestamp": "2026-01-01T12:34:59Z",
        "actor": "agent-test",
        "host": "api.github.com",
        "method": "POST",
    }
    event = parse_event(data)
    assert isinstance(event, NetworkCallEvent)
    assert event.to_dict() == data


def test_unknown_type_raises_value_error() -> None:
    """Unknown `type` raises a clear `ValueError`."""
    with pytest.raises(ValueError, match="unknown event type 'bogus'"):
        parse_event({"type": "bogus"})


def test_unknown_type_with_other_fields() -> None:
    with pytest.raises(ValueError, match="unknown event type 'invalid'"):
        parse_event({
            "type": "invalid",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
        })


def test_missing_type_raises_value_error() -> None:
    """Missing 'type' field raises a clear error."""
    with pytest.raises(ValueError, match="missing required field 'type'"):
        parse_event({"actor": "agent-1"})


def test_missing_field_raises_value_error() -> None:
    """Missing required fields raise a clear error."""
    with pytest.raises(ValueError, match="missing required field"):
        parse_event({"type": "shell_command", "timestamp": "t", "actor": "a"})


def test_tool_call_missing_timestamp() -> None:
    with pytest.raises(ValueError, match="missing required field 'timestamp'"):
        parse_event({
            "type": "tool_call",
            "actor": "agent-1",
            "tool_name": "Read",
            "arguments": {},
        })


def test_tool_call_missing_actor() -> None:
    with pytest.raises(ValueError, match="missing required field 'actor'"):
        parse_event({
            "type": "tool_call",
            "timestamp": "2026-01-01T00:00:00Z",
            "tool_name": "Read",
            "arguments": {},
        })


def test_tool_call_missing_tool_name() -> None:
    with pytest.raises(ValueError, match="missing required field 'tool_name'"):
        parse_event({
            "type": "tool_call",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "arguments": {},
        })


def test_tool_call_missing_arguments() -> None:
    with pytest.raises(ValueError, match="missing required field 'arguments'"):
        parse_event({
            "type": "tool_call",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "tool_name": "Read",
        })


def test_shell_command_missing_command() -> None:
    with pytest.raises(ValueError, match="missing required field 'command'"):
        parse_event({
            "type": "shell_command",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "cwd": "/tmp",
        })


def test_shell_command_missing_cwd() -> None:
    with pytest.raises(ValueError, match="missing required field 'cwd'"):
        parse_event({
            "type": "shell_command",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "command": "ls",
        })


def test_file_edit_missing_path() -> None:
    with pytest.raises(ValueError, match="missing required field 'path'"):
        parse_event({
            "type": "file_edit",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "diff": "-old\n+new",
        })


def test_file_edit_missing_diff() -> None:
    with pytest.raises(ValueError, match="missing required field 'diff'"):
        parse_event({
            "type": "file_edit",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "path": "foo.py",
        })


def test_network_call_missing_host() -> None:
    with pytest.raises(ValueError, match="missing required field 'host'"):
        parse_event({
            "type": "network_call",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "method": "GET",
        })


def test_network_call_missing_method() -> None:
    with pytest.raises(ValueError, match="missing required field 'method'"):
        parse_event({
            "type": "network_call",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "host": "api.example.com",
        })


def test_tool_call_with_empty_arguments() -> None:
    """Tool call with empty arguments dict should parse successfully."""
    data = {
        "type": "tool_call",
        "timestamp": "2026-01-01T00:00:00Z",
        "actor": "agent-1",
        "tool_name": "Read",
        "arguments": {},
    }
    event = parse_event(data)
    assert isinstance(event, ToolCallEvent)
    assert event.arguments == {}
    assert event.to_dict() == data


def test_tool_call_with_nested_arguments() -> None:
    """Tool call with nested argument structures should parse successfully."""
    data = {
        "type": "tool_call",
        "timestamp": "2026-01-01T00:00:00Z",
        "actor": "agent-1",
        "tool_name": "Edit",
        "arguments": {
            "file_path": "src/main.py",
            "old_string": "def foo():",
            "new_string": "def bar():",
            "nested": {"key": "value", "num": 42},
        },
    }
    event = parse_event(data)
    assert isinstance(event, ToolCallEvent)
    assert event.to_dict() == data


@pytest.mark.parametrize("bad_input", [["tool_call"], "tool_call", 5, None])
def test_parse_event_rejects_non_object_input(bad_input) -> None:
    with pytest.raises(ValueError, match="event must be a JSON object"):
        parse_event(bad_input)


def test_parse_event_rejects_non_string_type() -> None:
    with pytest.raises(ValueError, match="event type must be a string, got list"):
        parse_event({"type": ["tool_call"], "timestamp": "t", "actor": "a"})
