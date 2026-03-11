---
title: "CD Tree \u2194 MCP Tool Correlation Matrix"
description: Maps every MCP tool to its grandMA2 console object tree branch for navigation-based verification
version: 3.0.0
created: 2026-03-08T22:00:00Z
last_updated: 2026-03-11T19:13:00Z
---

# CD Tree \u2194 MCP Tool Correlation Matrix

## Purpose

This document maps every MCP tool to the grandMA2 console object tree branch
it operates on. Use this to know which `cd` + `list` path to inspect when
verifying that an MCP tool actually created/modified/deleted the expected object.

The **\u2194** symbol in the title represents the **bidirectional relationship** between
the grandMA2 console cd-tree (navigable object hierarchy) and the MCP tools that
read from or write to it: every tool either navigates the tree, queries a branch,
or produces a side-effect visible through `cd [branch]` + `list`.

## Quick Reference: 87 MCP Tools \u2192 Tree Branches

### Navigation & Inspection Tools (7)

| MCP Tool | Tree Branch | cd Command | Purpose |
|----------|------------|------------|---------|
| `navigate_console` | Any | `cd [destination]` | Navigate to any tree branch |
| `get_console_location` | Any | _(empty line)_ | Query current location |
| `list_console_destination` | Any | `list` | Enumerate children at current cd |
| `scan_console_indexes` | Any | `cd N` \u2192 `list` \u2192 `cd /` (loop) | Sequential index discovery |
| `set_node_property` | Any | `cd [path]` \u2192 `assign N/prop=val` | Set property on tree node |
| `get_object_info` | Any | `info [type] [id]` | Query object metadata |
| `navigate_page` | `cd Page` / `cd FaderPage` | `Page N` | Navigate executor pages; updates `$FADERPAGE`/`$BUTTONPAGE`/`$CHANNELPAGE` |

### Object-Creating/Modifying Tools (13)

| MCP Tool | Tree Branch | cd + list Verification | MA Command | Risk |
|----------|------------|----------------------|------------|------|
| `create_fixture_group` | `cd Group` | `cd Group` \u2192 `list` \u2192 check group ID appears | `SelFix N Thru M; Store Group X` | DESTRUCTIVE |
| `store_current_cue` | `cd Sequence.N` | `cd Sequence.N` \u2192 `list` \u2192 check cue ID appears | `Store Cue N [Sequence X]` | DESTRUCTIVE |
| `store_cue_with_timing` | `cd Sequence.N` | `cd Sequence.N` \u2192 `list` \u2192 check cue ID appears | `Store Cue N /fade=F /out=O [Sequence X]` | DESTRUCTIVE |
| `store_new_preset` | `cd PresetType.N` | `cd PresetType.N` \u2192 `list` \u2192 check preset ID | `Store Preset T.N` | DESTRUCTIVE |
| `store_object` | _varies_ | `cd [type]` \u2192 `list` \u2192 check object ID | `Store [Type] N` | DESTRUCTIVE |
| `update_cue_data` | `cd Sequence.N` | `cd Sequence.N` \u2192 `list` \u2192 cue contents updated | `Update Cue N [Sequence X]` | DESTRUCTIVE |
| `assign_object(assign)` | `cd Executor` | `cd Executor` \u2192 `list` \u2192 check executor has source | `Assign [Src] At [Tgt]` | DESTRUCTIVE |
| `assign_object(layout)` | `cd Layout` | `cd Layout.N` \u2192 `list` \u2192 check object placed | `Assign [Src] At Layout N` | DESTRUCTIVE |
| `assign_object(function)` | `cd Executor` | `cd Executor` \u2192 `list` \u2192 check function set | `Assign [Func] Executor N` | DESTRUCTIVE |
| `assign_object(fade)` | `cd Sequence.N` | `cd Sequence.N` \u2192 `list` \u2192 check fade time | `Assign Fade T Cue N` | DESTRUCTIVE |
| `assign_object(empty)` | `cd Executor` | `cd Executor` \u2192 `list` \u2192 executor cleared | `Assign Empty Executor N` | DESTRUCTIVE |
| `label_or_appearance` | _varies_ | `cd [type]` \u2192 `list` \u2192 check name/appearance | `Label [Type] N "Name"` | DESTRUCTIVE |
| `copy_or_move_object` | _varies_ | `cd [type]` \u2192 `list` \u2192 check target ID | `Copy/Move [Type] N At M` | DESTRUCTIVE |
| `edit_object` | _varies_ | N/A (opens editor) | `Edit/Cut/Paste [Type] N` | SAFE_WRITE |
| `set_intensity` | Programmer | Programmer state (not persistent in tree) | `Fixture N At L` | SAFE_WRITE |
| `save_recall_view` | `cd View` / `cd ViewButton` | `cd View` \u2192 `list` \u2192 check view appears | `Store View N`, `Go View N`, `Label View N "X"` | DESTRUCTIVE (store) |
| `store_timecode_event` | `cd Timecode.N` | `cd Timecode.N` \u2192 `list` \u2192 check event time | `Store Timecode N Cue X At T` | DESTRUCTIVE |

