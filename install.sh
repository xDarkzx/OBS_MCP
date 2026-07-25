#!/bin/bash
set -euo pipefail

# Ensure PATH covers Homebrew on both Intel and Apple Silicon Macs so brew/python3
# are findable even when this is launched from Finder (which strips PATH).
if [[ "${OSTYPE:-}" == "darwin"* ]]; then
    # Process Intel first, Apple Silicon second: each iteration prepends, so
    # the last one processed ends up first. That makes /opt/homebrew win by
    # default when neither is already on PATH (e.g. launched from Finder,
    # which strips PATH) — the correct default on Apple Silicon — while the
    # "already on PATH" check below means a user's own correctly-ordered
    # shell PATH is never touched either way.
    for hb in /usr/local /opt/homebrew; do
        if [ -x "$hb/bin/brew" ] && [[ ":$PATH:" != *":$hb/bin:"* ]]; then
            export PATH="$hb/bin:$hb/sbin:$PATH"
        fi
    done
fi

echo ""
echo " ============================================"
echo "  OBS-MCP - One-Click Installer"
echo "  AI-powered stream and recording control for OBS Studio"
echo " ============================================"
echo ""
echo "  Platform: $(uname -s) $(uname -m)"
echo ""

# ── Check Python ──────────────────────────────────────────
echo "[1/5] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo ""
    echo " Python is not installed."
    echo ""
    read -rp " Would you like to install Python now? (y/n): " INSTALL_PY
    if [[ "$INSTALL_PY" =~ ^[Yy]$ ]]; then
        if [[ "${OSTYPE:-}" == "darwin"* ]]; then
            if command -v brew &> /dev/null; then
                echo " Installing Python via Homebrew..."
                brew install python3
            else
                echo " Homebrew not found. Install it first:"
                echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                echo " Then run this installer again."
                exit 1
            fi
        else
            if command -v apt &> /dev/null; then
                echo " Installing Python via apt..."
                sudo apt update && sudo apt install -y python3 python3-pip
            elif command -v dnf &> /dev/null; then
                echo " Installing Python via dnf..."
                sudo dnf install -y python3 python3-pip
            elif command -v pacman &> /dev/null; then
                echo " Installing Python via pacman..."
                sudo pacman -S --noconfirm python python-pip
            else
                echo " Could not detect your package manager."
                echo " Install Python 3.10+ manually: https://www.python.org/downloads/"
                exit 1
            fi
        fi
        # Re-detect after install
        if command -v python3 &> /dev/null; then
            PYTHON=python3
        elif command -v python &> /dev/null; then
            PYTHON=python
        else
            echo ""
            echo " ERROR: Python install succeeded but python3 not found in PATH."
            echo " Close and reopen your terminal, then run this installer again."
            exit 1
        fi
    else
        echo ""
        echo " OBS-MCP requires Python 3.10+ to run."
        echo " Install it and come back!"
        echo ""
        echo "   macOS:  brew install python3"
        echo "   Ubuntu: sudo apt install python3 python3-pip"
        echo "   Or:     https://www.python.org/downloads/"
        echo ""
        exit 1
    fi
fi

PYVER=$($PYTHON --version 2>&1)
echo "  Found $PYVER"

# Verify Python >= 3.10
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo ""
    echo " ERROR: Python 3.10+ is required, but you have $PYVER"
    echo " Please upgrade Python: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# Warn if running inside a virtual environment
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo ""
    echo " WARNING: You are inside a virtual environment."
    echo " obs-mcp should be installed globally so Claude Desktop can find it."
    echo " Deactivate your venv first: deactivate"
    echo ""
    exit 1
fi

# ── Install obs-mcp ────────────────────────────────────────
echo ""
echo "[2/5] Installing obs-mcp..."

# Check if pip is available
if ! $PYTHON -m pip --version &> /dev/null; then
    echo "  pip not found, installing pip..."
    if ! $PYTHON -m ensurepip --upgrade &> /dev/null; then
        echo ""
        echo " ERROR: pip is not installed and ensurepip failed."
        echo " Try: $PYTHON -m ensurepip --upgrade"
        echo " Or reinstall Python with pip enabled."
        echo ""
        exit 1
    fi
fi

