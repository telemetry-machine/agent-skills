# Telemetry Machine Agent Skill — Development Guide

## Repository Structure

This repo contains a single Claude Code plugin at `telemetry-machine/`. The root
also has a marketplace manifest at `.claude-plugin/marketplace.json` and build
scripts with their tests under `scripts/`.

```text
telemetry-machine/            # Plugin root
  README.md                   # Listing text in Anthropic's plugin directory
  .claude-plugin/plugin.json  # Claude Code plugin manifest
  .claude-plugin/icon.png     # Listing icon in Anthropic's plugin directory
  .codex-plugin/              # Codex plugin manifest
  .cursor-plugin/             # Cursor plugin manifest
  .mcp.json                   # MCP server for Codex; Claude Code and Cursor also declare it in their manifests
  skills/                     # One directory per skill: SKILL.md + references/ + scripts/
scripts/
  build_skills_index.py       # skills/index.json, for agents that download skills; CI checks it
server.json                   # MCP Registry entry for the MCP server (README: MCP Registry)
```

## Key Conventions

- All versions (plugin.json, marketplace.json, skill metadata) must stay in sync
- `server.json` has its own version, the MCP Registry entry's; releases don't change it

## Adding a New Skill

1. Create `telemetry-machine/skills/<skill-name>/SKILL.md` with frontmatter:

   ```yaml
   name: <skill-name>
   description: <when to use this skill>
   ```

2. Add reference files in `telemetry-machine/skills/<skill-name>/references/`
3. Run `python3 scripts/build_skills_index.py` to update `telemetry-machine/skills/index.json`

## Observability

Every service must be instrumented using OTel traces, logs, and metrics in Telemetry Machine.
