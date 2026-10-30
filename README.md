# Telemetry Machine agent skills

Skills that let coding agents set up, query and investigate Telemetry Machine. The
Claude Code plugin also adds Telemetry Machine's MCP server
(`https://telemetrymachine.com/api/mcp`) as `telemetry-machine`. Agents sign in to it
with OAuth in the browser; there is no key to copy.

| Skill | Use |
|---|---|
| `tm-instrument` | Loads when the agent adds or changes OpenTelemetry instrumentation; gives it TM's OpenTelemetry doc and has it look up names with `get_semconv`. |
| `tm-investigate` | Loads when the agent investigates or root-causes an issue; walks it through datasets, SLOs (`get_slos`), annotations (`get_annotations`), `run_surface` and `run_query`. |
| `tm-cli` | Loads when the agent uses tm-cli; its commands, column names and query pitfalls. |

The skills are short on purpose. Agents already know OpenTelemetry and SQL; the skills
hold only what they can't know about Telemetry Machine. The MCP server's tools,
errors and onboarding guide carry the rest.

## Install

### Claude Code

Run in a terminal (Claude Code 2.1.292 or later):

```bash
claude plugin install telemetry-machine --marketplace https://telemetrymachine.com/docs/skills/marketplace.json
```

Then start Claude Code in your application's folder, run `/mcp`, choose
`telemetry-machine` and sign in. Then run `/mcp__telemetry-machine__onboarding`.

After that, ask for what you need. When the agent adds OpenTelemetry instrumentation
or investigates an issue, the `tm-instrument` and `tm-investigate` skills load and send
it to Telemetry Machine.

For a site other than telemetrymachine.com, also add that site's server under its own
name, and use that name instead:

```bash
claude mcp add --scope user --transport http tm-local https://tm-local.test/api/mcp
```

### Other agents

Add `https://telemetrymachine.com/api/mcp` as a remote (Streamable HTTP) MCP server and
sign in when the agent asks. To onboard, ask the agent to call `get_onboarding_guide`
and follow it. To onboard another system once you're sending data, ask it to call
`get_instrumentation_guide`. Telemetry Machine's onboarding page shows the exact steps
for Codex, Cursor and others. The skills are also at
`https://telemetrymachine.com/docs/skills/index.json`.

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

### MCP Registry

`server.json` lists the MCP server in the official MCP Registry
(`registry.modelcontextprotocol.io`) as `com.telemetrymachine/telemetry-machine`.
Releases don't publish it. To publish a change, raise `version` (the registry refuses
a version it already has), then, from the repo root on Monster:

```bash
mcp-publisher validate
mcp-publisher login dns --domain telemetrymachine.com \
  --private-key "$(pass show telemetry-machine/mcp-registry-dns-key | head -1)"
mcp-publisher publish
mcp-publisher logout
```

The login signs with the Ed25519 key in `pass`; the registry checks it against the
`v=MCPv1` TXT record at the apex of `telemetrymachine.com` (in the `infrastructure`
repo's Cloudflare zone).