### Object-Deleting Tools (2)

| MCP Tool | Tree Branch | cd + list Verification | MA Command |
|----------|------------|----------------------|------------|
| `delete_object` | _varies_ | `cd [type]` \u2192 `list` \u2192 confirm ID is gone | `Delete [Type] N /noconfirm` |
| `remove_content` | _varies_ | `cd [parent]` \u2192 `list` \u2192 confirm content removed | `Remove [Type] N` |

### Playback & Control Tools (13)

| MCP Tool | Tree Branch | cd + list Verification | MA Command | Risk |
|----------|------------|----------------------|------------|------|
| `execute_sequence` | `cd Sequence` | N/A (playback state, not tree) | `Go+ Sequence N` | SAFE_WRITE |
| `playback_action` | `cd Executor` | N/A (playback state) | `Go/GoBack/Goto` | SAFE_WRITE |
| `run_macro` | `cd Macro` | N/A (triggers execution) | `Go+ Macro N` | SAFE_WRITE |
| `apply_preset` | `cd PresetType.N` | Programmer state | `Call Preset T.N` | SAFE_WRITE |
| `set_attribute` | Programmer | Programmer state | `Attribute "X" At V` | SAFE_WRITE |
| `release_executor` | `cd Executor` | N/A (playback state) | `Release Executor N` | SAFE_WRITE |
| `blackout_toggle` | Global | N/A (output state) | `Blackout` | SAFE_WRITE |
| `control_executor` | `cd Executor` | N/A (playback state) | `Go/Top/Off/Flash/Solo Executor N` | SAFE_WRITE / DESTRUCTIVE (set_speed) |
| `control_timecode` | `cd Timecode` | N/A (playback state) | `Go/Off/Goto Timecode N` | SAFE_WRITE |
| `control_timer` | `cd Timer` | N/A (runtime state) | `Go/Off/Oops Timer N` | SAFE_WRITE |
| `set_executor_level` | `cd Executor` | N/A (fader level, not persistent) | `Fader Executor N At L` | SAFE_WRITE |
| `toggle_console_mode` | Global | N/A (mode flag) | `Blind`/`Highlight`/`Solo`/`Freeze` | SAFE_WRITE |
| `highlight_fixtures` | Programmer | N/A (programmer state) | `Highlight On/Off` | SAFE_WRITE |

### Selection & Programmer Tools (8)

| MCP Tool | Tree Branch | Notes | MA Command | Risk |
|----------|------------|-------|------------|------|
| `modify_selection` | Programmer | Adds/removes/replaces/clears fixture selection | `SelFix +/- N`, `SelFix N Thru M`, `Clear` | SAFE_WRITE |
| `select_fixtures_by_group` | `cd Group` | Selects all fixtures in a group | `Group N` | SAFE_WRITE |
| `select_executor` | `cd Executor` | Sets `$SELECTEDEXEC` | `Select Executor N` | SAFE_WRITE |
| `select_feature` | `cd Feature` | Updates `$FEATURE`, `$PRESET`, `$ATTRIBUTE` | `Feature [name]` | SAFE_WRITE |
| `select_preset_type` | `cd 10.2` | Updates `$PRESET`, `$FEATURE`, `$ATTRIBUTE` | `PresetType [id or name]` | SAFE_WRITE |
| `adjust_value_relative` | Programmer | Nudges attribute in programmer; not tree-persistent | `+/- [attr] At V` | SAFE_WRITE |
| `if_filter` | Programmer | Applies If filter to selection context | `If [condition]` | SAFE_WRITE |
| `remove_from_programmer` | Programmer | Removes channels/fixtures/group from programmer | `Off Fixture N`, `Off Group N` | SAFE_WRITE |

