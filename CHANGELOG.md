# Changelog

All notable changes to OBS-MCP will be documented in this file.

## [Unreleased]

### Added

- **Initial release — 147 tools covering the full obs-websocket v5 protocol.**
  ⚠️ **Not yet tested against a live OBS Studio instance** — every tool maps
  to a verified obs-websocket request (field names and types checked against
  the official protocol spec, not guessed), and the full module set was
  syntax-checked and registration-tested, but no end-to-end run against real
  OBS has happened yet. Test before relying on it for anything live.
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
