"""Agent run replay and guardrail audit

Replays recorded agent sessions (tool calls, shell commands, file edits) as a readable
timeline and flags actions outside a configurable policy, such as writes outside the
repo or network calls. For teams that want an audit trail without a full runtime.
"""

__version__ = "0.1.0"
