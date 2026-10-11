# Agent run replay and guardrail audit

Replays recorded agent sessions (tool calls, shell commands, file edits) as a readable timeline and flags actions outside a configurable policy, such as writes outside the repo or network calls. For teams that want an audit trail without a full runtime.

## Install

```bash
pip install -e ".[dev]"
```

## Usage

Sessions are JSONL files with one event per line. Each event has a `type` of `tool_call`, `shell_command`, `file_edit`, or `network_call`, plus a timestamp and actor.

```bash
# Print a recorded session as a timeline, one line per event
agent-audit replay path/to/session.jsonl

# Mark each event that breaks a policy, inline in the timeline
agent-audit replay path/to/session.jsonl --policy path/to/policy.yaml

# Show only the events that break the policy (requires --policy)
agent-audit replay path/to/session.jsonl --policy path/to/policy.yaml --only-violations

# Audit a session against a policy; exits 1 if any violation is found
agent-audit audit path/to/session.jsonl --policy path/to/policy.yaml
```

Options:

- `--policy FILE`: a YAML (`.yaml`/`.yml`) or TOML (`.toml`) guardrail policy. Required for `audit`; optional for `replay`.
- `--only-violations`: `replay` only. Hides every event except the ones flagged by `--policy`.

## Example

TODO.

## FAQ

TODO.

## License

MIT -- see [LICENSE](LICENSE).
