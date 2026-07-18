# Contributing to OBS-MCP

Thanks for your interest in contributing! Every PR — tool, bug fix, doc, or test — is welcome.

## Development setup

```bash
git clone https://github.com/xDarkzx/OBS_MCP.git
cd OBS_MCP
pip install -e ".[dev]"
```

This installs `obs-mcp` in editable mode along with `pytest` / `pytest-asyncio` for tests.

## Running tests

```bash
pytest tests/ -x -q
```

All tests must pass before submitting a PR.

## Adding a new tool

1. Pick the right module in `obs_mcp/tools/` — or create a new `*_tools.py` file. The tool registry auto-discovers any module that defines `register(mcp)`; helper files without that function are silently skipped.
2. Inside `register(mcp)`, define your tool with the `@mcp.tool()` decorator.
3. Validate required inputs (missing-parameter checks, range-check anything obs-websocket documents a numeric range for) before dispatching.
4. Dispatch via `client.execute("RequestType", **params)` — the exact `RequestType` string and field names come from the [obs-websocket v5 protocol spec](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md). Verify field names against that spec (or the actual OBS source for filter/plugin settings) — don't guess.
5. If you're adding a new module, add its name to `_EXPECTED_MODULES` in `tool_registry.py`.
6. Add tests in `tests/`.

Example:

```python
from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError

def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def my_tool(scene_name: str) -> dict:
        """Short description of what this tool does.

        Args:
            scene_name: What this parameter controls.
        """
        if not scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "scene_name is required")
        return await client.execute("MyRequestType", sceneName=scene_name)
```

See `obs_mcp/tools/scene_tools.py` for a straightforward reference implementation.

## Adding a new pipeline tool

Pipeline tools (`pipeline_tools.py`) compose several raw requests into one call that
does what the user actually wants, instead of making the AI hand-assemble the
mechanism. If you're adding one:

1. Verify every setting field name against the actual OBS Studio source
   (`plugins/obs-filters/*.c` for filter settings) — the UI labels in OBS's
   own dialogs don't always match the underlying JSON keys.
2. Query what's actually available (e.g. `GetSourceFilterKindList`) rather than
   assuming a filter kind is registered — it varies by platform and OBS build.
3. Skip stages that already exist instead of duplicating them.

## Code style

- Python 3.10+ (type hints on public surfaces).
- No comments or docstrings on obvious code — well-named identifiers are enough.
- Keep input validation explicit; error handling should mention the specific bad value.

## Security

- Validate every parameter before dispatch.
- Never commit API keys, OBS WebSocket passwords, or credentials. Secrets go in environment variables, not source.

## Pull requests

- Keep PRs focused on a single change.
- Include tests for new tools.
- Describe what your change does and why.
- Update `CHANGELOG.md` under the current unreleased section.

## Reporting issues

Open an issue on GitHub with:

- What you expected to happen.
- What actually happened.
- Steps to reproduce.
- Your OS, Python version, and OBS Studio version.
- Relevant stderr output from the MCP server (the `[obs-mcp]` banner lines).
