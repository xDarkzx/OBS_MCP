# Installation Guide

Get OBS-MCP running in 3 steps: **install OBS-MCP → enable the WebSocket server in OBS → connect your AI client**.

OBS-MCP is published on PyPI as `obs-mcp` — no clone required if you just want it running. The one-click installer below is still the easiest path if you've never touched MCP config files before, since it also writes your AI client's config for you.

---

## Step 1: Install OBS-MCP

### Option A: One-click installer (easiest, especially if you've never used MCP before)

- **Windows:** Double-click `install.bat` in the repo folder
- **macOS / Linux:** Open a terminal in the repo folder and run `bash install.sh`

The installer checks for Python (offers to install it if missing), installs `obs-mcp`, and — if you say yes when asked — automatically writes the config for Claude Desktop and/or LM Studio. Skip to [Step 2](#step-2-enable-the-websocket-server-in-obs) once it finishes. (This still needs a cloned/downloaded copy of the repo — it's the file `install.bat`/`install.sh` that does the work.)

### Option B: Install from PyPI (no clone needed)

```bash
pip install obs-mcp
```

or, for a true zero-install run (nothing left behind, matches the same idea as `npx` in the Node.js world):

```bash
uvx obs-mcp
```

Either way you get the `obs-mcp` command — you'll still need to write the client config yourself (see [Step 3](#step-3-connect-your-ai-client)), since there's no repo folder for an installer script to run from.

### Option C: pip install from source

```bash
git clone https://github.com/xDarkzx/OBS_MCP.git
cd OBS_MCP
pip install -e .
```

This gives you the `obs-mcp` command, and lets you `git pull` for updates or modify the code.

### Option D: Run directly (no install)

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

Then pick whichever of these matches your setup:

### You haven't set a password before (fresh setup)

Leave the password field blank in OBS. Leave `OBS_PASSWORD` empty (`""`) in the config in Step 3. This is the simplest option and is fine for a single-machine, purely local setup — nothing on your network can reach OBS's WebSocket port without also being on your machine or LAN.

If you'd rather set one now (recommended if other devices on your network can reach this PC), check **Enable Authentication**, set a password, and use that value below instead.

### You already have a password set (existing streaming setup)

If you've used obs-websocket before for something else — a Stream Deck integration, a chatbot, another automation tool — there's likely already a password configured, and you don't need to remember or reset it. OBS will show it to you:

1. **Tools → WebSocket Server Settings → Show Connect Info**.
2. This opens a window with your Server IP, Port, and **Password** already filled in and visible.
3. Copy the password exactly as shown — don't retype it, complex generated passwords are easy to mistype.

Paste that exact value into `OBS_PASSWORD` in Step 3. One thing worth knowing if your password has special characters: if it contains a `"` or `\`, escape it for JSON (`\"` and `\\` respectively) — everything else (spaces, `!@#$%^&*`, etc.) can go directly inside the quotes with no escaping needed.

---

OBS-MCP connects to `localhost:4455` with no password by default. Override with environment variables if yours differs:

| Variable | Default | Purpose |
|----------|---------|---------|
| `OBS_HOST` | `localhost` | Host OBS's WebSocket server is running on |
| `OBS_PORT` | `4455` | WebSocket server port |
| `OBS_PASSWORD` | *(empty)* | WebSocket server password, if you set one |

> **Keep OBS Studio open** — the connection only works while OBS is running with the WebSocket server enabled.

---

## Step 3: Connect Your AI Client

**If you used the one-click installer and said yes to configuring your client**, this is already done — skip to [Verify It Works](#verify-it-works).

Otherwise, pick your client below. Each section shows the **complete config** — copy it and you're done.

### Claude Desktop

**Option A: Installed with pip** (simplest config)

If you installed via `pip install obs-mcp` or `pip install -e .`, your config is:

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

**Option A2: Running via `uvx`** (nothing permanently installed)

If you're using `uvx obs-mcp` instead of a permanent install, point the config at `uvx` itself, not at an `obs-mcp` binary — there isn't one sitting on your PATH in this case:

```json
{
  "mcpServers": {
    "obs": {
      "command": "uvx",
      "args": ["obs-mcp"],
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

### LM Studio

Relevant if you're running a local/offline model instead of a cloud one — LM Studio's MCP support works the same way regardless of which model you have loaded.

1. Open LM Studio → **Program** tab in the right sidebar → **Install** → **Edit mcp.json**
2. Add the `obs` entry inside `mcpServers`:

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

3. Save — LM Studio loads MCP servers defined in `mcp.json` automatically.

<details>
<summary>Config file location</summary>

- **Windows:** `%USERPROFILE%\.lmstudio\mcp.json`
- **macOS / Linux:** `~/.lmstudio/mcp.json`

</details>

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
| "Authentication failed" | Password mismatch | Match `OBS_PASSWORD` to what's set in OBS's WebSocket Server Settings exactly, including empty vs. set. Use **Show Connect Info** in that settings window to see the exact stored password instead of retyping it from memory — this is the #1 cause of this error with pre-existing/complex passwords. |
| "command not found: obs-mcp" | Not installed, or installed in a different Python env than your AI client uses | Run the installer again, or manually: `pip install obs-mcp` (or `pip install -e .` from the repo folder if you're working from a clone) |
| Config not working | Wrong path or JSON syntax | Copy the complete example above, validate JSON at jsonlint.com |
| Claude Desktop doesn't see OBS-MCP | Config not loaded | Restart Claude Desktop after editing the config |
| Tool calls hang | OBS itself showing a blocking dialog | Check for a "scene collection changed" or similar prompt in OBS — some requests block until you dismiss OBS-side UI |
| Scene/input "not found" errors | Name mismatch | Names are case-sensitive and must match exactly. Call `get_scene_list` / `get_input_list` first to see exact names |
| "externally-managed-environment" error during `install.sh` | Modern Python + PEP 668 | Re-run `install.sh` — it auto-retries with `--user`. Or use `pipx install -e .` |
| `bash: ./install.sh: /bin/bash^M: bad interpreter` | Git on Windows converted line endings to CRLF | Run `bash install.sh` (don't execute directly), or `sed -i 's/\r$//' install.sh`. Pulling the latest repo (with `.gitattributes`) avoids this. |
| `install.sh` / `install.bat` says "obs-mcp isn't resolving on PATH" | Multiple Python installs on the machine, or a fresh terminal hasn't picked up the PATH change yet | Close and reopen your terminal, then run `obs-mcp --help` (or just retry asking your AI client) — if it still doesn't resolve, run `which -a obs-mcp` (macOS/Linux) or `where obs-mcp` (Windows) to see every copy on PATH and which one wins |
