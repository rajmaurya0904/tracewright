"""Guardrail checker: evaluate recorded events against a Policy."""

from __future__ import annotations

import ntpath
import posixpath
from dataclasses import dataclass

from .events import Event, FileEditEvent, NetworkCallEvent, ShellCommandEvent
from .policy import Policy

#: Prefixes that mean "the repository root", i.e. anything inside the repo.
_REPO_ROOT = ""


@dataclass(frozen=True)
class Violation:
    """A single policy violation found while auditing an agent run."""

    event: Event
    rule: str
    message: str


def _normalise_path(path: str) -> str:
    """Collapse a recorded path to a comparable POSIX form.

    Backslashes become forward slashes, `.`/`..` segments are collapsed, and
    a leading `./` is dropped, so `.`, `./` and `` all normalise to the repo
    root (the empty string). Absolute paths keep their leading `/` and paths
    that climb out of the repo keep their leading `../`.
    """
    normalised = posixpath.normpath(path.replace("\\", "/"))
    if normalised == ".":
        return _REPO_ROOT
    return normalised


def _is_inside_repo(path: str) -> bool:
    """True if a normalised path stays inside the repository root.

    Absolute paths in either POSIX (`/etc/hosts`) or Windows (`C:/Windows`)
    form are outside, as is anything reached by climbing out with `..`.
    """
    if posixpath.isabs(path) or ntpath.isabs(path):
        return False
    return path != ".." and not path.startswith("../")


def _write_is_allowed(path: str, prefixes: list[str]) -> bool:
    """True if `path` sits under one of `prefixes`, compared path-wise.

    A prefix of `.` (or `./`) means the repo root and therefore matches any
    path inside the repo, so `src/app.py` is allowed while `/etc/hosts` and
    `../outside.txt` are not. Other prefixes match on whole path segments,
    so `src` matches `src/app.py` but not `srcfoo.py`.
    """
    target = _normalise_path(path)
    for prefix in prefixes:
        normalised_prefix = _normalise_path(prefix)
        if normalised_prefix == _REPO_ROOT:
            if _is_inside_repo(target):
                return True
        elif target == normalised_prefix or target.startswith(normalised_prefix + "/"):
            return True
    return False


def _check_file_edit(event: FileEditEvent, policy: Policy) -> Violation | None:
    if _write_is_allowed(event.path, policy.allowed_write_prefixes):
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
