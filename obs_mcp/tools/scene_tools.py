"""Scene tools — list/create/remove/rename scenes, program/preview scene control,
per-scene transition overrides, canvases and groups."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_canvas_list() -> dict:
        """List all canvases in OBS (multi-canvas is a newer OBS feature; most
        setups only have the main canvas)."""
        return await client.execute("GetCanvasList")

    @mcp.tool()
    async def get_scene_list() -> dict:
        """List every scene, plus the current program and preview scene names."""
        return await client.execute("GetSceneList")

    @mcp.tool()
    async def get_group_list() -> dict:
        """List all groups (OBS treats groups as a special kind of scene)."""
        return await client.execute("GetGroupList")

    @mcp.tool()
    async def get_current_program_scene() -> dict:
        """The scene currently live on Program (what viewers see)."""
        return await client.execute("GetCurrentProgramScene")

    @mcp.tool()
    async def set_current_program_scene(scene_name: str) -> dict:
        """Switch the live Program scene — the core "cut to this scene" action.

        Args:
            scene_name: Exact scene name (see get_scene_list).
        """
        if not scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "scene_name is required")
        return await client.execute("SetCurrentProgramScene", sceneName=scene_name)

    @mcp.tool()
    async def get_current_preview_scene() -> dict:
        """The scene currently loaded in Preview. Only meaningful in studio mode."""
        return await client.execute("GetCurrentPreviewScene")

    @mcp.tool()
    async def set_current_preview_scene(scene_name: str) -> dict:
        """Load a scene into Preview (studio mode only) — stage it before
        transitioning to Program with trigger_studio_mode_transition.

        Args:
            scene_name: Exact scene name.
        """
        if not scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "scene_name is required")
        return await client.execute("SetCurrentPreviewScene", sceneName=scene_name)

    @mcp.tool()
    async def create_scene(scene_name: str) -> dict:
        """Create a new, empty scene.

        Args:
            scene_name: Name for the new scene.
        """
        if not scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "scene_name is required")
        return await client.execute("CreateScene", sceneName=scene_name)

    @mcp.tool()
    async def remove_scene(scene_name: str) -> dict:
        """Delete a scene.

        Args:
            scene_name: Name of the scene to remove.
        """
        if not scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "scene_name is required")
        return await client.execute("RemoveScene", sceneName=scene_name)

    @mcp.tool()
    async def set_scene_name(scene_name: str, new_scene_name: str) -> dict:
        """Rename a scene.

        Args:
            scene_name: Current name of the scene.
            new_scene_name: New name.
        """
        if not scene_name or not new_scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "scene_name and new_scene_name are required")
        return await client.execute("SetSceneName", sceneName=scene_name, newSceneName=new_scene_name)

    @mcp.tool()
    async def get_scene_transition_override(scene_name: str) -> dict:
        """Get the transition overridden for a specific scene, if any.

        Args:
            scene_name: Name of the scene.
        """
        return await client.execute("GetSceneSceneTransitionOverride", sceneName=scene_name)

    @mcp.tool()
    async def set_scene_transition_override(
        scene_name: str, transition_name: str | None = None, transition_duration_ms: int | None = None,
    ) -> dict:
        """Override which transition (and/or duration) is used when switching
        INTO this specific scene, instead of the global current transition.

        Args:
            scene_name: Name of the scene.
            transition_name: Transition to use, or None to clear the override.
            transition_duration_ms: Duration override in ms (50-20000), or None to clear.
        """
        if not scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "scene_name is required")
        params = {"sceneName": scene_name, "transitionName": transition_name}
        if transition_duration_ms is not None:
            params["transitionDuration"] = transition_duration_ms
        return await client.execute("SetSceneSceneTransitionOverride", **params)