# Install from local directory (not on PyPI yet).
# Many modern Pythons (Homebrew on macOS, Debian/Ubuntu, Fedora) ship with
# PEP 668 "externally-managed" protection that blocks global pip installs.
# Try a normal install first; if it fails with that error, retry with --user.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

install_log=$(mktemp)
if $PYTHON -m pip install -e "$SCRIPT_DIR" 2>"$install_log"; then
    rm -f "$install_log"
    echo "  obs-mcp installed successfully!"
elif grep -qE "externally-managed|error: could not install" "$install_log"; then
    echo "  System pip is externally managed — retrying with --user..."
    if ! $PYTHON -m pip install --user -e "$SCRIPT_DIR"; then
        cat "$install_log"
        rm -f "$install_log"
        echo ""
        echo " ERROR: pip install --user also failed."
        echo " Try: pipx install -e $SCRIPT_DIR"
        echo ""
        exit 1
    fi
    rm -f "$install_log"
    echo "  obs-mcp installed to user site-packages."
    # Make sure ~/.local/bin is on PATH so Claude Desktop finds obs-mcp
    USER_BIN="$($PYTHON -m site --user-base)/bin"
    if [ -d "$USER_BIN" ] && [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        echo ""
        echo "  NOTE: $USER_BIN is not on your PATH."
        echo "  Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "    export PATH=\"$USER_BIN:\$PATH\""
        echo ""
    fi
else
    cat "$install_log"
    rm -f "$install_log"
    echo ""
    echo " ERROR: pip install failed. See error above."
    echo " If you see 'externally-managed', install pipx and retry with:"
    echo "   pipx install -e $SCRIPT_DIR"
    echo ""
    exit 1
fi

# Verify the 'obs-mcp' command on PATH actually points at the Python we just
# installed with — not a stale install from a different Python (e.g. an old
# Intel-Homebrew obs-mcp shadowing a fresh Apple-Silicon one, or any other
# case of two Pythons on the same machine). Claude Desktop will run whatever
# 'obs-mcp' resolves to, which may not be what this script just set up.
RESOLVED_CMD="$(command -v obs-mcp 2>/dev/null || true)"
if [ -z "$RESOLVED_CMD" ]; then
    echo ""
    echo "  NOTE: 'obs-mcp' isn't on PATH yet in this shell session."
    echo "  Open a new terminal (or source your shell rc file) before asking"
    echo "  Claude to use it — Claude Desktop launches commands using your"
    echo "  normal shell PATH, so if it doesn't resolve here, it won't there."
elif [ -f "$RESOLVED_CMD" ] && head -1 "$RESOLVED_CMD" 2>/dev/null | grep -q '^#!'; then
    SHEBANG_PY="$(head -1 "$RESOLVED_CMD" | sed 's/^#!//' | awk '{print $1}')"
    ACTUAL_PY="$($PYTHON -c 'import sys; print(sys.executable)')"
    if [ -n "$SHEBANG_PY" ] && [ "$SHEBANG_PY" != "$ACTUAL_PY" ]; then
        echo ""
        echo "  WARNING: 'obs-mcp' on your PATH is bound to a DIFFERENT"
        echo "  Python than the one just used to install it:"
        echo "    On PATH now: $SHEBANG_PY"
        echo "    Just used:   $ACTUAL_PY"
        echo "  This usually means an older obs-mcp install (a different"
        echo "  Homebrew Python, a previous global pip install, etc.) is"
        echo "  shadowing the one just installed. Run 'echo \$PATH' and check"
        echo "  which directory containing 'obs-mcp' comes first, or run"
        echo "  'which -a obs-mcp' to see every copy on PATH."
        echo ""
    fi
fi

# ── Configure Claude Desktop ──────────────────────────────
echo ""
echo "[3/5] Configuring Claude Desktop..."

read -rp "  Configure Claude Desktop for OBS-MCP? (y/n): " CONFIGURE_CLAUDE
if [[ ! "$CONFIGURE_CLAUDE" =~ ^[Yy]$ ]]; then
    echo "  Skipped. See docs/INSTALLATION.md for manual setup."
else
    if [[ "${OSTYPE:-}" == "darwin"* ]]; then
        CONFIG_DIR="$HOME/Library/Application Support/Claude"
    else
        CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/Claude"
    fi
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

    mkdir -p "$CONFIG_DIR"

    if [ -f "$CONFIG_FILE" ]; then
        if grep -q '"obs"' "$CONFIG_FILE" 2>/dev/null; then
            echo "  Claude Desktop config already has an obs entry - skipping."
        else
            cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
            echo "  Backed up existing config to: $CONFIG_FILE.bak"
            echo ""
            echo "  Found existing Claude Desktop config at:"
            echo "  $CONFIG_FILE"
            echo ""
            echo "  Add this inside your \"mcpServers\" block:"
            echo ""
            echo '    "obs": {'
            echo '      "command": "obs-mcp",'
            echo '      "env": {'
            echo '        "OBS_HOST": "localhost",'
            echo '        "OBS_PORT": "4455",'
            echo '        "OBS_PASSWORD": ""'
            echo '      }'
            echo '    }'
            echo ""
        fi
    else
        cat > "$CONFIG_FILE" << 'EOF'
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
EOF
        chmod 600 "$CONFIG_FILE"
        echo "  Created Claude Desktop config at:"
        echo "  $CONFIG_FILE"
    fi
fi

# ── Configure LM Studio ───────────────────────────────────
# LM Studio's mcp.json uses the exact same {"mcpServers": {...}} shape as
# Claude Desktop's config, just a different file location — no XDG
# variance, same path on macOS and Linux.
echo ""
echo "[4/5] Configuring LM Studio..."

read -rp "  Configure LM Studio for OBS-MCP? (y/n): " CONFIGURE_LMSTUDIO
if [[ ! "$CONFIGURE_LMSTUDIO" =~ ^[Yy]$ ]]; then
    echo "  Skipped. See docs/INSTALLATION.md for manual setup."
else
    LMSTUDIO_CONFIG_DIR="$HOME/.lmstudio"
    LMSTUDIO_CONFIG_FILE="$LMSTUDIO_CONFIG_DIR/mcp.json"

    mkdir -p "$LMSTUDIO_CONFIG_DIR"

    if [ -f "$LMSTUDIO_CONFIG_FILE" ]; then
        if grep -q '"obs"' "$LMSTUDIO_CONFIG_FILE" 2>/dev/null; then
            echo "  LM Studio config already has an obs entry - skipping."
        else
            cp "$LMSTUDIO_CONFIG_FILE" "$LMSTUDIO_CONFIG_FILE.bak"
            echo "  Backed up existing config to: $LMSTUDIO_CONFIG_FILE.bak"
            echo ""
            echo "  Found existing LM Studio config at:"
            echo "  $LMSTUDIO_CONFIG_FILE"
            echo ""
            echo "  Add this inside your \"mcpServers\" block:"
            echo ""
            echo '    "obs": {'
            echo '      "command": "obs-mcp",'
            echo '      "env": {'
            echo '        "OBS_HOST": "localhost",'
            echo '        "OBS_PORT": "4455",'
            echo '        "OBS_PASSWORD": ""'
            echo '      }'
            echo '    }'
            echo ""
        fi
    else
        cat > "$LMSTUDIO_CONFIG_FILE" << 'EOF'
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
EOF
        chmod 600 "$LMSTUDIO_CONFIG_FILE"
        echo "  Created LM Studio config at:"
        echo "  $LMSTUDIO_CONFIG_FILE"
    fi
fi

# ── Done ──────────────────────────────────────────────────
echo ""
echo "[5/5] Done!"
echo ""
echo " ============================================"
echo "  SETUP COMPLETE!"
echo " ============================================"
echo ""
echo " Next steps:"
echo ""
echo "  1. Open OBS Studio"
echo "  2. Enable the WebSocket server:"
echo "     Tools > WebSocket Server Settings > Enable WebSocket server"
echo "     (default port 4455 — if you set a password there, put it in"
echo "     OBS_PASSWORD in your AI client's config)"
echo "  3. Restart Claude Desktop / LM Studio (whichever you configured, if open)"
echo "  4. Ask your AI: \"What OBS scenes do I have?\""
echo ""
echo " OBS Studio must be open with the WebSocket server enabled for MCP to work."
echo ""
echo " Docs: https://github.com/xDarkzx/OBS_MCP"
echo " If this is useful to you, a star on GitHub helps other people find it!"
echo " ============================================"
echo ""
