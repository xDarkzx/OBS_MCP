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

    @mcp.tool()
    async def diagnose_av_health() -> dict:
        """Diagnose why a stream/recording might be dropping frames or stuttering
        — pulls GetStats + GetStreamStatus + GetRecordStatus in one call and
        interprets the ratios instead of leaving the AI to fetch three things
        and do the arithmetic itself.

        The three numbers that actually matter, and what each one means:
        - renderSkippedFrames/renderTotalFrames high: OBS's render thread can't
          keep up with your scene (too many sources/filters, canvas resolution
          too high, or GPU-bound). Fix: lower canvas resolution, cut filters,
          simplify the scene.
        - outputSkippedFrames/outputTotalFrames high with LOW congestion:
          encoding can't keep up (CPU/GPU encoder overloaded). Fix: switch to
          a hardware encoder (NVENC/AMF/QSV), lower the encoder preset, or
          lower output resolution/fps.
        - outputCongestion high: the network can't keep up with your bitrate.
          Fix: lower bitrate, check upload speed.

        These thresholds are heuristics, not authoritative OBS cutoffs — a
        few skipped frames right after starting a stream is normal; this
        flags *sustained* skip ratios worth investigating, not noise.
        """
        stats = await client.execute("GetStats")
        stream_status = await client.execute("GetStreamStatus")
        record_status = await client.execute("GetRecordStatus")

        def pct(skipped, total):
            return round(100 * skipped / total, 2) if total else 0.0

        render_skip_pct = pct(stats.get("renderSkippedFrames", 0), stats.get("renderTotalFrames", 0))
        output_skip_pct = pct(stats.get("outputSkippedFrames", 0), stats.get("outputTotalFrames", 0))
        congestion = stream_status.get("outputCongestion", 0.0)

        findings = []
        if render_skip_pct > 2.0:
            findings.append(
                f"Render thread is skipping {render_skip_pct}% of frames — OBS can't render "
                f"your scene fast enough. Likely GPU-bound: lower canvas resolution, cut "
                f"filters/sources, or simplify the scene."
            )
        if output_skip_pct > 2.0 and congestion < 0.1:
            findings.append(
                f"Output thread is skipping {output_skip_pct}% of frames with low network "
                f"congestion ({congestion}) — encoding itself can't keep up. Switch to a "
                f"hardware encoder (NVENC/AMF/QSV), lower the encoder preset, or lower "
                f"output resolution/fps."
            )
        if congestion > 0.1:
            findings.append(
                f"Output congestion is {congestion} (0.0-1.0 scale) — your upload can't "
                f"keep up with the current bitrate. Lower the video bitrate or check your "
                f"actual upload speed."
            )
        if stream_status.get("outputReconnecting"):
            findings.append("Stream output is actively reconnecting right now — the connection to your streaming service just dropped.")
        available_disk_mb = stats.get("availableDiskSpace", None)
        if available_disk_mb is not None and available_disk_mb < 2048:
            findings.append(
                f"Only {available_disk_mb}MB of disk space free on the recording drive — "
                f"recordings can silently stop or corrupt when this runs out."
            )

        if not findings:
            findings.append("No sustained frame-skip, congestion, or disk-space issues detected in current stats.")

        return {
            "streaming": {
                "active": stream_status.get("outputActive", False),
                "reconnecting": stream_status.get("outputReconnecting", False),
                "congestion": congestion,
                "skipped_frames_percent": output_skip_pct,
            },
            "recording": {
                "active": record_status.get("outputActive", False),
                "paused": record_status.get("outputPaused", False),
            },
            "render_skipped_frames_percent": render_skip_pct,
            "cpu_usage_percent": stats.get("cpuUsage"),
            "memory_usage_mb": stats.get("memoryUsage"),
            "available_disk_space_mb": available_disk_mb,
            "findings": findings,
        }