### Cue & Sequence Property Tools (4)

| MCP Tool | Tree Branch | cd + list Verification | MA Command | Risk |
|----------|------------|----------------------|------------|------|
| `set_cue_timing` | `cd Sequence.N` | `cd Sequence.N` \u2192 `list` \u2192 check updated timing | `Assign Fade T Delay D Cue N [Sequence X]` | DESTRUCTIVE |
| `assign_cue_trigger` | `cd Sequence.N` | `cd Sequence.N` \u2192 `list` \u2192 check trigger type | `Assign [TriggerType] Cue N [Sequence X]` | DESTRUCTIVE |
| `assign_executor_property` | `cd Executor` | `cd Executor` \u2192 `list` \u2192 check property | `Assign [Prop=V] [Sequence/Executor] N` | DESTRUCTIVE |
| `set_sequence_property` | `cd Sequence.N` | `cd Sequence.N` \u2192 node property changed | `cd [path]` \u2192 `assign N/prop=val` | DESTRUCTIVE |

### Utility Tools (6)

| MCP Tool | Tree Branch | Notes | Risk |
|----------|------------|-------|------|
| `clear_programmer` | Programmer | Clears selection/values, no tree change | SAFE_WRITE |
| `park_fixture` | `cd Fixture` | Parks output values | SAFE_WRITE |
| `unpark_fixture` | `cd Fixture` | Unparks output values | SAFE_WRITE |
| `manage_variable` | N/A | Variables are not in the cd tree | SAFE_WRITE |
| `send_raw_command` | Any | Depends on the raw command sent | varies |
| `undo_last_action` | Any | `Oops` N times; reverts last N tree changes | SAFE_WRITE |

### Import/Export Tools (5)

| MCP Tool | Tree Branch | MA Command | Purpose | Risk |
|----------|------------|------------|---------|------|
| `export_objects` | _varies_ | `Export [Type] [Range] "file"` | Export show objects to XML file | SAFE_READ |
| `import_objects` | _varies_ | `Import [Type] "file" At [id]` | Import objects from XML file | DESTRUCTIVE |
| `import_fixture_type` | `cd 10.3` | `Import FixtureType "file"` (EditSetup context) | Import fixture type from MA2 library | DESTRUCTIVE |
| `import_fixture_layer` | `cd 10.4` | `Import Layer "file"` (EditSetup context) | Import fixture layer XML into show patch | DESTRUCTIVE |
| `generate_fixture_layer_xml` | N/A (file I/O) | Writes XML file to importexport dir | Generate fixture layer XML for import | DESTRUCTIVE |

### Show Management Tools (3)

| MCP Tool | Tree Branch | MA Command | Risk |
|----------|------------|------------|------|
| `load_show` | N/A | `LoadShow "name"` | DESTRUCTIVE — replaces current show |
| `new_show` | N/A | `NewShow "name"` | DESTRUCTIVE — replaces current show |
| `save_show` | N/A | `Save` / `SaveAs "name"` | SAFE_WRITE — persists current show to disk |

### Variable & History Tools (3)

| MCP Tool | Tree Branch | MA Command | Purpose |
|----------|------------|------------|---------|
| `get_variable` | N/A | `ListVar`, `ListUserVar` | Read system/user variables |
| `list_system_variables` | N/A | `ListVar` | List all 26 built-in system variables |
| `list_undo_history` | N/A | `ListOops` | Show undo history |

### List & Query Tools (8)

| MCP Tool | Tree Branch | MA Command | Purpose |
|----------|------------|------------|---------|
| `list_shows` | N/A | `ListShows` | List available show files |
| `list_library` | N/A | `ListLibrary`, `ListEffectLibrary`, `ListMacroLibrary` | Browse fixture/effect/macro libraries |
| `query_object_list` | _varies_ | `list [type]` | List objects by type (groups, cues, presets, …) |
| `list_fixtures` | `cd Fixture` | `list fixture [N]` | List/check fixtures; use before park/intensity/attribute |
| `list_sequence_cues` | `cd Sequence.N` | `list cue [Sequence N]` | List/check cues within a sequence |
| `list_preset_pool` | `cd PresetType.N` | `list preset [T.N]` | List Global preset pool entries |
| `discover_object_names` | _varies_ | `cd [type]` \u2192 `list` \u2192 `cd /` | Navigate pool, return names for wildcard building |
| `get_executor_status` | `cd Executor` | `list executor [N]` | Query executor status (running/stopped/level) |

