# Installation Guide

Get OBS-MCP running in 3 steps: **install OBS-MCP → enable the WebSocket server in OBS → connect your AI client**.

All install options below assume you start from a **cloned copy of this repo** — there is no `pip install obs-mcp` published on PyPI yet.

---

## Step 1: Install OBS-MCP

### Option A: pip install from source

```bash
git clone https://github.com/xDarkzx/OBS_MCP.git
cd OBS_MCP
pip install -e .
```

This gives you the `obs-mcp` command.

### Option B: Run directly (no install)

```bash
cd OBS_MCP
python -m obs_mcp.main
```

When running directly, use `python -m obs_mcp.main` anywhere this guide says `obs-mcp`.

---

## Step 2: Enable the WebSocket Server in OBS

OBS Studio has shipped `obs-websocket` v5 built in since **v28** — no plugin to install.

1. Open **OBS Studio**.
2. **Tools → WebSocket Server Settings**.
3. Check **Enable WebSocket server**.
4. Note the **Server Port** (default `4455`).
5. If you want a password (recommended if OBS is reachable from other machines on your network), set one and note it — otherwise leave it blank.

OBS-MCP connects to `localhost:4455` with no password by default. Override with environment variables if yours differs:

| Variable | Default | Purpose |
|----------|---------|---------|
| `OBS_HOST` | `localhost` | Host OBS's WebSocket server is running on |
| `OBS_PORT` | `4455` | WebSocket server port |
| `OBS_PASSWORD` | *(empty)* | WebSocket server password, if you set one |

> **Keep OBS Studio open** — the connection only works while OBS is running with the WebSocket server enabled.

---

## Step 3: Connect Your AI Client

Pick your client below. Each section shows the **complete config** — copy it and you're done.

### Claude Desktop

**Option A: Installed with pip** (simplest config)

If you installed via `pip install -e .`, your config is:

```json
{
  "mcpServers": {
    "obs": {
      "command": "obs-mcp",
      "env": {
        "OBS_HOST": "localhost",
        "OBS_PORT": "4455",
        "OBS_PASSWORD": ""
      }
    }
  }
}
```

**Option B: Running from source** (no pip install)

If you skipped `pip install` and want to run directly from the cloned repo:

Windows:
```json
{
  "mcpServers": {
    "obs": {
      "command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
      "args": ["-m", "obs_mcp.main"],
      "cwd": "C:\\Users\\YourName\\Projects\\OBS_MCP",
      "env": { "OBS_HOST": "localhost", "OBS_PORT": "4455", "OBS_PASSWORD": "" }
    }
  }
}
```

macOS / Linux:
```json
{
  "mcpServers": {
    "obs": {
      "command": "/usr/bin/python3",
      "args": ["-m", "obs_mcp.main"],
      "cwd": "/Users/yourname/Projects/OBS_MCP",
      "env": { "OBS_HOST": "localhost", "OBS_PORT": "4455", "OBS_PASSWORD": "" }
    }
  }
}
```

> **How to find your Python path:** Run `where python` (Windows) or `which python3` (macOS/Linux).
> On Apple Silicon with Homebrew, the path is usually `/opt/homebrew/bin/python3`.

**Already have other stuff in your config?** Just add the `"obs"` key inside the existing `mcpServers`:

```json
{
  "mcpServers": {
    "obs": {
      "command": "obs-mcp",
      "env": { "OBS_HOST": "localhost", "OBS_PORT": "4455", "OBS_PASSWORD": "" }
    },
    "some-other-server": {
      "command": "some-other-command"
    }
  }
}
```

<details>
<summary>Config file locations</summary>

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json` (or `$XDG_CONFIG_HOME/Claude/` if set)

</details>

Save the config and **restart Claude Desktop**.

### Claude Code (CLI)

```bash
claude --mcp-server obs=obs-mcp
```

Or add to your project's `.mcp.json` for persistent config:

```json
{
  "mcpServers": {
    "obs": {
      "command": "obs-mcp",
      "type": "stdio",
      "env": { "OBS_HOST": "localhost", "OBS_PORT": "4455", "OBS_PASSWORD": "" }
    }
  }
}
```

### Cursor

1. Open **Settings** → **Tools & MCP** → **New MCP Server**
2. Set type to `command`, enter `obs-mcp`
3. Done

Or create `.cursor/mcp.json` in your project root (or `~/.cursor/mcp.json` for global):

```json
{
  "mcpServers": {
    "obs": {
      "command": "obs-mcp",
      "env": { "OBS_HOST": "localhost", "OBS_PORT": "4455", "OBS_PASSWORD": "" }
    }
  }
}
```

### Other MCP Clients

OBS-MCP uses **stdio transport**. Point any MCP-compatible client at the `obs-mcp` command, with `OBS_HOST` / `OBS_PORT` / `OBS_PASSWORD` in its environment if your setup differs from the defaults.

---

## Verify It Works

1. **Open OBS Studio** (with the WebSocket server enabled)
2. Open your AI client
3. Ask it:

```
"What OBS scenes do I have?"
```

If you see your actual scene list come back, you're all set — everything downstream (audio mixer, filters, streaming, recording) will work too.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "Could not connect to OBS" | OBS isn't running, or WebSocket server is disabled | Start OBS, check Tools → WebSocket Server Settings → Enable WebSocket server |
| "Authentication failed" | Password mismatch | Match `OBS_PASSWORD` to what's set in OBS's WebSocket Server Settings exactly, including empty vs. set |
| "command not found: obs-mcp" | Not installed, or installed in a different Python env than your AI client uses | Run `pip install -e .` from the repo folder |
| Config not working | Wrong path or JSON syntax | Copy the complete example above, validate JSON at jsonlint.com |
| Claude Desktop doesn't see OBS-MCP | Config not loaded | Restart Claude Desktop after editing the config |
| Tool calls hang | OBS itself showing a blocking dialog | Check for a "scene collection changed" or similar prompt in OBS — some requests block until you dismiss OBS-side UI |
| Scene/input "not found" errors | Name mismatch | Names are case-sensitive and must match exactly. Call `get_scene_list` / `get_input_list` first to see exact names |
