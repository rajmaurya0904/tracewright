"""Core event data model for recorded agent run actions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, ClassVar


@dataclass(frozen=True)
class ToolCallEvent:
    """A tool invocation performed by the agent."""

    type: ClassVar[str] = "tool_call"
    timestamp: str
    actor: str
    tool_name: str
    arguments: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, **{k: v for k, v in asdict(self).items()}}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolCallEvent:
        return cls(
            timestamp=_require(data, "timestamp"),
            actor=_require(data, "actor"),
            tool_name=_require(data, "tool_name"),
            arguments=_require(data, "arguments"),
        )


@dataclass(frozen=True)
class ShellCommandEvent:
    """A shell command executed by the agent."""

    type: ClassVar[str] = "shell_command"
    timestamp: str
    actor: str
    command: str
    cwd: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, **{k: v for k, v in asdict(self).items()}}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShellCommandEvent:
        return cls(
            timestamp=_require(data, "timestamp"),
            actor=_require(data, "actor"),
            command=_require(data, "command"),
            cwd=_require(data, "cwd"),
        )


@dataclass(frozen=True)
class FileEditEvent:
    """A file edit made by the agent."""

    type: ClassVar[str] = "file_edit"
    timestamp: str
    actor: str
    path: str
    diff: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, **{k: v for k, v in asdict(self).items()}}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FileEditEvent:
        return cls(
            timestamp=_require(data, "timestamp"),
            actor=_require(data, "actor"),
            path=_require(data, "path"),
            diff=_require(data, "diff"),
        )


@dataclass(frozen=True)
class NetworkCallEvent:
    """A network call made by the agent."""

    type: ClassVar[str] = "network_call"
    timestamp: str
    actor: str
    host: str
    method: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, **{k: v for k, v in asdict(self).items()}}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NetworkCallEvent:
        return cls(
            timestamp=_require(data, "timestamp"),
            actor=_require(data, "actor"),
            host=_require(data, "host"),
            method=_require(data, "method"),
        )


Event = ToolCallEvent | ShellCommandEvent | FileEditEvent | NetworkCallEvent

_EVENT_TYPES: dict[str, type[Event]] = {
    ToolCallEvent.type: ToolCallEvent,
    ShellCommandEvent.type: ShellCommandEvent,
    FileEditEvent.type: FileEditEvent,
    NetworkCallEvent.type: NetworkCallEvent,
}


def _require(data: dict[str, Any], field: str) -> Any:
    try:
        return data[field]
    except KeyError:
        raise ValueError(f"missing required field {field!r}") from None


def parse_event(data: dict[str, Any]) -> Event:
    """Dispatch a raw dict to the appropriate Event subclass based on its `type` field."""
    event_type = _require(data, "type")
    try:
        event_cls = _EVENT_TYPES[event_type]
    except KeyError:
        raise ValueError(f"unknown event type {event_type!r}") from None
    return event_cls.from_dict(data)
