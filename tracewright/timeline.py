"""Human-readable timeline rendering for recorded agent run events."""

from __future__ import annotations

from .events import (
    Event,
    FileEditEvent,
    NetworkCallEvent,
    ShellCommandEvent,
    ToolCallEvent,
)

_KIND_LABELS: dict[str, str] = {
    ToolCallEvent.type: "TOOL",
    ShellCommandEvent.type: "SHELL",
    FileEditEvent.type: "WRITE",
    NetworkCallEvent.type: "NET",
}


def _summarize(event: Event) -> str:
    """Return a short, kind-specific summary of an event."""
    if isinstance(event, ToolCallEvent):
        return event.tool_name
    if isinstance(event, ShellCommandEvent):
        return event.command
    if isinstance(event, FileEditEvent):
        return event.path
    if isinstance(event, NetworkCallEvent):
        return f"{event.method} {event.host}"
    raise TypeError(f"unsupported event type: {type(event).__name__}")


def describe_event(event: Event) -> str:
    """Return a short, kind-specific description of an event, e.g. `WRITE foo.py`."""
    return f"{_KIND_LABELS[event.type]} {_summarize(event)}"


def render_timeline(events: list[Event]) -> str:
    """Format events chronologically as a human-readable timeline.

    Events are sorted by timestamp. Each line shows the event's timestamp,
    kind, and a short kind-specific summary, e.g.
    `2026-01-01T00:00:00Z WRITE foo.py`.
    """
    sorted_events = sorted(events, key=lambda e: e.timestamp)
    lines = [f"{event.timestamp} {describe_event(event)}" for event in sorted_events]
    return "\n".join(lines)
