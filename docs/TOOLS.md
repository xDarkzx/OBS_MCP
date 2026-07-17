# Tools Reference

Complete reference for every MCP tool exposed by OBS-MCP — **147 tools across 13 modules**, full coverage of the [obs-websocket v5](https://github.com/obsproject/obs-websocket) protocol. Grouped by domain; each tool's exact request/response shape follows the [official protocol spec](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md).

Scene, input, and filter names are **case-sensitive** and must match exactly what's shown in OBS. Use `get_scene_list` / `get_input_list` / `get_source_filter_list` to see exact names before acting on them.

## General

Source: `general_tools.py`

| Tool | Description |
|------|-------------|
| `get_version()` | OBS/obs-websocket version, platform, supported image formats, and the full list of requests available. |
| `get_stats()` | Live perf stats — CPU/memory usage, active FPS, render/output skipped frames, disk space. |
| `broadcast_custom_event(event_data)` | Broadcast an arbitrary JSON payload to all subscribed obs-websocket clients. |
| `call_vendor_request(vendor_name, request_type, request_data)` | Call a request registered by a third-party OBS plugin/script. |
| `get_hotkey_list()` | List all hotkey names. |
| `trigger_hotkey_by_name(hotkey_name, context_name)` | Trigger a hotkey by name. |
| `trigger_hotkey_by_key_sequence(key_id, shift, control, alt, command)` | Trigger a hotkey by simulated key press + modifiers. |
| `get_persistent_data(realm, slot_name)` | Read a value from an OBS persistent-data slot. |
| `set_persistent_data(realm, slot_name, slot_value)` | Write a value to an OBS persistent-data slot — useful for state the AI needs across calls. |

## Config

Source: `config_tools.py`

| Tool | Description |
|------|-------------|
| `get_scene_collection_list()` | List all scene collections and the active one. |
| `set_current_scene_collection(name)` | Switch scene collections. Blocks until complete. |
| `create_scene_collection(name)` | Create and switch to a new scene collection. |
| `get_profile_list()` | List all profiles and the active one. |
| `set_current_profile(name)` | Switch profiles. |
| `create_profile(name)` | Create and switch to a new profile. |
| `remove_profile(name)` | Delete a profile. |
| `get_profile_parameter(category, name)` | Read a raw .ini parameter from the current profile. |
| `set_profile_parameter(category, name, value)` | Write a raw .ini parameter. Advanced/low-level. |
| `get_video_settings()` | Canvas/output resolution and FPS. |
| `set_video_settings(...)` | Change resolution/FPS — width/height fields must be set in pairs. |
| `get_stream_service_settings()` | Current stream destination service and settings. |
| `set_stream_service_settings(service_type, settings)` | Set stream destination (e.g. `rtmp_custom` + server/key). |
| `get_record_directory()` | Current recording output directory. |
| `set_record_directory(path)` | Change recording output directory. |

## Sources

Source: `source_tools.py`. Compatible with both inputs and scenes.

| Tool | Description |
|------|-------------|
| `get_source_active(source_name)` | Whether a source is showing in Program and/or visible in the UI. |
| `get_source_screenshot(source_name, image_format, ...)` | Base64-encoded screenshot — actually SEE what's on stream. |
| `save_source_screenshot(source_name, image_file_path, ...)` | Save a screenshot directly to disk. |

## Scenes

Source: `scene_tools.py`

| Tool | Description |
|------|-------------|
| `get_canvas_list()` | List canvases (multi-canvas is a newer OBS feature). |
| `get_scene_list()` | List every scene plus current program/preview. |
| `get_group_list()` | List all groups (OBS treats groups as a special scene type). |
| `get_current_program_scene()` | The scene currently live on Program. |
| `set_current_program_scene(scene_name)` | Cut to a scene — the core "switch scenes" action. |
| `get_current_preview_scene()` | The scene loaded in Preview (studio mode only). |
| `set_current_preview_scene(scene_name)` | Stage a scene in Preview before transitioning. |
| `create_scene(scene_name)` | Create a new empty scene. |
| `remove_scene(scene_name)` | Delete a scene. |
| `set_scene_name(scene_name, new_scene_name)` | Rename a scene. |
| `get_scene_transition_override(scene_name)` | Get a scene's overridden transition, if any. |
| `set_scene_transition_override(scene_name, transition_name, transition_duration_ms)` | Override which transition is used switching into this scene. |

## Inputs & Audio

Source: `input_tools.py` — the deepest audio-control layer available.

| Tool | Description |
|------|-------------|
| `get_input_list(input_kind)` | List all inputs, optionally filtered by kind. |
| `get_input_kind_list(unversioned)` | List every input kind this OBS install can create. |
| `get_special_inputs()` | Names of the built-in Desktop Audio 1/2 and Mic/Aux 1-4 channels. |
| `create_input(input_name, input_kind, scene_name, input_settings, scene_item_enabled)` | Create a new input and add it to a scene. |
| `remove_input(input_name)` | Delete an input (and its scene items). |
| `set_input_name(input_name, new_input_name)` | Rename an input. |
| `get_input_default_settings(input_kind)` | Default settings for an input kind. |
| `get_input_settings(input_name)` | Current settings + kind of an input. |
| `set_input_settings(input_name, input_settings, overlay)` | Configure an input. |
| `get_input_mute(input_name)` / `set_input_mute(input_name, input_muted)` / `toggle_input_mute(input_name)` | Mute control. |
| `get_input_volume(input_name)` / `set_input_volume(input_name, volume_db, volume_mul)` | Volume in dB or linear mul. |
| `get_input_audio_balance(input_name)` / `set_input_audio_balance(input_name, balance)` | Stereo balance, 0.0-1.0. |
| `get_input_audio_sync_offset(input_name)` / `set_input_audio_sync_offset(input_name, offset_ms)` | Fix audio/video drift, -950..20000ms. |
| `get_input_audio_monitor_type(input_name)` / `set_input_audio_monitor_type(input_name, monitor_type)` | Monitoring mode (none/monitor-only/monitor+output). |
| `get_input_audio_tracks(input_name)` / `set_input_audio_tracks(input_name, audio_tracks)` | Which of the 6 mixer tracks an input routes to. |
| `get_input_deinterlace_mode(input_name)` / `set_input_deinterlace_mode(input_name, mode)` | Deinterlace mode (async inputs only). |
| `get_input_deinterlace_field_order(input_name)` / `set_input_deinterlace_field_order(input_name, field_order)` | Deinterlace field order. |
| `get_input_properties_list_property_items(input_name, property_name)` | Items of a dynamic list property, e.g. display-capture's monitor list. |
| `press_input_properties_button(input_name, property_name)` | Press a properties-dialog button, e.g. a browser source's refresh. |

## Transitions

Source: `transition_tools.py`

| Tool | Description |
|------|-------------|
| `get_transition_kind_list()` | List available transition kinds (Cut, Fade, Stinger, etc). |
| `get_scene_transition_list()` | List configured transitions and the current one. |
| `get_current_scene_transition()` | Full detail: kind, duration, fixed?, settings. |
| `set_current_scene_transition(transition_name)` | Make a transition active for the next switch. |
| `set_current_scene_transition_duration(duration_ms)` | Duration, 50-20000ms, if not fixed-duration. |
| `set_current_scene_transition_settings(settings, overlay)` | Configure a transition (e.g. a Stinger's video file). |
| `get_current_scene_transition_cursor()` | Transition progress, 0.0-1.0. |
| `trigger_studio_mode_transition()` | Trigger the current transition — cuts Preview to Program. |
| `set_tbar_position(position, release)` | Manual T-bar transition scrubbing. |

## Filters

Source: `filter_tools.py`. Raw CRUD — for a one-call clean mic setup see [Pipelines](#pipelines) instead.

| Tool | Description |
|------|-------------|
| `get_source_filter_kind_list()` | List every filter kind this OBS install supports. |
| `get_source_filter_list(source_name)` | List a source's filters, in chain order. |
| `get_source_filter_default_settings(filter_kind)` | Default settings for a filter kind. |
| `create_source_filter(source_name, filter_name, filter_kind, filter_settings)` | Add a filter to a source. |
| `remove_source_filter(source_name, filter_name)` | Remove a filter. |
| `set_source_filter_name(source_name, filter_name, new_filter_name)` | Rename a filter. |
| `get_source_filter(source_name, filter_name)` | Filter's enabled state, index, kind, settings. |
| `set_source_filter_index(source_name, filter_name, filter_index)` | Reorder a filter in the chain. |
| `set_source_filter_settings(source_name, filter_name, filter_settings, overlay)` | Configure a filter's parameters. |
| `set_source_filter_enabled(source_name, filter_name, filter_enabled)` | Enable/disable without removing. |

## Scene Items

Source: `scene_item_tools.py` — the sources placed *within* a scene (distinct from the sources/inputs themselves).

| Tool | Description |
|------|-------------|
| `get_scene_item_list(scene_name)` | List every placed source in a scene. |
| `get_group_scene_item_list(group_name)` | Same, for a group. |
| `get_scene_item_id(scene_name, source_name, search_offset)` | Find a scene item's numeric ID by source name. |
| `get_scene_item_source(scene_name, scene_item_id)` | The source a scene item references. |
| `create_scene_item(scene_name, source_name, scene_item_enabled)` | Add an existing source to a scene. |
| `remove_scene_item(scene_name, scene_item_id)` | Remove a scene item (not the underlying source). |
| `duplicate_scene_item(scene_name, scene_item_id, destination_scene_name)` | Copy a scene item's transform/crop. |
| `get_scene_item_transform(scene_name, scene_item_id)` / `set_scene_item_transform(...)` | Position, scale, rotation, crop. |
| `get_scene_item_enabled(...)` / `set_scene_item_enabled(...)` | Show/hide a scene item. |
| `get_scene_item_locked(...)` / `set_scene_item_locked(...)` | Lock state. |
| `get_scene_item_index(...)` / `set_scene_item_index(...)` | Z-order / stacking position. |
| `get_scene_item_blend_mode(...)` / `set_scene_item_blend_mode(...)` | Blend mode. |

## Outputs

Source: `output_tools.py`

| Tool | Description |
|------|-------------|
| `get_virtual_cam_status()` / `toggle_virtual_cam()` / `start_virtual_cam()` / `stop_virtual_cam()` | Virtual camera control. |
| `get_replay_buffer_status()` / `toggle_replay_buffer()` / `start_replay_buffer()` / `stop_replay_buffer()` | Replay buffer control. |
| `save_replay_buffer()` | Save the "instant replay" clip. |
| `get_last_replay_buffer_replay()` | File path of the last saved replay. |
| `get_output_list()` | List every registered output (stream, record, virtualcam, plugin-added). |
| `get_output_status(output_name)` | Active/reconnecting, timecode, duration, congestion, bytes, frames. |
| `toggle_output(output_name)` / `start_output(output_name)` / `stop_output(output_name)` | Named output control. |
| `get_output_settings(output_name)` / `set_output_settings(output_name, settings)` | Named output settings. |

## Stream & Record

Source: `stream_record_tools.py`

| Tool | Description |
|------|-------------|
| `get_stream_status()` | Active/reconnecting, timecode, duration, congestion, bytes, frames. |
| `toggle_stream()` / `start_stream()` / `stop_stream()` | Go live / end stream. |
| `send_stream_caption(caption_text)` | Send CEA-608 captions over the stream. |
| `get_record_status()` | Active, paused, timecode, duration, bytes. |
| `toggle_record()` / `start_record()` / `stop_record()` | Recording control. `stop_record` returns the saved file path. |
| `toggle_record_pause()` / `pause_record()` / `resume_record()` | Pause/resume. |
| `split_record_file()` | Split the current recording into a new file now. |
| `create_record_chapter(chapter_name)` | Add a chapter marker (Hybrid MP4 output only). |

## Media

Source: `media_tools.py` — playback control for media sources (video files, VLC sources).

| Tool | Description |
|------|-------------|
| `get_media_input_status(input_name)` | Playback state, duration, cursor position. |
| `set_media_input_cursor(input_name, cursor_ms)` | Seek to an absolute position. |
| `offset_media_input_cursor(input_name, offset_ms)` | Seek relative to current position. |
| `trigger_media_input_action(input_name, action)` | Play/pause/stop/restart/next/previous. |

## UI

Source: `ui_tools.py`

| Tool | Description |
|------|-------------|
| `get_studio_mode_enabled()` / `set_studio_mode_enabled(enabled)` | Studio mode (separate Preview/Program) toggle. |
| `open_input_properties_dialog(input_name)` | Open an input's Properties dialog. |
| `open_input_filters_dialog(input_name)` | Open an input's Filters dialog. |
| `open_input_interact_dialog(input_name)` | Open an input's Interact dialog. |
| `get_monitor_list()` | List connected monitors. |
| `open_video_mix_projector(video_mix_type, monitor_index, projector_geometry)` | Open a Preview/Program/Multiview projector. |
| `open_source_projector(source_name, monitor_index, projector_geometry)` | Open a projector for a specific source. |

## Pipelines

Source: `pipeline_tools.py` — composite tools that do the actual job in one call instead of raw protocol wrapping.

| Tool | Description |
|------|-------------|
| `clean_audio_input(input_name, gate, suppression, compressor, ...)` | One-call Noise Gate → Noise Suppression → Compressor chain. Filter parameter keys verified against OBS Studio's actual C source, not guessed. Auto-picks RNNoise vs. the older suppression method based on what the connected OBS build supports. Skips stages that already exist. |

---

## A note on omitted requests

`Sleep` (from the General category) is intentionally not exposed — it only
functions inside `RequestBatch` calls (`SERIAL_REALTIME`/`SERIAL_FRAME`
execution), which this version doesn't implement. Every other request in
the [obs-websocket v5 protocol](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md)
is covered.
