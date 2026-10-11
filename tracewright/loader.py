"""Load recorded agent session events from a JSONL file."""

from __future__ import annotations

import json
from os import PathLike

from .events import Event, parse_event


def load_session(path: str | PathLike[str]) -> list[Event]:
    """Read a JSONL session recording into a list of Events, in file order.

    Blank lines are skipped. Each non-blank line is parsed as a JSON object
    and dispatched to the appropriate Event subclass via `parse_event`.
    Raises ValueError if a JSON line is malformed, including the line number.
    """
    events: list[Event] = []
    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                data = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"malformed JSON on line {line_number}: {e}"
                ) from e
            try:
                events.append(parse_event(data))
            except ValueError as e:
                raise ValueError(f"invalid event on line {line_number}: {e}") from e
    return events
