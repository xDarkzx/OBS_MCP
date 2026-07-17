import importlib
import logging
import pkgutil
import sys

from mcp.server.fastmcp import FastMCP

import obs_mcp.tools as tools_package

logger = logging.getLogger(__name__)

# Every module that should exist on disk in a healthy checkout — update this
# when adding a new obs_mcp/tools/*.py module. Lets startup fail loud if a
# module goes missing instead of silently shipping fewer tools than intended.
_EXPECTED_MODULES = frozenset({
    "general_tools", "config_tools", "source_tools", "scene_tools",
    "input_tools", "transition_tools", "filter_tools", "scene_item_tools",
    "output_tools", "stream_record_tools", "media_tools", "ui_tools",
    "pipeline_tools",
})


def register_all_tools(mcp: FastMCP):
    """Discover and register every tool module in obs_mcp/tools/."""
    failures: list[tuple[str, Exception]] = []
    registered: list[str] = []

    for _finder, name, _ispkg in pkgutil.iter_modules(tools_package.__path__):
        try:
            module = importlib.import_module(f"obs_mcp.tools.{name}")
        except Exception as e:
            logger.error("IMPORT FAILED for tool module %s: %s", name, e, exc_info=True)
            sys.stderr.write(f"\n[obs-mcp] ERROR: Failed to import tool module '{name}': {e}\n")
            failures.append((name, e))
            continue

        if not hasattr(module, "register"):
            continue

        try:
            module.register(mcp)
            registered.append(name)
        except Exception as e:
            logger.error("REGISTER FAILED for %s: %s", name, e, exc_info=True)
            sys.stderr.write(f"\n[obs-mcp] ERROR: Tool registration failed for '{name}': {e}\n")
            failures.append((name, e))

    sys.stderr.write(f"[obs-mcp] Registered {len(registered)} tool module(s)\n")

    missing = _EXPECTED_MODULES - set(registered) - {n for n, _ in failures}
    if missing:
        sys.stderr.write(
            f"[obs-mcp] WARNING: expected module(s) not found on disk: {sorted(missing)}. "
            f"This install is incomplete.\n"
        )

    if failures:
        sys.stderr.write(
            f"[obs-mcp] WARNING: {len(failures)} tool module(s) failed to load: "
            f"{', '.join(n for n, _ in failures)}\n"
        )
