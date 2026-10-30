# Telemetry Machine

[Telemetry Machine](https://telemetrymachine.com) stores a team's OpenTelemetry traces,
logs and metrics, and arbitrary wide events. This plugin lets Claude set up, query and
investigate it. It connects Claude to Telemetry Machine's MCP server and adds three
skills.

| Skill | Use |
|---|---|
| `tm-instrument` | Loads when Claude adds or changes OpenTelemetry instrumentation; gives it Telemetry Machine's OpenTelemetry guide and has it look up names with `get_semconv`. |
| `tm-investigate` | Loads when Claude investigates or root-causes an issue; walks it through datasets, SLOs, annotations, `run_surface` and `run_query`. |
| `tm-cli` | Loads when Claude uses tm-cli, the Telemetry Machine CLI; its commands, column names and query pitfalls. |

## Get started

1. Install the plugin. In Claude Code (2.1.292 or later), run:

   ```text
   /plugin install telemetry-machine --marketplace telemetry-machine/agent-skills
   ```

2. In Claude Code, run `/mcp`, choose `plugin:telemetry-machine:telemetry-machine` and
   sign in in your browser.
3. To send your first data, run
   `/mcp__plugin_telemetry-machine_telemetry-machine__onboarding` in Claude Code, or ask
   Claude to call `get_onboarding_guide`.

After that, ask for what you need. When Claude adds instrumentation or investigates an
issue, the skills load and send it to Telemetry Machine.

## What the plugin connects to

- **Telemetry Machine's MCP server** at `https://telemetrymachine.com/api/mcp`. You sign
  in with OAuth. Claude sends it your queries and the changes you ask for, such as new
  datasets, dashboards, SLOs and API keys, and reads your telemetry back from it.
- **Telemetry Machine's ingest API** at `https://api.telemetrymachine.com`. When you ask
  Claude to send a system's data, the `tm-instrument` skill has it point that system's
  OpenTelemetry exporter there, with an ingest key.
- **tm-cli**, only when Claude uses it. The `tm-cli` skill has Claude download tm-cli
  from `https://telemetrymachine.com/downloads/tm-cli/`, check its SHA-256 and install
  it in a directory such as `~/.local/bin`. tm-cli talks to Telemetry Machine and keeps
  its sign-in in the system keychain, or in private files when there is none.
- **Documentation.** The skills link to Telemetry Machine's docs and to
  opentelemetry.io, which Claude may read.

The plugin has no hooks and runs no code of its own.

## Privacy and license

Read Telemetry Machine's [privacy policy](https://telemetrymachine.com/privacy). The
plugin is MIT licensed.
