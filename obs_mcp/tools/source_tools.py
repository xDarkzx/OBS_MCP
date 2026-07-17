"""Source tools — active-state check and screenshots. Works for both inputs and scenes."""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def get_source_active(source_name: str) -> dict:
        """Check whether a source (input or scene) is currently showing in
        Program (videoActive) and/or visible anywhere in the UI (videoShowing).

        Args:
            source_name: Name of the input or scene.
        """
        return await client.execute("GetSourceActive", sourceName=source_name)

    @mcp.tool()
    async def get_source_screenshot(
        source_name: str, image_format: str = "png",
        image_width: int | None = None, image_height: int | None = None,
        image_compression_quality: int = -1,
    ) -> dict:
        """Get a Base64-encoded screenshot of a source (input or scene) — use
        this to actually SEE what's on stream. Check get_version's
        supportedImageFormats for valid image_format values on this OBS build.

        Args:
            source_name: Name of the input or scene to capture.
            image_format: e.g. "png", "jpg".
            image_width/image_height: Optional scale-to-fit dimensions (8-4096).
                Omit to use the source's native resolution.
            image_compression_quality: 0 (max compression) to 100 (uncompressed),
                -1 for format default.
        """
        if not source_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "source_name is required")
        params = {"sourceName": source_name, "imageFormat": image_format,
                  "imageCompressionQuality": image_compression_quality}
        if image_width is not None:
            params["imageWidth"] = image_width
        if image_height is not None:
            params["imageHeight"] = image_height
        return await client.execute("GetSourceScreenshot", **params)

    @mcp.tool()
    async def save_source_screenshot(
        source_name: str, image_file_path: str, image_format: str = "png",
        image_width: int | None = None, image_height: int | None = None,
        image_compression_quality: int = -1,
    ) -> dict:
        """Save a screenshot of a source (input or scene) directly to disk.

        Args:
            source_name: Name of the input or scene to capture.
            image_file_path: Absolute path to save to, e.g. C:/renders/shot.png.
            image_format: e.g. "png", "jpg".
            image_width/image_height: Optional scale-to-fit dimensions (8-4096).
            image_compression_quality: 0 (max compression) to 100 (uncompressed),
                -1 for format default.
        """
        if not source_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "source_name is required")
        if not image_file_path:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "image_file_path is required")
        params = {"sourceName": source_name, "imageFormat": image_format,
                  "imageFilePath": image_file_path, "imageCompressionQuality": image_compression_quality}
        if image_width is not None:
            params["imageWidth"] = image_width
        if image_height is not None:
            params["imageHeight"] = image_height
        return await client.execute("SaveSourceScreenshot", **params)
