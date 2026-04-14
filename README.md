# ReasonCavalier

ReasonCavalier is an agentic plugin framework for Cursor, Claude Code, Codex, and similar AI coding tools.

This repository provides:

- A cross-tool plugin skeleton
- Reusable skills, commands, and hooks layout
- A baseline structure for multi-agent development workflows

## Repository

- GitHub: https://github.com/liushoukun/reason-cavalier

## Initial Structure

- `.cursor-plugin/` Cursor plugin entry metadata
- `.cursor/rules/` persistent Cursor rules (`.mdc`)
- `.claude-plugin/` Claude plugin installation notes
- `.codex/` Codex installation instructions
- `agents/` agent prompts and role definitions
- `commands/` reusable command templates
- `hooks/` automation hook configuration
- `skills/` composable skills

## Next Steps

1. Define a first set of mandatory skills (plan, debug, tdd, review).
2. Add tool-specific install adapters under each plugin folder.
3. Add validation tests for skill triggers and prompt outputs.
