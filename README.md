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

The repo ships a sample session and policy in `examples/`. Run these from the repository root.

`examples/policy.yaml` allows writes under `.`, denies all network calls, and only allows shell commands starting with `git`, `pytest`, or `ruff`:

```yaml
allowed_write_prefixes:
  - .
deny_network: true
allowed_network_hosts: []
allowed_shell_prefixes:
  - git
  - pytest
  - ruff
```

Replay the session as a timeline:

```bash
agent-audit replay examples/session.jsonl
```

```text
2026-01-01T00:00:00Z TOOL Read
2026-01-01T00:00:01Z SHELL pytest -q
2026-01-01T00:00:02Z WRITE ./tracewright/cli.py
2026-01-01T00:00:03Z SHELL rm -rf build
2026-01-01T00:00:04Z WRITE /etc/hosts
2026-01-01T00:00:05Z NET GET api.example.com
```

Show only the events that break the policy:

```bash
agent-audit replay examples/session.jsonl --policy examples/policy.yaml --only-violations
```

```text
[VIOLATION: shell-command-denied] 2026-01-01T00:00:03Z SHELL rm -rf build
[VIOLATION: write-outside-repo] 2026-01-01T00:00:04Z WRITE /etc/hosts
[VIOLATION: network-call-denied] 2026-01-01T00:00:05Z NET GET api.example.com
```

Audit the session. Each violation is listed with its rule, and the command exits 1:

```bash
agent-audit audit examples/session.jsonl --policy examples/policy.yaml
echo $?   # 1
```

```text
[shell-command-denied] SHELL rm -rf build: shell command 'rm -rf build' does not match allowed prefixes ['git', 'pytest', 'ruff']
[write-outside-repo] WRITE /etc/hosts: write to '/etc/hosts' is outside allowed prefixes ['.']
[network-call-denied] NET GET api.example.com: network call to 'api.example.com' is denied: network access is disabled by policy
```

Run `audit` against a clean session and the command exits 0 with `no violations found; session complies with policy`.

## FAQ

TODO.

## License

MIT -- see [LICENSE](LICENSE).
