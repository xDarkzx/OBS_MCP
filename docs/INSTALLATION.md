# Installation Guide

Get OBS-MCP running in 3 steps: **install OBS-MCP → enable the WebSocket server in OBS → connect your AI client**.

All install options below assume you start from a **cloned copy of this repo** — there is no `pip install obs-mcp` published on PyPI.

---

## Step 1: Install OBS-MCP

### Option A: pip install from source

```bash
git clone https://github.com/xDarkzx/OBS-MCP.git
cd OBS-MCP
pip install -e .
```

This gives you the `obs-mcp` command.

### Option B: Run directly (no install)

```bash
cd OBS-MCP
python -m obs_mcp.main
```

---

## Step 2: Enable the WebSocket server in OBS

OBS Studio has shipped `obs-websocket` v5 built in since **v28** — no plugin to install.

1. Open OBS Studio.
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

---

## Step 3: Connect your AI client

### Claude Desktop

Edit your Claude Desktop config (Settings → Developer → Edit Config), add:

```json
{
  "mcpServers": {
    "obs": {
      "command": "obs-mcp",
      "env": {
        "OBS_HOST": "localhost",
        "OBS_PORT": "4455",
        "OBS_PASSWORD": "your_password_here"
      }
    }
  }
}
```

Restart Claude Desktop.

### Claude Code / Cursor / other MCP clients

Check your client's MCP server documentation for its config file location — the JSON block above is the same shape everywhere; only the file path differs.

If you installed via **Option B** (no pip install), use this instead:

```json
{
  "mcpServers": {
    "obs": {
      "command": "python",
      "args": ["-m", "obs_mcp.main"],
      "cwd": "/absolute/path/to/OBS-MCP",
      "env": { "OBS_HOST": "localhost", "OBS_PORT": "4455", "OBS_PASSWORD": "" }
    }
  }
}
```

---

## Verifying it works

With OBS running and the WebSocket server enabled, ask your AI assistant to call `get_version` — it should return OBS's version, obs-websocket's version, and platform info. If that works, everything downstream (scenes, audio, streaming, recording) will too.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "Could not connect to OBS" | OBS isn't running, or WebSocket server is disabled | Start OBS, check Tools → WebSocket Server Settings → Enable WebSocket server |
| "Authentication failed" | Password mismatch | Match `OBS_PASSWORD` to what's set in OBS's WebSocket Server Settings exactly, including empty vs. set |
| "command not found: obs-mcp" | Not installed, or installed in a different Python env than your AI client uses | Run `pip install -e .` from the repo folder; or use Option B (`python -m obs_mcp.main`) with an absolute path |
| Scene/input "not found" | Name mismatch | Names are case-sensitive and must match exactly. Call `get_scene_list` / `get_input_list` first to see exact names |