### LiveSetup Navigation Tools (4)

| MCP Tool | Tree Branch | cd Path | Purpose |
|----------|------------|---------|---------|
| `list_fixture_types` | `cd 10.3` | `cd /` \u2192 `cd 10` \u2192 `cd 3` \u2192 `list` | List all fixture types in the show |
| `list_layers` | `cd 10.4` | `cd /` \u2192 `cd 10` \u2192 `cd 4` \u2192 `list` | List all fixture layers |
| `list_universes` | `cd 10.5` | `cd /` \u2192 `cd 10` \u2192 `cd 5` \u2192 `list` | List DMX universes |
| `browse_preset_type` | `cd 10.2.N` | `cd /` \u2192 `cd 10.2.N[.M[.K]]` \u2192 `list` | Browse feature/attribute tree under a preset type |

### MAtricks Tools (2)

| MCP Tool | Tree Branch | cd Path | Purpose |
|----------|------------|---------|---------|
| `manage_matricks` | `cd MAtricks` | `set_property("MAtricks", ...)` | Configure MAtricks selection patterns |
| `create_matricks_library` | `cd MAtricks` | Store + assign + label loop | Generate combinatorial MAtricks pool (**DESTRUCTIVE**) |

### Fixture Patching Tools (4)

| MCP Tool | Tree Branch | cd Path | MA Command | Risk |
|----------|------------|---------|------------|------|
| `browse_patch_schedule` | `cd 10.3.N` | `cd /` \u2192 `cd 10` \u2192 `cd 3` \u2192 `cd N` \u2192 `list` | Navigation + list | SAFE_READ |
| `patch_fixture` | `cd Fixture` | N/A | `Assign FixtureType At Fixture; Assign DMX At Fixture` | DESTRUCTIVE |
| `unpatch_fixture` | `cd Fixture` | N/A | `Delete Fixture N` | DESTRUCTIVE |
| `set_fixture_type_property` | `cd 10.3.N` | `set_property("10.3.N", ...)` | `cd` + `assign N/prop=val` | DESTRUCTIVE |

### Categorization & Discovery Tools (5)

| MCP Tool | Tree Branch | Purpose | Risk |
|----------|------------|---------|------|
| `search_codebase` | N/A | RAG semantic search across MCP server codebase | SAFE_READ |
| `list_tool_categories` | N/A | List ML-generated taxonomy of all MCP tools | SAFE_READ |
| `recluster_tools` | N/A | Re-run K-Means clustering on all tools | SAFE_READ |
| `get_similar_tools` | N/A | Find MCP tools similar to a given tool | SAFE_READ |
| `suggest_tool_for_task` | N/A | Suggest MCP tools for a natural-language task | SAFE_READ |

## Object Tree Branches (53 navigable via cd)

### Core Show Objects (most commonly used)

| Branch | cd Keyword | Create Tools | Delete Tools | Query Tools |
|--------|-----------|--------------|--------------|-------------|
| **Groups** | `cd Group` | `create_fixture_group` | `delete_object("group")` | `query_object_list("group")`, `list_console_destination` |
| **Sequences** | `cd Sequence` | `store_object("sequence")` | `delete_object("sequence")` | `query_object_list("sequence")`, `list_console_destination` |
| **Cues** | `cd Sequence.N` | `store_current_cue` | `delete_object("cue")` | `query_object_list("cue")`, `list_console_destination` |
| **Presets** | `cd Preset`, `cd PresetType.N`, `cd 17.1.N` | `store_new_preset` | `delete_object("preset")` | `query_object_list("preset")`, `list_preset_pool`, `list_console_destination` |
| **Macros** | `cd Macro` | `store_object("macro")` | `delete_object("macro")` | `query_object_list`, `list_console_destination` |
| **Effects** | `cd Effect` | `store_object("effect")` | `delete_object("effect")` | `query_object_list`, `list_console_destination` |
| **Executors** | `cd Executor` | `assign_object(assign)` | `assign_object(empty)` | `list_console_destination` |
| **Layouts** | `cd Layout` | `assign_object(layout)` | `delete_object("layout")` | `list_console_destination` |
| **Fixtures** | `cd Fixture` | `patch_fixture` | `delete_object("fixture")`, `unpatch_fixture` | `query_object_list`, `list_console_destination` |
| **Channels** | `cd Channel` | _(patched externally)_ | \u2014 | `list_console_destination` |

