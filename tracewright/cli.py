"""Command-line interface for replaying recorded agent run sessions."""

from __future__ import annotations

import argparse
import sys

from .guardrail import check_events
from .loader import load_session
from .policy import load_policy
from .timeline import describe_event, render_timeline


def _replay(args: argparse.Namespace) -> int:
    events = load_session(args.session_file)
    print(render_timeline(events))
    return 0


def _audit(args: argparse.Namespace) -> int:
    events = load_session(args.session_file)
    policy = load_policy(args.policy)
    violations = check_events(events, policy)

    if not violations:
        print("no violations found; session complies with policy")
        return 0

    for violation in violations:
        print(f"[{violation.rule}] {describe_event(violation.event)}: {violation.message}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-audit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    replay_parser = subparsers.add_parser(
        "replay", help="Print a recorded session as a human-readable timeline"
    )
    replay_parser.add_argument("session_file", help="Path to a JSONL session recording")
    replay_parser.set_defaults(func=_replay)

    audit_parser = subparsers.add_parser(
        "audit", help="Audit a recorded session against a guardrail policy"
    )
    audit_parser.add_argument("session_file", help="Path to a JSONL session recording")
    audit_parser.add_argument(
        "--policy", required=True, help="Path to a YAML or TOML guardrail policy file"
    )
    audit_parser.set_defaults(func=_audit)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
