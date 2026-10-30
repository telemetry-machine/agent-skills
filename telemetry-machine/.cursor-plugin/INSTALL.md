# Installing the Telemetry Machine plugin in Cursor

Telemetry Machine ships as a Cursor **plugin** — skills, agents, the `/telemetry-machine-setup`
command, hooks, and the Telemetry Machine MCP server, all declared in
[`plugin.json`](./plugin.json).

## Recommended — Cursor plugin directory

Install from the public listing:
**[cursor.directory/plugins/telemetry-machine](https://cursor.directory/plugins/telemetry-machine)**

Open the listing and use its **Install** action. Cursor shows the plugin's MCP
server config for review before passing it to Cursor — confirm it, then restart
Cursor or run **Developer: Reload Window** from the command palette.

## Teams / Enterprise — Marketplace import

GitHub import is available on Teams and Enterprise plans via Team Marketplaces:

1. Open the Cursor dashboard → **Settings > Plugins**.
2. Under **Team Marketplaces**, import from the repository URL:
   `https://github.com/telemetry-machine/agent-skills`
3. Add the `telemetry-machine` plugin to your marketplace and grant team access.

## Manual / local install (development)

For plugin development or offline use, load it from Cursor's local plugins
folder by symlinking (recommended, so `git pull` keeps it current) or copying.

### macOS / Linux

```bash
git clone https://github.com/telemetry-machine/agent-skills.git
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/agent-skills/telemetry-machine" ~/.cursor/plugins/local/telemetry-machine
```

### Windows (PowerShell)

```powershell
git clone https://github.com/telemetry-machine/agent-skills.git
New-Item -ItemType Directory -Force "$env:USERPROFILE\.cursor\plugins\local" | Out-Null
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.cursor\plugins\local\telemetry-machine" `
  -Target "$(Resolve-Path .\agent-skills\telemetry-machine)"
```

Then **restart Cursor**, or run **Developer: Reload Window** from the command
palette so Cursor rescans local plugins.

## Verify

The plugin root must contain `.cursor-plugin/plugin.json`:

```bash
ls ~/.cursor/plugins/local/telemetry-machine/.cursor-plugin/plugin.json
```

In Agent chat, type `/` and search for `tm-cli` to confirm the skill loaded.

## Update

```bash
cd agent-skills && git pull
```

Reload the window afterward. (If you copied the directory instead of symlinking,
re-copy `telemetry-machine/` into `~/.cursor/plugins/local/`.)

## Uninstall

```bash
rm ~/.cursor/plugins/local/telemetry-machine   # removes the symlink, not your clone
```

## MCP server

The plugin declares the Telemetry Machine MCP server (`mcp.json`). You can also configure
it independently — see
[Telemetry Machine Docs: MCP Configuration](https://docs.telemetrymachine.com/integrations/mcp/configuration-guide/).
The `/telemetry-machine-setup` command walks through configuration interactively.

See [Cursor: Plugins](https://cursor.com/docs/plugins) for the underlying plugin
system.
