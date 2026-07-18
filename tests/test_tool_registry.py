"""Tests for tool_registry.py's module-discovery/registration sanity checks.

Same pattern as the sibling Reaper-MCP project's test_tool_registry.py —
written to catch a repeat of a real bug found there: an over-broad
.gitignore rule silently excluded shipped tool modules from every published
copy of the repo, with no error at install or startup.
"""

import pkgutil

import pytest
from mcp.server.fastmcp import FastMCP

import obs_mcp.tools as tools_package
from obs_mcp.tool_registry import _EXPECTED_MODULES, register_all_tools


def _modules_on_disk_with_register() -> set[str]:
    found = set()
    for _finder, name, _ispkg in pkgutil.iter_modules(tools_package.__path__):
        module = __import__(f"obs_mcp.tools.{name}", fromlist=["register"])
        if hasattr(module, "register"):
            found.add(name)
    return found


class TestExpectedModulesStaysInSync:
    def test_every_registrable_module_is_expected(self):
        on_disk = _modules_on_disk_with_register()
        missing_from_expected = on_disk - _EXPECTED_MODULES
        assert not missing_from_expected, (
            f"Module(s) with register() exist on disk but aren't in "
            f"_EXPECTED_MODULES: {missing_from_expected}."
        )

    def test_every_expected_module_still_exists(self):
        on_disk = _modules_on_disk_with_register()
        stale = _EXPECTED_MODULES - on_disk
        assert not stale, (
            f"_EXPECTED_MODULES references module(s) that no longer exist: {stale}."
        )

    def test_full_registration_finds_every_expected_module(self):
        mcp = FastMCP("test")
        register_all_tools(mcp)
        on_disk = _modules_on_disk_with_register()
        assert on_disk == _EXPECTED_MODULES

    def test_tool_count_matches_protocol_coverage(self):
        """148 tools = full obs-websocket v5 coverage minus Sleep (batch-only,
        not implemented) plus diagnose_av_health (a pipeline tool, not a raw
        protocol wrapper). If this drifts, either a tool was silently dropped
        or a new one was added without updating this guard rail."""
        import re

        total = 0
        for _finder, name, _ispkg in pkgutil.iter_modules(tools_package.__path__):
            module = __import__(f"obs_mcp.tools.{name}", fromlist=["register"])
            src = module.__file__
            with open(src, encoding="utf-8") as f:
                total += len(re.findall(r"@mcp\.tool\(\)", f.read()))
        assert total == 148, f"Expected 148 tools, found {total}"
