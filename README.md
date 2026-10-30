# Telemetry Machine: OpenTelemetry-native observability for engineers and agents

[Telemetry Machine](https://telemetrymachine.com) stores a team's OpenTelemetry traces,
logs and metrics, and arbitrary wide events, and answers any question about them. This
repo is its plugin for coding agents. The plugin connects the agent to Telemetry
Machine's MCP server (`https://telemetrymachine.com/api/mcp`) and adds three skills,
so the agent can instrument your code, send its telemetry to Telemetry Machine, query
it and root-cause issues. Agents sign in with OAuth in the browser; there is no key to
copy.

## Install

### Claude Code

In Claude Code (2.1.292 or later), run:

```text
/plugin install telemetry-machine --marketplace telemetry-machine/agent-skills
```

Or, from a terminal:

```bash
claude plugin install telemetry-machine --marketplace telemetry-machine/agent-skills
```

Then start Claude Code in your application's folder, run `/mcp`, choose
`telemetry-machine` and sign in. To send your first data, run
`/mcp__telemetry-machine__onboarding`.

After that, ask for what you need. When the agent adds OpenTelemetry instrumentation
or investigates an issue, the `tm-instrument` and `tm-investigate` skills load and send
it to Telemetry Machine.

### Other agents

Add `https://telemetrymachine.com/api/mcp` as a remote (Streamable HTTP) MCP server and
sign in when the agent asks. To onboard, ask the agent to call `get_onboarding_guide`
and follow it. To onboard another system once you're sending data, ask it to call
`get_instrumentation_guide`. Telemetry Machine's onboarding page shows the exact steps
for Codex, Cursor and others. The skills are also at
`https://telemetrymachine.com/docs/skills/index.json`.

## Skills

| Skill | Use |
|---|---|
| `tm-instrument` | Loads when the agent adds or changes OpenTelemetry instrumentation; gives it TM's OpenTelemetry doc and has it look up names with `get_semconv`. |
| `tm-investigate` | Loads when the agent investigates or root-causes an issue; walks it through datasets, SLOs (`get_slos`), annotations (`get_annotations`), `run_surface` and `run_query`. |
| `tm-cli` | Loads when the agent uses tm-cli; its commands, column names and query pitfalls. |

The skills are short on purpose. Agents already know OpenTelemetry and SQL; the skills
hold only what they can't know about Telemetry Machine. The MCP server's tools,
errors and onboarding guide carry the rest.

## Links

- [Telemetry Machine](https://telemetrymachine.com)
- [Documentation](https://telemetrymachine.com/docs), and its
  [index for agents](https://telemetrymachine.com/docs/llms.txt)
- MCP server: `https://telemetrymachine.com/api/mcp`, listed in the
  [MCP Registry](https://registry.modelcontextprotocol.io) as
  `com.telemetrymachine/telemetry-machine`
- [What the plugin connects to](telemetry-machine/README.md#what-the-plugin-connects-to)
- [Privacy policy](https://telemetrymachine.com/privacy)

## Development

The plugin is in `telemetry-machine/`. Each release publishes two things to
`https://telemetrymachine.com/docs/skills/`:

- `index.json` and the skill files, from `scripts/build_skills_bundle.py`;
- `marketplace.json` and a pinned plugin zip under `releases/<version>/`, from
  `scripts/build_claude_marketplace.py`.

Run the tests with:

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Check the plugin with `claude plugin validate --strict .`.

To try the plugin against another Telemetry Machine site, add that site's MCP server
under its own name, and use that name instead of `telemetry-machine`:

```bash
claude mcp add --scope user --transport http <name> https://<site>/api/mcp
```

### MCP Registry

`server.json` lists the MCP server in the official MCP Registry
(`registry.modelcontextprotocol.io`) as `com.telemetrymachine/telemetry-machine`.
Releases don't publish it. To publish a change, raise `version` (the registry refuses
a version it already has), then, from the repo root:

```bash
mcp-publisher validate
mcp-publisher login dns --domain telemetrymachine.com --private-key <key>
mcp-publisher publish
mcp-publisher logout
```

`<key>` is the Ed25519 private key whose public half is in the `v=MCPv1` TXT record at
the apex of `telemetrymachine.com`.
