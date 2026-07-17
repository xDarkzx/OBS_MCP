"""Output tools — virtual camera, replay buffer, and generic named outputs
(anything registered as an OBS output that isn't stream/record, e.g. a custom
NDI or FTL output some plugins add)."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    # ── Virtual camera ──────────────────────────────────────
    @mcp.tool()
    async def get_virtual_cam_status() -> dict:
        """Whether the virtual camera output is active."""
        return await client.execute("GetVirtualCamStatus")

    @mcp.tool()
    async def toggle_virtual_cam() -> dict:
        """Toggle the virtual camera on/off."""
        return await client.execute("ToggleVirtualCam")

    @mcp.tool()
    async def start_virtual_cam() -> dict:
        """Start the virtual camera."""
        return await client.execute("StartVirtualCam")

    @mcp.tool()
    async def stop_virtual_cam() -> dict:
        """Stop the virtual camera."""
        return await client.execute("StopVirtualCam")

    # ── Replay buffer ──────────────────────────────────────
    @mcp.tool()
    async def get_replay_buffer_status() -> dict:
        """Whether the replay buffer is active."""
        return await client.execute("GetReplayBufferStatus")

    @mcp.tool()
    async def toggle_replay_buffer() -> dict:
        """Toggle the replay buffer on/off."""
        return await client.execute("ToggleReplayBuffer")

    @mcp.tool()
    async def start_replay_buffer() -> dict:
        """Start the replay buffer."""
        return await client.execute("StartReplayBuffer")

    @mcp.tool()
    async def stop_replay_buffer() -> dict:
        """Stop the replay buffer."""
        return await client.execute("StopReplayBuffer")

    @mcp.tool()
    async def save_replay_buffer() -> dict:
        """Save the last N seconds from the replay buffer to disk — the "instant
        replay" clip-save action."""
        return await client.execute("SaveReplayBuffer")

    @mcp.tool()
    async def get_last_replay_buffer_replay() -> dict:
        """File path of the last replay buffer save."""
        return await client.execute("GetLastReplayBufferReplay")

    # ── Generic outputs ──────────────────────────────────────
    @mcp.tool()
    async def get_output_list() -> dict:
        """List every registered OBS output (stream, record, virtualcam,
        replay buffer, and any plugin-added outputs)."""
        return await client.execute("GetOutputList")

    @mcp.tool()
    async def get_output_status(output_name: str) -> dict:
        """Detailed status of a named output: active/reconnecting, timecode,
        duration, congestion, bytes sent, frame counts."""
        if not output_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "output_name is required")
        return await client.execute("GetOutputStatus", outputName=output_name)

    @mcp.tool()
    async def toggle_output(output_name: str) -> dict:
        """Toggle a named output on/off."""
        return await client.execute("ToggleOutput", outputName=output_name)

    @mcp.tool()
    async def start_output(output_name: str) -> dict:
        """Start a named output."""
        return await client.execute("StartOutput", outputName=output_name)

    @mcp.tool()
    async def stop_output(output_name: str) -> dict:
        """Stop a named output."""
        return await client.execute("StopOutput", outputName=output_name)

    @mcp.tool()
    async def get_output_settings(output_name: str) -> dict:
        """Get a named output's settings object."""
        return await client.execute("GetOutputSettings", outputName=output_name)

    @mcp.tool()
    async def set_output_settings(output_name: str, settings: dict) -> dict:
        """Set a named output's settings object."""
        return await client.execute("SetOutputSettings", outputName=output_name, outputSettings=settings)
