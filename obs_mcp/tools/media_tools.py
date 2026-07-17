"""Media input tools — playback control for media sources (video files,
VLC sources): status, seek, and transport actions."""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_media_input_status(input_name: str) -> dict:
        """Playback state (playing/paused/stopped/buffering/ended/error),
        duration, and cursor position of a media source."""
        return await client.execute("GetMediaInputStatus", inputName=input_name)

    @mcp.tool()
    async def set_media_input_cursor(input_name: str, cursor_ms: int) -> dict:
        """Seek a media source to an absolute position. No bounds checking.

        Args:
            input_name: Name of the media input.
            cursor_ms: Position in milliseconds.
        """
        return await client.execute("SetMediaInputCursor", inputName=input_name, mediaCursor=cursor_ms)

    @mcp.tool()
    async def offset_media_input_cursor(input_name: str, offset_ms: int) -> dict:
        """Seek a media source relative to its current position. No bounds checking.

        Args:
            input_name: Name of the media input.
            offset_ms: Milliseconds to offset by (negative = seek backward).
        """
        return await client.execute("OffsetMediaInputCursor", inputName=input_name, mediaCursorOffset=offset_ms)

    @mcp.tool()
    async def trigger_media_input_action(input_name: str, action: str) -> dict:
        """Trigger a transport action on a media source.

        Args:
            input_name: Name of the media input.
            action: One of OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY, _PAUSE,
                _STOP, _RESTART, _NEXT, _PREVIOUS.
        """
        return await client.execute("TriggerMediaInputAction", inputName=input_name, mediaAction=action)
