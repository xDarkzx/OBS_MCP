"""Pipeline tools — one-call, multi-filter setups. Raw filter CRUD lives in
filter_tools.py; these compose it into the actual outcome a streamer wants
("clean audio") instead of making the AI hand-assemble a filter chain and
guess at parameter names and ordering every time.
"""

from mcp.server.fastmcp import FastMCP

from obs_mcp.error_codes import ErrorCode, OBSMCPError

# Filter settings keys verified against OBS's actual C source
# (plugins/obs-filters/{noise-gate,noise-suppress,compressor}-filter.c) —
# not guessed. Order matters: gate first (cuts silence/room noise between
# words), then suppression (reduces steady background hiss/hum while
# talking), then compressor last (evens out speaking volume on what's left).
_GATE_DEFAULTS = {"open_threshold": -26.0, "close_threshold": -32.0,
                   "attack_time": 25, "hold_time": 200, "release_time": 150}
_COMPRESSOR_DEFAULTS = {"ratio": 3.0, "threshold": -18.0, "attack_time": 6,
                         "release_time": 60, "output_gain": 4.0}


def register(mcp: FastMCP):
    from obs_mcp.main import client

    @mcp.tool()
    async def clean_audio_input(
        input_name: str,
        gate: bool = True, suppression: bool = True, compressor: bool = True,
        gate_open_threshold_db: float = -26.0, gate_close_threshold_db: float = -32.0,
        suppression_method: str = "rnnoise",
        compressor_ratio: float = 3.0, compressor_threshold_db: float = -18.0,
    ) -> dict:
        """Set up a standard mic-cleanup filter chain in one call: Noise Gate
        -> Noise Suppression -> Compressor, in that order (order matters —
        gate first cuts room noise between words, suppression reduces steady
        background hiss while you're talking, compressor evens out what's left).

        Skips any filter kind that already exists on the input by that name
        instead of duplicating it. Removing a stage later is a normal
        remove_source_filter call — this only handles the one-shot setup.

        Args:
            input_name: Name of the mic/audio input to clean up.
            gate/suppression/compressor: Which stages to add (all on by default).
            gate_open_threshold_db: Gate opens above this level. Should sit
                slightly below your voice level. Default -26 dB.
            gate_close_threshold_db: Gate closes below this level. Should sit
                above the room's noise floor, 5-8 dB below open threshold.
                Default -32 dB.
            suppression_method: "rnnoise" (better quality, default) or "speex"
                (lighter weight, older).
            compressor_ratio: Compression ratio, 1.0-32.0. Default 3.0 (gentle).
            compressor_threshold_db: Level compression kicks in at, -60..0 dB.
                Default -18 dB.
        """
        if not input_name:
            raise OBSMCPError(ErrorCode.MISSING_PARAMETER, "input_name is required")

        existing = await client.execute("GetSourceFilterList", sourceName=input_name)
        existing_kinds = {f.get("filterKind") for f in existing.get("filters", [])}
        name_by_kind = {f.get("filterKind"): f.get("filterName") for f in existing.get("filters", [])}

        # Which noise-suppress filter kind this OBS build actually registers
        # varies (v2/RNNoise isn't available on every platform) — ask instead
        # of assuming, so this doesn't silently fail on older/limited builds.
        available_kinds = set((await client.execute("GetSourceFilterKindList")).get("sourceFilterKinds", []))
        suppress_kind = "noise_suppress_filter_v2" if "noise_suppress_filter_v2" in available_kinds else "noise_suppress_filter"

        created = []
        skipped = []
        stage_names = []  # filterName of each enabled stage, in gate/suppress/compressor order

        if gate:
            if "noise_gate_filter" in existing_kinds:
                skipped.append("noise_gate_filter")
                stage_names.append(name_by_kind["noise_gate_filter"])
            else:
                settings = dict(_GATE_DEFAULTS)
                settings["open_threshold"] = gate_open_threshold_db
                settings["close_threshold"] = gate_close_threshold_db
                await client.execute(
                    "CreateSourceFilter", sourceName=input_name, filterName="Noise Gate",
                    filterKind="noise_gate_filter", filterSettings=settings,
                )
                created.append("noise_gate_filter")
                stage_names.append("Noise Gate")

        if suppression:
            if "noise_suppress_filter" in existing_kinds or "noise_suppress_filter_v2" in existing_kinds:
                skipped.append(suppress_kind)
                existing_suppress_kind = "noise_suppress_filter_v2" if "noise_suppress_filter_v2" in existing_kinds else "noise_suppress_filter"
                stage_names.append(name_by_kind[existing_suppress_kind])
            else:
                settings = {"method": suppression_method}
                if suppression_method == "speex":
                    settings["suppress_level"] = -30
                await client.execute(
                    "CreateSourceFilter", sourceName=input_name, filterName="Noise Suppression",
                    filterKind=suppress_kind, filterSettings=settings,
                )
                created.append(suppress_kind)
                stage_names.append("Noise Suppression")

        if compressor:
            if "compressor_filter" in existing_kinds:
                skipped.append("compressor_filter")
                stage_names.append(name_by_kind["compressor_filter"])
            else:
                settings = dict(_COMPRESSOR_DEFAULTS)
                settings["ratio"] = compressor_ratio
                settings["threshold"] = compressor_threshold_db
                await client.execute(
                    "CreateSourceFilter", sourceName=input_name, filterName="Compressor",
                    filterKind="compressor_filter", filterSettings=settings,
                )
                created.append("compressor_filter")
                stage_names.append("Compressor")

        # A newly created stage always lands at the END of the chain, and a
        # pre-existing stage (found via existing_kinds above) could be
        # anywhere — so without this, running clean_audio_input on an input
        # that already has e.g. a Compressor would append Gate AFTER it,
        # inverting the whole point of gate-first ordering. Move the managed
        # stages to sit adjacent, in the correct relative order, anchored at
        # the earliest position any of them currently occupies (so filters
        # that were already before all three stay before them).
        if len(stage_names) > 1:
            current = await client.execute("GetSourceFilterList", sourceName=input_name)
            index_by_name = {f["filterName"]: f["filterIndex"] for f in current.get("filters", [])}
            anchor = min(index_by_name[name] for name in stage_names)
            # Each move shifts every filter after it, which invalidates the
            # rest of index_by_name — so this can't skip a stage just
            # because its pre-move index happened to match its target; only
            # unconditionally re-issuing every move keeps positions correct
            # after earlier moves in this same loop have already shuffled
            # the chain.
            for offset, name in enumerate(stage_names):
                await client.execute(
                    "SetSourceFilterIndex", sourceName=input_name, filterName=name, filterIndex=anchor + offset,
                )

        return {
            "input_name": input_name,
            "filters_created": created,
            "filters_skipped_already_present": skipped,
            "hint": (
                "Chain order is Gate -> Suppression -> Compressor. If voice still "
                "cuts out mid-word, lower gate_close_threshold_db (more negative). "
                "If background noise still comes through, the room is loud enough "
                "that suppression alone won't fix it — check the mic's physical "
                "gain/distance first."
            ),
        }
