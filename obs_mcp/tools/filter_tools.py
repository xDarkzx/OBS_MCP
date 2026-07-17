"""Filter tools — raw CRUD on source filters (audio/video effects chains).
For a one-call noise-free mic setup, see pipeline_tools.clean_audio_input instead
of hand-assembling a filter chain with these."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_source_filter_kind_list() -> dict:
        """List every filter kind this OBS install supports (noise_suppress_filter,
        noise_gate_filter, compressor_filter, color_filter, chroma_key_filter, etc)."""
        return await client.execute("GetSourceFilterKindList")

    @mcp.tool()
    async def get_source_filter_list(source_name: str) -> dict:
        """List all filters on a source (input or scene), in chain order.

        Args:
            source_name: Name of the source.
        """
        return await client.execute("GetSourceFilterList", sourceName=source_name)

    @mcp.tool()
    async def get_source_filter_default_settings(filter_kind: str) -> dict:
        """Default settings object for a filter kind."""
        return await client.execute("GetSourceFilterDefaultSettings", filterKind=filter_kind)

    @mcp.tool()
    async def create_source_filter(
        source_name: str, filter_name: str, filter_kind: str, filter_settings: dict | None = None,
    ) -> dict:
        """Add a new filter to a source.

        Args:
            source_name: Name of the source to add the filter to.
            filter_name: Name for the new filter.
            filter_kind: Filter kind (see get_source_filter_kind_list).
            filter_settings: Optional initial settings.
        """
        if not source_name or not filter_name or not filter_kind:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "source_name, filter_name, and filter_kind are required")
        return await client.execute(
            "CreateSourceFilter", sourceName=source_name, filterName=filter_name,
            filterKind=filter_kind, filterSettings=filter_settings or {},
        )

    @mcp.tool()
    async def remove_source_filter(source_name: str, filter_name: str) -> dict:
        """Remove a filter from a source."""
        if not source_name or not filter_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "source_name and filter_name are required")
        return await client.execute("RemoveSourceFilter", sourceName=source_name, filterName=filter_name)

    @mcp.tool()
    async def set_source_filter_name(source_name: str, filter_name: str, new_filter_name: str) -> dict:
        """Rename a filter."""
        return await client.execute(
            "SetSourceFilterName", sourceName=source_name, filterName=filter_name, newFilterName=new_filter_name,
        )

    @mcp.tool()
    async def get_source_filter(source_name: str, filter_name: str) -> dict:
        """Get a filter's enabled state, chain index, kind, and settings."""
        return await client.execute("GetSourceFilter", sourceName=source_name, filterName=filter_name)

    @mcp.tool()
    async def set_source_filter_index(source_name: str, filter_name: str, filter_index: int) -> dict:
        """Reorder a filter within a source's filter chain.

        Args:
            source_name: Name of the source.
            filter_name: Name of the filter to move.
            filter_index: New position, >= 0 (0 = first in chain).
        """
        if filter_index < 0:
            raise OBSMCPError(ErrorCode.VALUE_OUT_OF_RANGE, "filter_index must be >= 0")
        return await client.execute(
            "SetSourceFilterIndex", sourceName=source_name, filterName=filter_name, filterIndex=filter_index,
        )

    @mcp.tool()
    async def set_source_filter_settings(source_name: str, filter_name: str, filter_settings: dict, overlay: bool = True) -> dict:
        """Configure a filter's parameters.

        Args:
            source_name: Name of the source.
            filter_name: Name of the filter.
            filter_settings: Settings object.
            overlay: True = merge on top of current settings, False = reset to defaults first.
        """
        return await client.execute(
            "SetSourceFilterSettings", sourceName=source_name, filterName=filter_name,
            filterSettings=filter_settings, overlay=overlay,
        )

    @mcp.tool()
    async def set_source_filter_enabled(source_name: str, filter_name: str, filter_enabled: bool) -> dict:
        """Enable or disable a filter without removing it."""
        return await client.execute(
            "SetSourceFilterEnabled", sourceName=source_name, filterName=filter_name, filterEnabled=filter_enabled,
        )
