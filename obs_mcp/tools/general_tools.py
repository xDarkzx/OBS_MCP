"""General OBS tools — version/stats, hotkeys, custom events, vendor requests."""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_version() -> dict:
        """OBS/obs-websocket version info, platform, and the full list of requests
        available on this connection (availableRequests)."""
        return await client.execute("GetVersion")

    @mcp.tool()
    async def get_stats() -> dict:
        """Live perf stats: CPU/memory usage, active FPS, render/output skipped
        frames, disk space. Use to check for dropped-frame problems mid-stream."""
        return await client.execute("GetStats")

    @mcp.tool()
    async def broadcast_custom_event(event_data: dict) -> dict:
        """Broadcast a CustomEvent to all subscribed obs-websocket clients.

        Args:
            event_data: Arbitrary JSON payload delivered to receivers.
        """
        return await client.execute("BroadcastCustomEvent", eventData=event_data)

    @mcp.tool()
    async def call_vendor_request(vendor_name: str, request_type: str, request_data: dict | None = None) -> dict:
        """Call a request registered by a third-party OBS plugin/script vendor.

        Args:
            vendor_name: Unique vendor name registered by the plugin.
            request_type: The vendor's request type to call.
            request_data: Optional payload for the vendor request.
        """
        return await client.execute(
            "CallVendorRequest",
            vendorName=vendor_name, requestType=request_type,
            requestData=request_data or {},
        )

    @mcp.tool()
    async def get_hotkey_list() -> dict:
        """List all hotkey names in OBS. Best-effort — hotkey requests are less
        reliable than dedicated requests when one exists for the same action."""
        return await client.execute("GetHotkeyList")

    @mcp.tool()
    async def trigger_hotkey_by_name(hotkey_name: str, context_name: str = "") -> dict:
        """Trigger a hotkey by its name (see get_hotkey_list).

        Args:
            hotkey_name: Name of the hotkey to trigger.
            context_name: Optional hotkey context name.
        """
        params = {"hotkeyName": hotkey_name}
        if context_name:
            params["contextName"] = context_name
        return await client.execute("TriggerHotkeyByName", **params)

    @mcp.tool()
    async def trigger_hotkey_by_key_sequence(
        key_id: str = "", shift: bool = False, control: bool = False,
        alt: bool = False, command: bool = False,
    ) -> dict:
        """Trigger a hotkey by simulating a key press + modifiers.

        Args:
            key_id: OBS key ID (see obs-studio's obs-hotkeys.h for the list).
            shift/control/alt/command: Modifier keys to hold.
        """
        params = {}
        if key_id:
            params["keyId"] = key_id
        params["keyModifiers"] = {
            "shift": shift, "control": control, "alt": alt, "command": command,
        }
        return await client.execute("TriggerHotkeyByKeySequence", **params)

    @mcp.tool()
    async def get_persistent_data(realm: str, slot_name: str) -> dict:
        """Get a value from an OBS persistent-data "slot".

        Args:
            realm: "OBS_WEBSOCKET_DATA_REALM_GLOBAL" or "OBS_WEBSOCKET_DATA_REALM_PROFILE".
            slot_name: Name of the slot to read.
        """
        return await client.execute("GetPersistentData", realm=realm, slotName=slot_name)

    @mcp.tool()
    async def set_persistent_data(realm: str, slot_name: str, slot_value) -> dict:
        """Set a value in an OBS persistent-data "slot" — useful for storing state
        the AI needs to remember across tool calls (e.g. giveaway winners).

        Args:
            realm: "OBS_WEBSOCKET_DATA_REALM_GLOBAL" or "OBS_WEBSOCKET_DATA_REALM_PROFILE".
            slot_name: Name of the slot to write.
            slot_value: Any JSON-serializable value.
        """
        return await client.execute(
            "SetPersistentData", realm=realm, slotName=slot_name, slotValue=slot_value,
        )
