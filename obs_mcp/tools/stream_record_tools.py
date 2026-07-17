"""Stream and record tools — the two outputs the AI will touch most:
start/stop/toggle stream and recording, captions, pause/resume, file
splitting, and chapter markers."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    # ── Stream ──────────────────────────────────────
    @mcp.tool()
    async def get_stream_status() -> dict:
        """Stream output status: active/reconnecting, timecode, duration,
        congestion, bytes sent, skipped/total frames."""
        return await client.execute("GetStreamStatus")

    @mcp.tool()
    async def toggle_stream() -> dict:
        """Toggle the stream on/off."""
        return await client.execute("ToggleStream")

    @mcp.tool()
    async def start_stream() -> dict:
        """Go live. Requires stream service settings to already be configured
        (see config_tools.set_stream_service_settings)."""
        return await client.execute("StartStream")

    @mcp.tool()
    async def stop_stream() -> dict:
        """End the stream."""
        return await client.execute("StopStream")

    @mcp.tool()
    async def send_stream_caption(caption_text: str) -> dict:
        """Send CEA-608 caption text over the live stream output.

        Args:
            caption_text: Caption text to send.
        """
        if not caption_text:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "caption_text is required")
        return await client.execute("SendStreamCaption", captionText=caption_text)

    # ── Record ──────────────────────────────────────
    @mcp.tool()
    async def get_record_status() -> dict:
        """Record output status: active, paused, timecode, duration, bytes written."""
        return await client.execute("GetRecordStatus")

    @mcp.tool()
    async def toggle_record() -> dict:
        """Toggle recording on/off."""
        return await client.execute("ToggleRecord")

    @mcp.tool()
    async def start_record() -> dict:
        """Start recording to disk (see config_tools.get/set_record_directory
        for where files land)."""
        return await client.execute("StartRecord")

    @mcp.tool()
    async def stop_record() -> dict:
        """Stop recording. Returns the saved file's path."""
        return await client.execute("StopRecord")

    @mcp.tool()
    async def toggle_record_pause() -> dict:
        """Toggle pause on the active recording."""
        return await client.execute("ToggleRecordPause")

    @mcp.tool()
    async def pause_record() -> dict:
        """Pause the active recording."""
        return await client.execute("PauseRecord")

    @mcp.tool()
    async def resume_record() -> dict:
        """Resume a paused recording."""
        return await client.execute("ResumeRecord")

    @mcp.tool()
    async def split_record_file() -> dict:
        """Split the current recording into a new file right now — useful for
        keeping individual segments a manageable size on long streams."""
        return await client.execute("SplitRecordFile")

    @mcp.tool()
    async def create_record_chapter(chapter_name: str = "") -> dict:
        """Add a chapter marker to the file currently being recorded. Only
        supported on Hybrid MP4 output as of OBS 30.2.0.

        Args:
            chapter_name: Optional name for the chapter marker.
        """
        params = {"chapterName": chapter_name} if chapter_name else {}
        return await client.execute("CreateRecordChapter", **params)
