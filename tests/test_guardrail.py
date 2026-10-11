from tracewright.events import (
    FileEditEvent,
    NetworkCallEvent,
    ShellCommandEvent,
)
from tracewright.guardrail import check_events
from tracewright.policy import Policy


def test_write_outside_repo_is_flagged() -> None:
    policy = Policy(allowed_write_prefixes=["./"])
    events = [
        FileEditEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            path="/etc/passwd",
            diff="-old\n+new",
        ),
    ]

    violations = check_events(events, policy)

    assert len(violations) == 1
    assert violations[0].rule == "write-outside-repo"
    assert violations[0].event.path == "/etc/passwd"


def test_write_inside_repo_is_not_flagged() -> None:
    policy = Policy(allowed_write_prefixes=["./"])
    events = [
        FileEditEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            path="./src/main.py",
            diff="-old\n+new",
        ),
    ]

    assert check_events(events, policy) == []


def test_network_call_to_disallowed_host_is_flagged() -> None:
    policy = Policy(deny_network=False, allowed_network_hosts=["api.example.com"])
    events = [
        NetworkCallEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            host="evil.example.com",
            method="GET",
        ),
    ]

    violations = check_events(events, policy)

    assert len(violations) == 1
    assert violations[0].rule == "network-call-denied"
    assert violations[0].event.host == "evil.example.com"


def test_network_call_to_allowlisted_host_is_not_flagged() -> None:
    policy = Policy(deny_network=False, allowed_network_hosts=["api.example.com"])
    events = [
        NetworkCallEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            host="api.example.com",
            method="GET",
        ),
    ]

    assert check_events(events, policy) == []


def test_denied_shell_command_pattern_is_flagged() -> None:
    policy = Policy(allowed_shell_prefixes=["git", "pytest"])
    events = [
        ShellCommandEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            command="rm -rf /",
            cwd="/repo",
        ),
    ]

    violations = check_events(events, policy)

    assert len(violations) == 1
    assert violations[0].rule == "shell-command-denied"
    assert violations[0].event.command == "rm -rf /"


def test_clean_session_produces_zero_violations() -> None:
    policy = Policy(
        allowed_write_prefixes=["./"],
        deny_network=False,
        allowed_network_hosts=["api.example.com"],
        allowed_shell_prefixes=["git", "pytest"],
    )
    events = [
        FileEditEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            path="./src/main.py",
            diff="-old\n+new",
        ),
        ShellCommandEvent(
            timestamp="2026-01-01T00:00:01Z",
            actor="agent-1",
            command="git status",
            cwd="/repo",
        ),
        NetworkCallEvent(
            timestamp="2026-01-01T00:00:02Z",
            actor="agent-1",
            host="api.example.com",
            method="GET",
        ),
    ]

    assert check_events(events, policy) == []
