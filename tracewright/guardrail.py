"""Guardrail checker: evaluate recorded events against a Policy."""

from __future__ import annotations

from dataclasses import dataclass

from .events import Event, FileEditEvent, NetworkCallEvent, ShellCommandEvent
from .policy import Policy


@dataclass(frozen=True)
class Violation:
    """A single policy violation found while auditing an agent run."""

    event: Event
    rule: str
    message: str


def _check_file_edit(event: FileEditEvent, policy: Policy) -> Violation | None:
    if any(event.path.startswith(prefix) for prefix in policy.allowed_write_prefixes):
        return None
    return Violation(
        event=event,
        rule="write-outside-repo",
        message=(
            f"write to {event.path!r} is outside allowed prefixes "
            f"{policy.allowed_write_prefixes!r}"
        ),
    )


def _check_network_call(event: NetworkCallEvent, policy: Policy) -> Violation | None:
    if policy.deny_network:
        return Violation(
            event=event,
            rule="network-call-denied",
            message=(
                f"network call to {event.host!r} is denied: "
                "network access is disabled by policy"
            ),
        )
    if event.host not in policy.allowed_network_hosts:
        return Violation(
            event=event,
            rule="network-call-denied",
            message=(
                f"network call to {event.host!r} is not in allowed hosts "
                f"{policy.allowed_network_hosts!r}"
            ),
        )
    return None


def _check_shell_command(event: ShellCommandEvent, policy: Policy) -> Violation | None:
    if any(event.command.startswith(prefix) for prefix in policy.allowed_shell_prefixes):
        return None
    return Violation(
        event=event,
        rule="shell-command-denied",
        message=(
            f"shell command {event.command!r} does not match allowed prefixes "
            f"{policy.allowed_shell_prefixes!r}"
        ),
    )


def check_events(events: list[Event], policy: Policy) -> list[Violation]:
    """Evaluate recorded events against a policy, returning any violations.

    FileEditEvent paths are checked against `allowed_write_prefixes`,
    NetworkCallEvent hosts against `deny_network`/`allowed_network_hosts`,
    and ShellCommandEvent text against `allowed_shell_prefixes`. Other
    event kinds are not evaluated.
    """
    violations: list[Violation] = []
    for event in events:
        violation: Violation | None
        if isinstance(event, FileEditEvent):
            violation = _check_file_edit(event, policy)
        elif isinstance(event, NetworkCallEvent):
            violation = _check_network_call(event, policy)
        elif isinstance(event, ShellCommandEvent):
            violation = _check_shell_command(event, policy)
        else:
            violation = None
        if violation is not None:
            violations.append(violation)
    return violations
