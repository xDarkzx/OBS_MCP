"""Scene item tools — the sources placed WITHIN a scene: transform (position/
scale/crop), enabled/locked state, z-order index, blend mode, and lookups."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_scene_item_list(scene_name: str) -> dict:
        """List every scene item (placed source) in a scene."""
        return await client.execute("GetSceneItemList", sceneName=scene_name)

    @mcp.tool()
    async def get_group_scene_item_list(group_name: str) -> dict:
        """Like get_scene_item_list, but for a group (OBS groups are broken
        under the hood — prefer nested scenes over groups where possible)."""
        return await client.execute("GetGroupSceneItemList", sceneName=group_name)

    @mcp.tool()
    async def get_scene_item_id(scene_name: str, source_name: str, search_offset: int = 0) -> dict:
        """Find a scene item's numeric ID by the source name it references.

        Args:
            scene_name: Scene or group to search.
            source_name: Name of the source to find.
            search_offset: Matches to skip. -1 = last (topmost) match.
        """
        return await client.execute(
            "GetSceneItemId", sceneName=scene_name, sourceName=source_name, searchOffset=search_offset,
        )

    @mcp.tool()
    async def get_scene_item_source(scene_name: str, scene_item_id: int) -> dict:
        """Get the source name/UUID a scene item references."""
        return await client.execute("GetSceneItemSource", sceneName=scene_name, sceneItemId=scene_item_id)

    @mcp.tool()
    async def create_scene_item(scene_name: str, source_name: str, scene_item_enabled: bool = True) -> dict:
        """Add an existing source to a scene as a new scene item.

        Args:
            scene_name: Scene to add the item to.
            source_name: Existing source (input) to place.
            scene_item_enabled: Whether it starts visible.
        """
        return await client.execute(
            "CreateSceneItem", sceneName=scene_name, sourceName=source_name, sceneItemEnabled=scene_item_enabled,
        )

    @mcp.tool()
    async def remove_scene_item(scene_name: str, scene_item_id: int) -> dict:
        """Remove a scene item from a scene (does not delete the underlying source)."""
        if scene_item_id < 0:
            raise OBSMCPError(ErrorCode.VALUE_OUT_OF_RANGE, "scene_item_id must be >= 0")
        return await client.execute("RemoveSceneItem", sceneName=scene_name, sceneItemId=scene_item_id)

    @mcp.tool()
    async def duplicate_scene_item(scene_name: str, scene_item_id: int, destination_scene_name: str = "") -> dict:
        """Duplicate a scene item, copying its transform/crop, optionally into
        a different scene.

        Args:
            scene_name: Scene the item is currently in.
            scene_item_id: Numeric ID of the item to duplicate.
            destination_scene_name: Target scene; defaults to the source scene.
        """
        params = {"sceneName": scene_name, "sceneItemId": scene_item_id}
        if destination_scene_name:
            params["destinationSceneName"] = destination_scene_name
        return await client.execute("DuplicateSceneItem", **params)

    @mcp.tool()
    async def get_scene_item_transform(scene_name: str, scene_item_id: int) -> dict:
        """Get a scene item's position, scale, rotation, and crop."""
        return await client.execute("GetSceneItemTransform", sceneName=scene_name, sceneItemId=scene_item_id)

    @mcp.tool()
    async def set_scene_item_transform(scene_name: str, scene_item_id: int, transform: dict) -> dict:
        """Set a scene item's position/scale/rotation/crop.

        Args:
            scene_name: Scene the item is in.
            scene_item_id: Numeric ID of the item.
            transform: Object with any of positionX/positionY, rotation,
                scaleX/scaleY, alignment, boundsType/boundsAlignment/
                boundsWidth/boundsHeight, cropLeft/Right/Top/Bottom.
        """
        return await client.execute(
            "SetSceneItemTransform", sceneName=scene_name, sceneItemId=scene_item_id, sceneItemTransform=transform,
        )

    @mcp.tool()
    async def get_scene_item_enabled(scene_name: str, scene_item_id: int) -> dict:
        """Get whether a scene item is currently visible (shown/hidden, not mute)."""
        return await client.execute("GetSceneItemEnabled", sceneName=scene_name, sceneItemId=scene_item_id)

    @mcp.tool()
    async def set_scene_item_enabled(scene_name: str, scene_item_id: int, enabled: bool) -> dict:
        """Show or hide a scene item.

        Args:
            scene_name: Scene the item is in.
            scene_item_id: Numeric ID of the item.
            enabled: True = visible, False = hidden.
        """
        return await client.execute("SetSceneItemEnabled", sceneName=scene_name, sceneItemId=scene_item_id, sceneItemEnabled=enabled)

    @mcp.tool()
    async def get_scene_item_locked(scene_name: str, scene_item_id: int) -> dict:
        """Get a scene item's lock state (locked items can't be moved/resized in the UI)."""
        return await client.execute("GetSceneItemLocked", sceneName=scene_name, sceneItemId=scene_item_id)

    @mcp.tool()
    async def set_scene_item_locked(scene_name: str, scene_item_id: int, locked: bool) -> dict:
        """Lock or unlock a scene item."""
        return await client.execute("SetSceneItemLocked", sceneName=scene_name, sceneItemId=scene_item_id, sceneItemLocked=locked)

    @mcp.tool()
    async def get_scene_item_index(scene_name: str, scene_item_id: int) -> dict:
        """Get a scene item's stacking position (0 = bottom of the source list)."""
        return await client.execute("GetSceneItemIndex", sceneName=scene_name, sceneItemId=scene_item_id)

    @mcp.tool()
    async def set_scene_item_index(scene_name: str, scene_item_id: int, index: int) -> dict:
        """Reorder a scene item's stacking position (z-order).

        Args:
            scene_name: Scene the item is in.
            scene_item_id: Numeric ID of the item.
            index: New position, >= 0 (0 = bottom of the source list).
        """
        if index < 0:
            raise OBSMCPError(ErrorCode.VALUE_OUT_OF_RANGE, "index must be >= 0")
        return await client.execute("SetSceneItemIndex", sceneName=scene_name, sceneItemId=scene_item_id, sceneItemIndex=index)

    @mcp.tool()
    async def get_scene_item_blend_mode(scene_name: str, scene_item_id: int) -> dict:
        """Get a scene item's blend mode."""
        return await client.execute("GetSceneItemBlendMode", sceneName=scene_name, sceneItemId=scene_item_id)

    @mcp.tool()
    async def set_scene_item_blend_mode(scene_name: str, scene_item_id: int, blend_mode: str) -> dict:
        """Set a scene item's blend mode.

        Args:
            scene_name: Scene the item is in.
            scene_item_id: Numeric ID of the item.
            blend_mode: One of OBS_BLEND_NORMAL, _ADDITIVE, _SUBTRACT, _SCREEN,
                _MULTIPLY, _LIGHTEN, _DARKEN.
        """
        return await client.execute("SetSceneItemBlendMode", sceneName=scene_name, sceneItemId=scene_item_id, sceneItemBlendMode=blend_mode)