### Page Context

| Branch | cd Keyword | Related Tools |
|--------|-----------|---------------|
| **Pages** | `cd Page` | `playback_action` (page context) |
| **Fader Pages** | `cd FaderPage` | `playback_action` |
| **Button Pages** | `cd ButtonPage` | `playback_action` |

### Configuration & System Objects

| Branch | cd Keyword | Related Tools |
|--------|-----------|---------------|
| **Filters** | `cd Filter` | `store_object("filter")` |
| **Worlds** | `cd World` | `store_object("world")` |
| **Timecodes** | `cd Timecode` | `store_object("timecode")` |
| **Timers** | `cd Timer` | `store_object("timer")` |
| **Users** | `cd User` | Read-only via `list` |
| **User Profiles** | `cd UserProfile` | Read-only via `list` |
| **DMX** | `cd Dmx`, `cd DmxUniverse`, `cd 10.5` | `park_fixture`/`unpark_fixture`, `list_universes` |
| **Fixture Types** | `cd FixtureType`, `cd 10.3` | `list_fixture_types`, `browse_patch_schedule`, `set_fixture_type_property` |
| **Attributes** | `cd Attribute` | `set_attribute`, `query_object_list("attribute")` |
| **Features** | `cd Feature` | Read-only via `list` |

### UI & Display Objects

| Branch | cd Keyword | Related Tools |
|--------|-----------|---------------|
| **Views** | `cd View`, `cd ViewButton`, `cd ViewPage` | Read-only |
| **Screens** | `cd Screen` | Read-only |
| **Cameras** | `cd Camera` | Read-only |
| **Forms** | `cd Form` | Read-only |
| **Images** | `cd Image` | Read-only |
| **Gel** | `cd Gel` | Read-only |

### Remaining Navigable Branches (no direct MCP tool)

`Agenda`, `ChannelFader`, `Cue`, `Default`, `ExecButton1-3`, `Fader`,
`Mask`, `MAtricks`, `Part`, `PreviewExecutor`, `Programmer`, `Remote`,
`Root`, `RdmFixtureType`, `Selection`, `SoundChannel`, `SpecialMaster`,
`Messages`

### LiveSetup Tree (cd 10) — Deep Navigation

The LiveSetup branch is accessed via numeric index `cd 10` and supports
deep dot-separated paths up to depth 8+.

| Index Path | Node | MCP Tools |
|------------|------|-----------|
| `10` | LiveSetup | _(parent)_ |
| `10.1` | DMX_Profiles | — |
| `10.2` | PresetTypes (9 types: Dimmer-Video) | `browse_preset_type` |
| `10.2.N` | PresetType N — lists Features | `browse_preset_type(depth=1)` |
| `10.2.N.M` | Feature M under PresetType N — lists Attributes | `browse_preset_type(depth=2)` |
| `10.2.N.M.K` | Attribute K — lists SubAttributes | `browse_preset_type(depth=3)` |
| `10.2.N.M.K.L` | SubAttribute L — **leaf** (NO OBJECTS FOUND) | — |
| `10.3` | FixtureTypes | `list_fixture_types` |
| `10.3.N` | Fixture Type N | `browse_patch_schedule`, `set_fixture_type_property` |
| `10.4` | Layers | `list_layers` |
| `10.5` | Universes | `list_universes` |
| `10.6` | Objects3D | — |

## Verification Pattern

For every object-creating or object-deleting MCP tool, use this 3-step cycle:

```
1. navigate_console(destination="[branch]")
   list_console_destination()                  # BEFORE state

2. <execute MCP tool>                           # create / modify / delete

3. navigate_console(destination="[branch]")
   list_console_destination()                  # AFTER state
   # Compare entries \u2192 validate object appeared/disappeared
```

## Phase 2 Test Matrix (8 Core Branches)

