"""Config tools — scene collections, profiles, video settings, stream service, record directory."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    # ── Scene collections ──────────────────────────────────────
    @mcp.tool()
    async def get_scene_collection_list() -> dict:
        """List all scene collections and the currently active one."""
        return await client.execute("GetSceneCollectionList")

    @mcp.tool()
    async def set_current_scene_collection(name: str) -> dict:
        """Switch to a scene collection by name. Blocks until the switch completes."""
        return await client.execute("SetCurrentSceneCollection", sceneCollectionName=name)

    @mcp.tool()
    async def create_scene_collection(name: str) -> dict:
        """Create a new scene collection and switch to it."""
        return await client.execute("CreateSceneCollection", sceneCollectionName=name)

    # ── Profiles ──────────────────────────────────────
    @mcp.tool()
    async def get_profile_list() -> dict:
        """List all profiles and the currently active one."""
        return await client.execute("GetProfileList")

    @mcp.tool()
    async def set_current_profile(name: str) -> dict:
        """Switch to a profile by name."""
        return await client.execute("SetCurrentProfile", profileName=name)

    @mcp.tool()
    async def create_profile(name: str) -> dict:
        """Create a new profile and switch to it."""
        return await client.execute("CreateProfile", profileName=name)

    @mcp.tool()
    async def remove_profile(name: str) -> dict:
        """Remove a profile. If it's the active one, OBS switches away first."""
        return await client.execute("RemoveProfile", profileName=name)

    @mcp.tool()
    async def get_profile_parameter(category: str, name: str) -> dict:
        """Read a raw parameter from the current profile's .ini configuration.

        Args:
            category: Config category, e.g. "Output".
            name: Parameter name within that category.
        """
        return await client.execute("GetProfileParameter", parameterCategory=category, parameterName=name)

    @mcp.tool()
    async def set_profile_parameter(category: str, name: str, value: str | None) -> dict:
        """Write a raw parameter into the current profile's .ini configuration.
        Advanced/low-level — prefer a dedicated request when one exists.

        Args:
            category: Config category, e.g. "Output".
            name: Parameter name within that category.
            value: New value, or None to delete the parameter.
        """
        return await client.execute("SetProfileParameter", parameterCategory=category, parameterName=name, parameterValue=value)

    # ── Video settings ──────────────────────────────────────
    @mcp.tool()
    async def get_video_settings() -> dict:
        """Current canvas/output resolution and FPS (as a fraction — divide
        fpsNumerator by fpsDenominator for the true FPS)."""
        return await client.execute("GetVideoSettings")

    @mcp.tool()
    async def set_video_settings(
        fps_numerator: int | None = None, fps_denominator: int | None = None,
        base_width: int | None = None, base_height: int | None = None,
        output_width: int | None = None, output_height: int | None = None,
    ) -> dict:
        """Change canvas/output resolution and/or FPS. Width/height fields must
        be set in pairs (can't change baseWidth without baseHeight, etc).
        Range 1-4096 for all resolution fields.
        """
        params = {}
        if fps_numerator is not None:
            params["fpsNumerator"] = fps_numerator
        if fps_denominator is not None:
            params["fpsDenominator"] = fps_denominator
        if base_width is not None:
            params["baseWidth"] = base_width
        if base_height is not None:
            params["baseHeight"] = base_height
        if output_width is not None:
            params["outputWidth"] = output_width
        if output_height is not None:
            params["outputHeight"] = output_height
        return await client.execute("SetVideoSettings", **params)

    # ── Stream service settings ──────────────────────────────────────
    @mcp.tool()
    async def get_stream_service_settings() -> dict:
        """Current stream destination service type and settings (server/key etc)."""
        return await client.execute("GetStreamServiceSettings")

    @mcp.tool()
    async def set_stream_service_settings(service_type: str, settings: dict) -> dict:
        """Set the stream destination. For a plain custom RTMP target, use
        service_type="rtmp_custom" and settings={"server": "...", "key": "..."}.

        Args:
            service_type: e.g. "rtmp_custom" or "rtmp_common".
            settings: Service-specific settings object.
        """
        return await client.execute(
            "SetStreamServiceSettings", streamServiceType=service_type, streamServiceSettings=settings,
        )

    # ── Record directory ──────────────────────────────────────
    @mcp.tool()
    async def get_record_directory() -> dict:
        """Current output directory for recordings."""
        return await client.execute("GetRecordDirectory")

    @mcp.tool()
    async def set_record_directory(path: str) -> dict:
        """Set the output directory recordings are written to.

        Args:
            path: Absolute directory path.
        """
        if not path:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "path is required")
        return await client.execute("SetRecordDirectory", recordDirectory=path)
