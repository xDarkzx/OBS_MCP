# Changelog

All notable changes to OBS-MCP will be documented in this file.

## [Unreleased]

### Added

- **`diagnose_av_health` pipeline tool.** Pulls `GetStats` + `GetStreamStatus`
  + `GetRecordStatus` in one call and interprets the render-skip/output-skip/
  congestion ratios instead of returning raw numbers — distinguishes a GPU/
  scene bottleneck (high render-thread skips) from an encoder bottleneck
  (high output-thread skips, low congestion) from a network bottleneck (high
  congestion), and flags low disk space before it silently kills a
  recording. 148 tools total now.

### Fixed

- **Concurrent tool calls could corrupt results.** `obsws-python`'s request
  layer does a bare send-then-recv with no request-ID matching, so two
  overlapping calls could each read the other's response off the socket.
  `OBSClient.execute()` now serializes every call (connect included) through
  one lock.
- **The OBS WebSocket password was logged in plaintext.** `obsws-python`
  logs `"Connecting with parameters: ... password='...'"` at `INFO` on every
  connect; with our own logger also at `INFO`, that line reached stderr (and
  whatever log file the MCP client persists it to). `obsws_python`'s logger
  is now capped at `WARNING`.
- **An ordinary OBS-side error (bad scene name, out-of-range value) forced a
  full reconnect on the next call**, identically to an actual dropped
  connection — even though the socket was still healthy. Only a real
  connection failure resets the client now.
- **`clean_audio_input` could append the Noise Gate after a pre-existing
  Compressor/Suppression filter**, inverting the gate-first ordering the
  whole tool exists to guarantee. It now anchors its three managed stages
  as an adjacent, correctly-ordered group regardless of what already
  existed on the input.

### Added

- **Initial release — 147 tools covering the full obs-websocket v5 protocol.**
  Verified live against a real OBS Studio instance — scene/audio-mixer
  control, filter chains, video/output settings, and screenshots all
  confirmed working end-to-end, in addition to every tool mapping to a
  verified obs-websocket request (field names and types checked against the
  official protocol spec, not guessed).
  - **General** (9 tools): version/stats, hotkeys, custom events, vendor
    requests, persistent data.
  - **Config** (15 tools): scene collections, profiles, video/canvas
    settings, stream service destination, record directory.
  - **Sources** (3 tools): active-state check and screenshots.
  - **Scenes** (12 tools): list/create/remove/rename, program/preview
    control, per-scene transition overrides, canvases, groups.
  - **Inputs & Audio** (28 tools): the full mixer surface — mute, volume,
    balance, sync offset, monitor type, audio track routing, deinterlace
    mode/field order, dynamic property lists (e.g. display-capture's
    monitor list), properties-dialog button presses.
  - **Transitions** (9 tools): list/set, duration, settings, T-bar
    scrubbing, trigger (including studio mode).
  - **Filters** (10 tools): full CRUD on source filter chains, any order.
  - **Scene Items** (17 tools): transform, enabled/locked, z-order index,
    blend mode, source lookup, duplication.
  - **Outputs** (17 tools): virtual camera, replay buffer, generic named
    outputs.
  - **Stream & Record** (14 tools): start/stop/toggle, captions,
    pause/resume, file splitting, chapter markers.
  - **Media** (4 tools): playback status, seek, transport actions.
  - **UI** (8 tools): studio mode, property/filter/interact dialogs,
    monitor list, projectors.
  - **Pipelines** (1 tool): `clean_audio_input` — one-call Noise Gate →
    Noise Suppression → Compressor chain, with filter setting keys verified
    against OBS Studio's actual C source
    (`plugins/obs-filters/{noise-gate,noise-suppress,compressor}-filter.c`),
    not guessed from the UI. Picks `noise_suppress_filter_v2` (RNNoise) vs
    the older `noise_suppress_filter` based on what the connected OBS build
    actually registers, instead of assuming.
  - `tool_registry.py` ships with the fail-loud `_EXPECTED_MODULES` check
    from day one (a lesson learned the hard way on a sibling project —
    Reaper-MCP shipped for months with four tool modules silently excluded
    by an overbroad `.gitignore` rule; this project's registry refuses to
    stay quiet about a module going missing, for every profile, from the
    start).
