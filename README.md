# tracewright

**Replays a recorded agent session as a readable timeline and flags the actions that broke your policy — for teams who want an audit trail without wiring up a sandbox.**

An agent ran for forty minutes and left you a JSONL log. Somewhere in those
hundreds of lines it shelled out to something you would never have approved,
wrote to a path outside the repo, and phoned home. Reading the raw log to find
out which is miserable. `tracewright` turns the log into six readable lines and
tells you exactly which three were the problem.

## Real terminal output

```console
$ tracewright replay examples/session.jsonl
2026-01-01T00:00:00Z TOOL Read
2026-01-01T00:00:01Z SHELL pytest -q
2026-01-01T00:00:02Z WRITE ./tracewright/cli.py
2026-01-01T00:00:03Z SHELL rm -rf build
2026-01-01T00:00:04Z WRITE /etc/hosts
2026-01-01T00:00:05Z NET GET api.example.com

$ tracewright audit examples/session.jsonl --policy examples/policy.yaml
[shell-command-denied] SHELL rm -rf build: shell command 'rm -rf build' does not match allowed prefixes ['git', 'pytest', 'ruff']
[write-outside-repo] WRITE /etc/hosts: write to '/etc/hosts' is outside allowed prefixes ['.']
[network-call-denied] NET GET api.example.com: network call to 'api.example.com' is denied: network access is disabled by policy

$ echo $?
1
```

That is the shipped example in `examples/`, run from the repository root. The
policy there allows writes anywhere inside the repo, denies all outbound
network calls, and permits only `git`, `pytest` and `ruff`:

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

## Install

Not on PyPI, so install it from a clone:

```bash
pip install -e .
```

## Usage

A session is a JSONL file, one event per line, each with a `type` of
`tool_call`, `shell_command`, `file_edit` or `network_call` plus a timestamp
and an actor.

```bash
# Read the session as a timeline, one line per event
tracewright replay examples/session.jsonl

# Same timeline, with policy breaches marked inline
tracewright replay examples/session.jsonl --policy examples/policy.yaml

# Just the breaches, nothing else
tracewright replay examples/session.jsonl --policy examples/policy.yaml --only-violations

# Gate a build: prints each violation with its rule, exits 1 if there are any
tracewright audit examples/session.jsonl --policy examples/policy.yaml
```

## How it works

| Event type | Checked against | Rule on failure |
| --- | --- | --- |
| `file_edit` | `allowed_write_prefixes` | `write-outside-repo` |
| `shell_command` | `allowed_shell_prefixes` | `shell-command-denied` |
| `network_call` | `deny_network`, `allowed_network_hosts` | `network-call-denied` |
| `tool_call` | nothing — shown in the timeline only | — |

- The policy is a YAML (`.yaml`/`.yml`) or TOML (`.toml`) file with those four
  optional keys. Defaults are default-deny: empty allowlists permit nothing,
  and `deny_network` is `true`.
- Write prefixes are compared path-wise after normalising the recorded path.
  `.` and `./` both mean the repository root, so `src/app.py` is allowed while
  `/etc/hosts` and `../outside.txt` are flagged. A prefix naming a
  subdirectory matches whole segments, so `src` matches `src/app.py` but not
  `srcfoo.py`.
- Shell prefixes are plain string matching, so `git` also matches `gitk`.
- An unknown event `type`, a missing field, or a line that is not a JSON
  object stops the load and reports the line number. Unknown policy keys,
  wrong value types and empty policy files are errors too.

## Limitations

- `audit` exits 1 when it finds violations, and also exits 1 on a missing file
  or a malformed session or policy. The difference is that real errors print an
  `error:` message on stderr, so in CI treat any stderr output as a failure
  rather than a finding. Bad arguments exit 2. `replay` always exits 0, even
  when `--policy` marks violations — use `audit` to gate a build.
- Nothing is enforced at runtime. This reads a log after the fact; it cannot
  stop an agent mid-run.
- It does not produce the log. You have to record the session into the JSONL
  shape yourself.
- `tool_call` events are never policy-checked, so a tool that writes files or
  opens sockets slips past unless it is also recorded as a `file_edit` or
  `network_call`.
- Shell checking is prefix matching on the recorded command string, not shell
  parsing. `git status; rm -rf /` passes a `git` allowlist.

## Development

```bash
pip install -e ".[dev]"
pytest -q
ruff check .
```

## License

MIT -- see [LICENSE](LICENSE).
