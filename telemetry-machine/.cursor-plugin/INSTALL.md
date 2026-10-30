# Installing the Telemetry Machine plugin in Cursor

The plugin adds Telemetry Machine's MCP server (`https://telemetrymachine.com/api/mcp`)
and its skills to Cursor, as declared in [`plugin.json`](./plugin.json).

## Teams / Enterprise — Marketplace import

Team admins can add this repo as a marketplace:

1. In the Cursor dashboard, open **Plugins & MCPs**, click **Add Marketplace** and
   choose **Import from Repo**.
2. Import `https://github.com/telemetry-machine/agent-skills`.
3. Team members then find `telemetry-machine` under **Customize** and select **Install**.

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

## Sign in

Open **Cursor Settings → MCP**, find `telemetry-machine` and sign in to Telemetry
Machine in the browser. There is no key to copy. To send your first data, ask the agent
to call `get_onboarding_guide` and follow it.

To add the MCP server without the plugin, see Telemetry Machine's
[quick start](https://telemetrymachine.com/docs/quick-start). See
[Cursor: Plugins](https://cursor.com/docs/plugins) for the underlying plugin system.
