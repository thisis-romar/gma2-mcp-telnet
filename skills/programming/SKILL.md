---
title: grandMA2 Cue & Effect Programming
description: "grandMA2 cue and effect programming guide. Generates store, sequence, timing, MAtricks, and appearance commands. Execution available via ma2-onPC-MCP server."
version: 2.0.0
created: 2026-03-13T00:00:00Z
last_updated: 2026-03-15T00:00:00Z
name: gma2-programming
license: Apache-2.0
metadata:
  author: emblem-projects
  category: "AV/Lighting"
  console: "grandMA2"
  tier: "free-hybrid"
  available_tiers:
    - free-hybrid
  mcp_server: "thisis-romar/ma2-onPC-MCP"
  marketplace_slugs:
    skillsmp: "emblem/gma2-programming"
    clawhub: "gma2-programming"
  triggers:
    - "cue"
    - "effect"
    - "sequence"
    - "matricks"
    - "preset"
    - "appearance"
    - "store cue"
  depends_on:
    - "gma2-command-reference"
    - "gma2-show-architecture"
  max_risk_tier: "DESTRUCTIVE"
  tools_required:
    - "send_raw_command"
    - "store_cue"
    - "select_fixture"
  token_budget:
    level_1: 80
    level_2: 330
    level_3_max: 1100
---

# grandMA2 Cue & Effect Programming

Expert grandMA2 lighting programmer. Generates syntactically correct commands for cue storage, sequence building, timing, MAtricks sub-selection, effect engine, and appearance configuration.
