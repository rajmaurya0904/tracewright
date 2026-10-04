# Changelog

All notable changes to this project will be documented in this file.

## 0.1.0
- Introduced event model for recording agent sessions.
- Added session replay functionality to visualize recorded events.
- Implemented policy-based guardrail audit to flag disallowed actions such as writes outside allowed prefixes, network calls, and shell commands.
- Provided a CLI (`agent-audit`) for running audits and replays.
- Added comprehensive tests for policy loading, guardrail checks, and replay logic.
- Updated documentation and examples.

