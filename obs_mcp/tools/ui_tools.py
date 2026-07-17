"""UI tools — studio mode toggle, opening property/filter/interact dialogs,
monitor list, and projector windows."""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_studio_mode_enabled() -> dict:
        """Whether studio mode (separate Preview/Program) is enabled."""
        return await client.execute("GetStudioModeEnabled")

    @mcp.tool()
    async def set_studio_mode_enabled(enabled: bool) -> dict:
        """Enable or disable studio mode."""
        return await client.execute("SetStudioModeEnabled", studioModeEnabled=enabled)

    @mcp.tool()
    async def open_input_properties_dialog(input_name: str) -> dict:
        """Open an input's Properties dialog in the OBS UI."""
        return await client.execute("OpenInputPropertiesDialog", inputName=input_name)

    @mcp.tool()
    async def open_input_filters_dialog(input_name: str) -> dict:
        """Open an input's Filters dialog in the OBS UI."""
        return await client.execute("OpenInputFiltersDialog", inputName=input_name)

    @mcp.tool()
    async def open_input_interact_dialog(input_name: str) -> dict:
        """Open an input's Interact dialog in the OBS UI."""
        return await client.execute("OpenInputInteractDialog", inputName=input_name)

    @mcp.tool()
    async def get_monitor_list() -> dict:
        """List connected monitors (for opening a projector on one)."""
        return await client.execute("GetMonitorList")

    @mcp.tool()
    async def open_video_mix_projector(
        video_mix_type: str, monitor_index: int = -1, projector_geometry: str = "",
    ) -> dict:
        """Open a fullscreen or windowed projector for Preview/Program/Multiview.

        Args:
            video_mix_type: OBS_WEBSOCKET_VIDEO_MIX_TYPE_PREVIEW, _PROGRAM, or _MULTIVIEW.
            monitor_index: Monitor to open fullscreen on (see get_monitor_list),
                -1 for windowed.
            projector_geometry: Qt-base64 window geometry for windowed mode;
                mutually exclusive with monitor_index.
        """
        params = {"videoMixType": video_mix_type, "monitorIndex": monitor_index}
        if projector_geometry:
            params["projectorGeometry"] = projector_geometry
        return await client.execute("OpenVideoMixProjector", **params)

    @mcp.tool()
    async def open_source_projector(
        source_name: str, monitor_index: int = -1, projector_geometry: str = "",
    ) -> dict:
        """Open a fullscreen or windowed projector for a specific source.

        Args:
            source_name: Name of the source (input or scene).
            monitor_index: Monitor to open fullscreen on, -1 for windowed.
            projector_geometry: Qt-base64 window geometry for windowed mode.
        """
        params = {"sourceName": source_name, "monitorIndex": monitor_index}
        if projector_geometry:
            params["projectorGeometry"] = projector_geometry
        return await client.execute("OpenSourceProjector", **params)