| # | Branch | MCP Tool Call | Expected MA Command | Verify |
|---|--------|-------------|---------------------|--------|
| 1 | `Group` | `create_fixture_group(1, 10, 99, "Test")` | `SelFix 1 Thru 10; Store Group 99` | `cd Group` \u2192 Group 99 appears |
| 2 | `Group` | `delete_object("group", 99, confirm_destructive=True)` | `Delete Group 99 /noconfirm` | `cd Group` \u2192 Group 99 gone |
| 3 | `Sequence` | `store_object("sequence", 99, confirm_destructive=True)` | `Store Sequence 99` | `cd Sequence` \u2192 Seq 99 appears |
| 4 | `Sequence.99` | `store_current_cue(1, sequence_id=99)` | `Store Cue 1 Sequence 99` | `cd Sequence.99` \u2192 Cue 1 appears |
| 5 | `PresetType.4` | `store_new_preset("color", 99)` | `Store Preset 4.99` | `cd PresetType.4` \u2192 Preset 99 appears |
| 6 | `Macro` | `store_object("macro", 99, confirm_destructive=True)` | `Store Macro 99` | `cd Macro` \u2192 Macro 99 appears |
| 7 | `Executor` | `assign_object(mode="assign", ...)` | `Assign Seq 99 At Exec 201` | `cd Executor` \u2192 Exec 201 has seq |
| 8 | `Effect` | `store_object("effect", 99, confirm_destructive=True)` | `Store Effect 99` | `cd Effect` \u2192 Effect 99 appears |

### Cleanup Sequence

```
delete_object("group", 99, confirm_destructive=True)
delete_object("cue", 1, confirm_destructive=True)        # in sequence 99
delete_object("sequence", 99, confirm_destructive=True)
delete_object("preset", "4.99", confirm_destructive=True)
delete_object("macro", 99, confirm_destructive=True)
assign_object(mode="empty", target_type="executor", target_id=201, confirm_destructive=True)
delete_object("effect", 99, confirm_destructive=True)
```

## Tool Count Summary

| Category | Count | Tools |
|----------|-------|-------|
| Navigation & Inspection | 7 | `navigate_console`, `get_console_location`, `list_console_destination`, `scan_console_indexes`, `set_node_property`, `get_object_info`, `navigate_page` |
| Object Create/Modify | 13 | `create_fixture_group`, `store_current_cue`, `store_cue_with_timing`, `store_new_preset`, `store_object`, `update_cue_data`, `assign_object` _(5 modes: assign/layout/function/fade/empty)_, `label_or_appearance`, `copy_or_move_object`, `edit_object`, `set_intensity`, `save_recall_view`, `store_timecode_event` |
| Object Delete | 2 | `delete_object`, `remove_content` |
| Playback & Control | 13 | `execute_sequence`, `playback_action`, `run_macro`, `apply_preset`, `set_attribute`, `release_executor`, `blackout_toggle`, `control_executor`, `control_timecode`, `control_timer`, `set_executor_level`, `toggle_console_mode`, `highlight_fixtures` |
| Selection & Programmer | 8 | `modify_selection`, `select_fixtures_by_group`, `select_executor`, `select_feature`, `select_preset_type`, `adjust_value_relative`, `if_filter`, `remove_from_programmer` |
| Cue & Sequence Properties | 4 | `set_cue_timing`, `assign_cue_trigger`, `assign_executor_property`, `set_sequence_property` |
| Import/Export | 5 | `export_objects`, `import_objects`, `import_fixture_type`, `import_fixture_layer`, `generate_fixture_layer_xml` |
| Show Management | 3 | `load_show`, `new_show`, `save_show` |
| Variable & History | 3 | `get_variable`, `list_system_variables`, `list_undo_history` |
| List & Query | 8 | `list_shows`, `list_library`, `query_object_list`, `list_fixtures`, `list_sequence_cues`, `list_preset_pool`, `discover_object_names`, `get_executor_status` |
| LiveSetup Navigation | 4 | `list_fixture_types`, `list_layers`, `list_universes`, `browse_preset_type` |
| MAtricks | 2 | `manage_matricks`, `create_matricks_library` |
| Fixture Patching | 4 | `browse_patch_schedule`, `patch_fixture`, `unpatch_fixture`, `set_fixture_type_property` |
| Utility | 6 | `clear_programmer`, `park_fixture`, `unpark_fixture`, `manage_variable`, `send_raw_command`, `undo_last_action` |
| Categorization & Discovery | 5 | `search_codebase`, `list_tool_categories`, `recluster_tools`, `get_similar_tools`, `suggest_tool_for_task` |
| **Total** | **87** | |
