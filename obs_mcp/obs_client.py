"""Async wrapper around obsws-python's synchronous ReqClient.

obsws-python's ReqClient blocks on the underlying WebSocket call; every
request here runs in a thread-pool executor so FastMCP's async tool
functions never block the event loop on OBS round-trips.
"""

import asyncio
import logging
import os

import obsws_python as obsws
from obsws_python.error import OBSSDKRequestError

from obs_mcp.error_codes import ErrorCode, OBSMCPError

logger = logging.getLogger(__name__)


class OBSClient:
    def __init__(self):
        self._client: obsws.ReqClient | None = None
        self._lock = asyncio.Lock()

    def _connect_sync(self) -> obsws.ReqClient:
        host = os.environ.get("OBS_HOST", "localhost")
        port = int(os.environ.get("OBS_PORT", "4455"))
        password = os.environ.get("OBS_PASSWORD", "")
        try:
            return obsws.ReqClient(host=host, port=port, password=password, timeout=5)
        except Exception as e:
            raise OBSMCPError(
                ErrorCode.CONNECTION_FAILED,
                f"Could not connect to OBS at {host}:{port} — {e}. "
                f"Make sure OBS Studio is running with the WebSocket server "
                f"enabled (Tools > WebSocket Server Settings) and that "
                f"OBS_HOST/OBS_PORT/OBS_PASSWORD match its settings.",
            )

    async def _ensure_connected_locked(self) -> obsws.ReqClient:
        """Must be called with self._lock already held."""
        if self._client is None:
            loop = asyncio.get_running_loop()
            self._client = await loop.run_in_executor(None, self._connect_sync)
        return self._client

    async def execute(self, request_type: str, **data) -> dict:
        """Call any obs-websocket v5 request by name. Returns response fields as a dict.

        obsws-python's req() does a bare send() then recv() with no request-ID
        matching, so it isn't safe to call from two threads at once — a second
        concurrent request can steal the first request's response off the
        socket. Serialize every call (connect included) through one lock so
        concurrent tool calls queue instead of racing.
        """
        loop = asyncio.get_running_loop()
        async with self._lock:
            client = await self._ensure_connected_locked()
            try:
                result = await loop.run_in_executor(
                    None, lambda: client.send(request_type, data if data else None, raw=True)
                )
            except OBSSDKRequestError as e:
                # OBS replied — the request was just invalid (bad scene name,
                # out-of-range value, etc). The socket is still healthy, so
                # don't force a reconnect for something that isn't a
                # connection problem; the AI will hit this routinely while
                # exploring scene/source names.
                raise OBSMCPError(
                    ErrorCode.REQUEST_FAILED,
                    f"OBS request '{request_type}' failed: {e}",
                )
            except Exception as e:
                # No reply came back at all — the connection itself is dead.
                # Reset so the next call reconnects instead of failing forever.
                self._client = None
                raise OBSMCPError(
                    ErrorCode.REQUEST_FAILED,
                    f"OBS request '{request_type}' failed: {e}",
                )
        if result is None:
            return {}
        return result if isinstance(result, dict) else result.__dict__

    async def close(self):
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:
                pass
            self._client = None
