"""Tests for pipeline_tools.clean_audio_input's composition logic — chain
order, skip-if-exists behavior, and RNNoise-vs-legacy filter kind selection.

Uses a fake mcp/client double instead of a live OBS connection: `register()`
is called against a stand-in `mcp` object whose `.tool()` decorator just
captures the function, with `obs_mcp.main.client` monkeypatched to a fake
async client that records every call it receives.
"""

import pytest

import obs_mcp.main as main_module
from obs_mcp.tools import pipeline_tools


class FakeMCP:
    """Captures @mcp.tool()-decorated functions by name instead of registering
    them with a real FastMCP server."""

    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorator


class FakeOBSClient:
    def __init__(self, existing_filters=None, available_filter_kinds=None):
        self.calls = []
        self._existing_filters = existing_filters or []
        self._available_kinds = available_filter_kinds or [
            "noise_gate_filter", "noise_suppress_filter_v2", "compressor_filter",
        ]

    async def execute(self, request_type, **data):
        self.calls.append((request_type, data))
        if request_type == "GetSourceFilterList":
            return {"filters": self._existing_filters}
        if request_type == "GetSourceFilterKindList":
            return {"sourceFilterKinds": self._available_kinds}
        return {}


@pytest.fixture
def fake_client(monkeypatch):
    client = FakeOBSClient()
    monkeypatch.setattr(main_module, "client", client)
    return client


@pytest.fixture
def clean_audio_input(fake_client):
    mcp = FakeMCP()
    pipeline_tools.register(mcp)
    return mcp.tools["clean_audio_input"], fake_client


class TestCleanAudioInputChainOrder:
    @pytest.mark.asyncio
    async def test_creates_all_three_stages_in_gate_suppress_compressor_order(self, clean_audio_input):
        tool, client = clean_audio_input
        await tool(input_name="Mic/Aux")

        create_calls = [c for c in client.calls if c[0] == "CreateSourceFilter"]
        assert len(create_calls) == 3
        kinds_in_order = [c[1]["filterKind"] for c in create_calls]
        assert kinds_in_order == ["noise_gate_filter", "noise_suppress_filter_v2", "compressor_filter"]

    @pytest.mark.asyncio
    async def test_result_reports_all_three_created(self, clean_audio_input):
        tool, _ = clean_audio_input
        result = await tool(input_name="Mic/Aux")
        assert set(result["filters_created"]) == {
            "noise_gate_filter", "noise_suppress_filter_v2", "compressor_filter",
        }
        assert result["filters_skipped_already_present"] == []


class TestCleanAudioInputSkipsExisting:
    @pytest.mark.asyncio
    async def test_skips_gate_already_present(self, monkeypatch):
        client = FakeOBSClient(existing_filters=[{"filterKind": "noise_gate_filter"}])
        monkeypatch.setattr(main_module, "client", client)
        mcp = FakeMCP()
        pipeline_tools.register(mcp)

        result = await mcp.tools["clean_audio_input"](input_name="Mic/Aux")

        assert "noise_gate_filter" not in result["filters_created"]
        assert "noise_gate_filter" in result["filters_skipped_already_present"]
        # The other two stages still get created.
        assert "compressor_filter" in result["filters_created"]

    @pytest.mark.asyncio
    async def test_no_filters_created_when_all_already_present(self, monkeypatch):
        client = FakeOBSClient(existing_filters=[
            {"filterKind": "noise_gate_filter"},
            {"filterKind": "noise_suppress_filter_v2"},
            {"filterKind": "compressor_filter"},
        ])
        monkeypatch.setattr(main_module, "client", client)
        mcp = FakeMCP()
        pipeline_tools.register(mcp)

        result = await mcp.tools["clean_audio_input"](input_name="Mic/Aux")

        assert result["filters_created"] == []
        assert len(result["filters_skipped_already_present"]) == 3
        assert not any(c[0] == "CreateSourceFilter" for c in client.calls)


class TestCleanAudioInputSuppressKindSelection:
    @pytest.mark.asyncio
    async def test_prefers_v2_rnnoise_when_available(self, monkeypatch):
        client = FakeOBSClient(available_filter_kinds=[
            "noise_gate_filter", "noise_suppress_filter", "noise_suppress_filter_v2", "compressor_filter",
        ])
        monkeypatch.setattr(main_module, "client", client)
        mcp = FakeMCP()
        pipeline_tools.register(mcp)

        result = await mcp.tools["clean_audio_input"](input_name="Mic/Aux")

        assert "noise_suppress_filter_v2" in result["filters_created"]

    @pytest.mark.asyncio
    async def test_falls_back_to_v1_when_v2_not_registered(self, monkeypatch):
        """Some OBS builds/platforms don't register the RNNoise-based v2 kind —
        assuming it's always available would silently break the pipeline there."""
        client = FakeOBSClient(available_filter_kinds=[
            "noise_gate_filter", "noise_suppress_filter", "compressor_filter",
        ])
        monkeypatch.setattr(main_module, "client", client)
        mcp = FakeMCP()
        pipeline_tools.register(mcp)

        result = await mcp.tools["clean_audio_input"](input_name="Mic/Aux")

        assert "noise_suppress_filter" in result["filters_created"]
        assert "noise_suppress_filter_v2" not in result["filters_created"]


class TestCleanAudioInputValidation:
    @pytest.mark.asyncio
    async def test_missing_input_name_raises(self, clean_audio_input):
        tool, _ = clean_audio_input
        with pytest.raises(Exception):
            await tool(input_name="")

    @pytest.mark.asyncio
    async def test_stage_can_be_individually_disabled(self, clean_audio_input):
        tool, client = clean_audio_input
        result = await tool(input_name="Mic/Aux", compressor=False)
        assert "compressor_filter" not in result["filters_created"]
        create_calls = [c for c in client.calls if c[0] == "CreateSourceFilter"]
        assert len(create_calls) == 2
