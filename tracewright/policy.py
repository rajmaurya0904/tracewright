"""Guardrail policy schema and loader.

A Policy describes what an agent run is allowed to do: which path prefixes
it may write to, whether network access is permitted at all (and to which
hosts if so), and which shell command prefixes are allowed to run.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Any

import yaml

_ALLOWED_KEYS = {
    "allowed_write_prefixes",
    "deny_network",
    "allowed_network_hosts",
    "allowed_shell_prefixes",
}


@dataclass(frozen=True)
class Policy:
    """Guardrail policy for auditing a recorded agent session.

    Defaults are default-deny: an empty allowlist permits nothing of that
    kind, and network access is denied unless explicitly allowed.
    """

    allowed_write_prefixes: list[str] = field(default_factory=list)
    deny_network: bool = True
    allowed_network_hosts: list[str] = field(default_factory=list)
    allowed_shell_prefixes: list[str] = field(default_factory=list)


def _parse_str_list(data: dict[str, Any], key: str) -> list[str]:
    if key not in data:
        return []
    value = data[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"policy key {key!r} must be a list of strings")
    return list(value)


def load_policy(path: str | PathLike[str]) -> Policy:
    """Read a YAML or TOML policy file into a Policy.

    Raises ValueError if the file contains an unknown top-level key, a
    value of the wrong type, or does not have a `.yaml`/`.yml`/`.toml`
    extension.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    # Guard against completely empty policy files – they provide no guidance.
    if not text.strip():
        raise ValueError("policy file is empty")

    if suffix in (".yaml", ".yml"):
        data = yaml.safe_load(text)
        if data is None:
            raise ValueError("policy file is empty")
    elif suffix == ".toml":
        data = tomllib.loads(text)
    else:
        raise ValueError(f"unsupported policy file extension: {suffix!r}")

    if not isinstance(data, dict):
        raise ValueError("policy file must contain a top-level mapping")

    unknown_keys = set(data) - _ALLOWED_KEYS
    if unknown_keys:
        raise ValueError(f"unknown policy key(s): {', '.join(sorted(unknown_keys))}")

    deny_network = data.get("deny_network", True)
    if not isinstance(deny_network, bool):
        raise ValueError("policy key 'deny_network' must be a boolean")

    return Policy(
        allowed_write_prefixes=_parse_str_list(data, "allowed_write_prefixes"),
        deny_network=deny_network,
        allowed_network_hosts=_parse_str_list(data, "allowed_network_hosts"),
        allowed_shell_prefixes=_parse_str_list(data, "allowed_shell_prefixes"),
    )
