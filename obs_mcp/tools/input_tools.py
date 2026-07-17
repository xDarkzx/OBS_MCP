"""Input tools — create/list/rename inputs, settings, and the full audio mixer
surface (mute, volume, balance, sync offset, monitor type, audio tracks,
deinterlace). This is the deepest audio-control layer available."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_input_list(input_kind: str = "") -> dict:
        """List all inputs (sources like mic, capture card, browser source, etc).

        Args:
            input_kind: Optional — restrict to one kind (see get_input_kind_list).
        """
        params = {"inputKind": input_kind} if input_kind else {}
        return await client.execute("GetInputList", **params)

    @mcp.tool()
    async def get_input_kind_list(unversioned: bool = False) -> dict:
        """List every input kind (source type) this OBS install can create."""
        return await client.execute("GetInputKindList", unversioned=unversioned)

    @mcp.tool()
    async def get_special_inputs() -> dict:
        """Names of the built-in special audio inputs: Desktop Audio 1/2,
        Mic/Aux 1-4. Use these names to control the default audio channels."""
        return await client.execute("GetSpecialInputs")

    @mcp.tool()
    async def create_input(
        input_name: str, input_kind: str, scene_name: str = "",
        input_settings: dict | None = None, scene_item_enabled: bool = True,
    ) -> dict:
        """Create a new input and add it as a scene item to a scene.

        Args:
            input_name: Name for the new input.
            input_kind: Kind of input to create (see get_input_kind_list).
            scene_name: Scene to add it to.
            input_settings: Optional initial settings object.
            scene_item_enabled: Whether the new scene item starts visible.
        """
        if not input_name or not input_kind or not scene_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "input_name, input_kind, and scene_name are required")
        return await client.execute(
            "CreateInput", inputName=input_name, inputKind=input_kind, sceneName=scene_name,
            inputSettings=input_settings or {}, sceneItemEnabled=scene_item_enabled,
        )

    @mcp.tool()
    async def remove_input(input_name: str) -> dict:
        """Delete an input. Removes all its scene items too.

        Args:
            input_name: Name of the input to remove.
        """
        if not input_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "input_name is required")
        return await client.execute("RemoveInput", inputName=input_name)

    @mcp.tool()
    async def set_input_name(input_name: str, new_input_name: str) -> dict:
        """Rename an input.

        Args:
            input_name: Current name.
            new_input_name: New name.
        """
        if not input_name or not new_input_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "input_name and new_input_name are required")
        return await client.execute("SetInputName", inputName=input_name, newInputName=new_input_name)

    @mcp.tool()
    async def get_input_default_settings(input_kind: str) -> dict:
        """Default settings object for an input kind — overlay get_input_settings
        on top of this to reconstruct the full effective settings."""
        return await client.execute("GetInputDefaultSettings", inputKind=input_kind)

    @mcp.tool()
    async def get_input_settings(input_name: str) -> dict:
        """Current (non-default) settings of an input, plus its kind.

        Args:
            input_name: Name of the input.
        """
        return await client.execute("GetInputSettings", inputName=input_name)

    @mcp.tool()
    async def set_input_settings(input_name: str, input_settings: dict, overlay: bool = True) -> dict:
        """Set an input's settings.

        Args:
            input_name: Name of the input.
            input_settings: Settings object to apply.
            overlay: True = merge on top of current settings, False = reset to
                     defaults first then apply.
        """
        if not input_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "input_name is required")
        return await client.execute(
            "SetInputSettings", inputName=input_name, inputSettings=input_settings, overlay=overlay,
        )

    # ── Audio mixer ──────────────────────────────────────
    @mcp.tool()
    async def get_input_mute(input_name: str) -> dict:
        """Get an input's mute state."""
        return await client.execute("GetInputMute", inputName=input_name)

    @mcp.tool()
    async def set_input_mute(input_name: str, input_muted: bool) -> dict:
        """Mute or unmute an input."""
        if not input_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "input_name is required")
        return await client.execute("SetInputMute", inputName=input_name, inputMuted=input_muted)

    @mcp.tool()
    async def toggle_input_mute(input_name: str) -> dict:
        """Toggle an input's mute state."""
        return await client.execute("ToggleInputMute", inputName=input_name)

    @mcp.tool()
    async def get_input_volume(input_name: str) -> dict:
        """Get an input's volume as both a linear multiplier and dB."""
        return await client.execute("GetInputVolume", inputName=input_name)

    @mcp.tool()
    async def set_input_volume(input_name: str, volume_db: float | None = None, volume_mul: float | None = None) -> dict:
        """Set an input's volume — pass exactly one of volume_db or volume_mul.

        Args:
            input_name: Name of the input.
            volume_db: Volume in dB, range -100..26.
            volume_mul: Volume as a linear multiplier, range 0..20.
        """
        if not input_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "input_name is required")
        if volume_db is None and volume_mul is None:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "one of volume_db or volume_mul is required")
        params = {"inputName": input_name}
        if volume_db is not None:
            params["inputVolumeDb"] = volume_db
        if volume_mul is not None:
            params["inputVolumeMul"] = volume_mul
        return await client.execute("SetInputVolume", **params)

    @mcp.tool()
    async def get_input_audio_balance(input_name: str) -> dict:
        """Get an input's stereo balance (0.0 full left .. 1.0 full right, 0.5 center)."""
        return await client.execute("GetInputAudioBalance", inputName=input_name)

    @mcp.tool()
    async def set_input_audio_balance(input_name: str, balance: float) -> dict:
        """Set an input's stereo balance.

        Args:
            input_name: Name of the input.
            balance: 0.0 (full left) to 1.0 (full right), 0.5 = center.
        """
        if not 0.0 <= balance <= 1.0:
            raise OBSMCPError(ErrorCode.VALUE_OUT_OF_RANGE, "balance must be 0.0-1.0")
        return await client.execute("SetInputAudioBalance", inputName=input_name, inputAudioBalance=balance)

    @mcp.tool()
    async def get_input_audio_sync_offset(input_name: str) -> dict:
        """Get an input's audio sync offset in milliseconds (can be negative)."""
        return await client.execute("GetInputAudioSyncOffset", inputName=input_name)

    @mcp.tool()
    async def set_input_audio_sync_offset(input_name: str, offset_ms: float) -> dict:
        """Set an input's audio sync offset — use to fix audio/video drift.

        Args:
            input_name: Name of the input.
            offset_ms: Offset in milliseconds, range -950..20000.
        """
        if not -950 <= offset_ms <= 20000:
            raise OBSMCPError(ErrorCode.VALUE_OUT_OF_RANGE, "offset_ms must be -950..20000")
        return await client.execute("SetInputAudioSyncOffset", inputName=input_name, inputAudioSyncOffset=offset_ms)

    @mcp.tool()
    async def get_input_audio_monitor_type(input_name: str) -> dict:
        """Get an input's monitoring mode (none / monitor-only / monitor-and-output)."""
        return await client.execute("GetInputAudioMonitorType", inputName=input_name)

    @mcp.tool()
    async def set_input_audio_monitor_type(input_name: str, monitor_type: str) -> dict:
        """Set an input's monitoring mode.

        Args:
            input_name: Name of the input.
            monitor_type: One of OBS_MONITORING_TYPE_NONE,
                OBS_MONITORING_TYPE_MONITOR_ONLY, OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT.
        """
        return await client.execute("SetInputAudioMonitorType", inputName=input_name, monitorType=monitor_type)

    @mcp.tool()
    async def get_input_audio_tracks(input_name: str) -> dict:
        """Get which of the 6 audio mixer tracks this input is routed to."""
        return await client.execute("GetInputAudioTracks", inputName=input_name)

    @mcp.tool()
    async def set_input_audio_tracks(input_name: str, audio_tracks: dict) -> dict:
        """Set which audio mixer tracks an input is routed to.

        Args:
            input_name: Name of the input.
            audio_tracks: Object like {"1": true, "2": false, ...} for tracks 1-6.
        """
        return await client.execute("SetInputAudioTracks", inputName=input_name, inputAudioTracks=audio_tracks)

    # ── Deinterlace (async/capture inputs only) ──────────────────────────────────────
    @mcp.tool()
    async def get_input_deinterlace_mode(input_name: str) -> dict:
        """Get an input's deinterlace mode. Async inputs only (capture cards, etc)."""
        return await client.execute("GetInputDeinterlaceMode", inputName=input_name)

    @mcp.tool()
    async def set_input_deinterlace_mode(input_name: str, mode: str) -> dict:
        """Set an input's deinterlace mode.

        Args:
            input_name: Name of the input.
            mode: One of OBS_DEINTERLACE_MODE_DISABLE, _DISCARD, _RETRO, _BLEND,
                _BLEND_2X, _LINEAR, _LINEAR_2X, _YADIF, _YADIF_2X.
        """
        return await client.execute("SetInputDeinterlaceMode", inputName=input_name, inputDeinterlaceMode=mode)

    @mcp.tool()
    async def get_input_deinterlace_field_order(input_name: str) -> dict:
        """Get an input's deinterlace field order. Async inputs only."""
        return await client.execute("GetInputDeinterlaceFieldOrder", inputName=input_name)

    @mcp.tool()
    async def set_input_deinterlace_field_order(input_name: str, field_order: str) -> dict:
        """Set an input's deinterlace field order.

        Args:
            input_name: Name of the input.
            field_order: OBS_DEINTERLACE_FIELD_ORDER_TOP or _BOTTOM.
        """
        return await client.execute("SetInputDeinterlaceFieldOrder", inputName=input_name, inputDeinterlaceFieldOrder=field_order)

    # ── Dynamic properties (e.g. display-capture's monitor list) ──────────────────────────────────────
    @mcp.tool()
    async def get_input_properties_list_property_items(input_name: str, property_name: str) -> dict:
        """Get the items of a dynamic list property on an input — e.g. the
        available displays for a display-capture source.

        Args:
            input_name: Name of the input.
            property_name: Name of the list property.
        """
        return await client.execute("GetInputPropertiesListPropertyItems", inputName=input_name, propertyName=property_name)

    @mcp.tool()
    async def press_input_properties_button(input_name: str, property_name: str) -> dict:
        """Press a button in an input's properties — e.g. "refreshnocache" to
        reload a browser source.

        Args:
            input_name: Name of the input.
            property_name: Name of the button property to press.
        """
        return await client.execute("PressInputPropertiesButton", inputName=input_name, propertyName=property_name)
