"""Transition tools — list/set the current transition, duration, settings,
T-bar control, and triggering scene transitions (including studio mode)."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_transition_kind_list() -> dict:
        """List every transition kind this OBS install supports (Cut, Fade, Stinger, etc)."""
        return await client.execute("GetTransitionKindList")

    @mcp.tool()
    async def get_scene_transition_list() -> dict:
        """List every configured transition and which one is current."""
        return await client.execute("GetSceneTransitionList")

    @mcp.tool()
    async def get_current_scene_transition() -> dict:
        """Full detail on the current transition: kind, duration, whether it's
        fixed-duration, and its settings."""
        return await client.execute("GetCurrentSceneTransition")

    @mcp.tool()
    async def set_current_scene_transition(transition_name: str) -> dict:
        """Make a transition the active one for the next scene switch.

        Args:
            transition_name: Name of the transition to activate.
        """
        if not transition_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "transition_name is required")
        return await client.execute("SetCurrentSceneTransition", transitionName=transition_name)

    @mcp.tool()
    async def set_current_scene_transition_duration(duration_ms: int) -> dict:
        """Set the duration of the current transition, if it isn't fixed-duration.

        Args:
            duration_ms: Duration in milliseconds, 50-20000.
        """
        if not 50 <= duration_ms <= 20000:
            raise OBSMCPError(ErrorCode.VALUE_OUT_OF_RANGE, "duration_ms must be 50-20000")
        return await client.execute("SetCurrentSceneTransitionDuration", transitionDuration=duration_ms)

    @mcp.tool()
    async def set_current_scene_transition_settings(settings: dict, overlay: bool = True) -> dict:
        """Configure the current transition (e.g. a Stinger's video file path).

        Args:
            settings: Settings object for the transition.
            overlay: True = merge on top of current settings, False = replace.
        """
        return await client.execute("SetCurrentSceneTransitionSettings", transitionSettings=settings, overlay=overlay)

    @mcp.tool()
    async def get_current_scene_transition_cursor() -> dict:
        """Current transition progress, 0.0-1.0. Returns 1.0 when no transition is active."""
        return await client.execute("GetCurrentSceneTransitionCursor")

    @mcp.tool()
    async def trigger_studio_mode_transition() -> dict:
        """Trigger the current transition — same as clicking the Transition
        button in studio mode. Cuts Preview to Program."""
        return await client.execute("TriggerStudioModeTransition")

    @mcp.tool()
    async def set_tbar_position(position: float, release: bool = True) -> dict:
        """Set the T-bar position for manual transition scrubbing.

        Args:
            position: 0.0-1.0.
            release: Set False only if you're about to send another position
                     update immediately after this one.
        """
        if not 0.0 <= position <= 1.0:
            raise OBSMCPError(ErrorCode.VALUE_OUT_OF_RANGE, "position must be 0.0-1.0")
        return await client.execute("SetTBarPosition", position=position, release=release)
