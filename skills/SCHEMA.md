---
title: Skill Metadata Schema
description: Specification for all required and optional YAML frontmatter fields in SKILL.md files
version: 1.0.0
created: 2026-03-15T00:00:00Z
last_updated: 2026-03-15T00:00:00Z
---

# Skill Metadata Schema

This document defines the complete YAML frontmatter specification for `SKILL.md` files in the ma2-onPC-MCP skill library.

## Three-Level Framework

Skills follow a progressive disclosure model:

| Level | File | Purpose | Token budget |
|-------|------|---------|-------------|
| **Level 1** | `SKILL.md` | Pure metadata + 1-line persona | ~80 tokens |
| **Level 2** | `context.md` | Quick answers, grep patterns, mode, scope, safety | ~300 tokens |
| **Level 3** | `references/*.md` | Deep reference material, loaded on demand | ~1000-1200 tokens |

**Retrieval protocol:**
1. **Router** — Read SKILL.md first (metadata only, ~80 tokens)
2. **Grep index** — For cross-skill lookups, grep `skills/INDEX.md` for the topic
3. **Quick answers** — Read context.md grep patterns to find specific sections in references
4. **Deep dive** — Only read full reference files when grep results are insufficient

## Required Fields

### Document fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title (matches the `# H1` heading) |
| `description` | string | One-line summary |
| `version` | semver | `MAJOR.MINOR.PATCH` — bump MAJOR for restructures, MINOR for new content |
| `created` | ISO 8601 | `YYYY-MM-DDTHH:MM:SSZ` — set once, never changed |
| `last_updated` | ISO 8601 | Updated every time file content changes |
| `name` | string | Package identifier, format: `gma2-<skill-name>` |
| `license` | string | License identifier (e.g. `Apache-2.0`) |

### Metadata block

| Field | Type | Description |
|-------|------|-------------|
| `metadata.author` | string | Author identifier |
| `metadata.category` | string | Marketplace category (e.g. `"AV/Lighting"`) |
| `metadata.console` | string | Target console (e.g. `"grandMA2"`) |
| `metadata.tier` | string | `"free"` or `"free-hybrid"` |
| `metadata.available_tiers` | list | All tiers this skill is available in |
| `metadata.mcp_server` | string | GitHub repo of the MCP server |
| `metadata.marketplace_slugs` | object | Marketplace identifiers (`skillsmp`, `clawhub`) |
| `metadata.triggers` | list | Keywords/phrases that route to this skill (5-10 items) |
| `metadata.depends_on` | list | Skill `name` values this skill depends on (empty list if none) |
| `metadata.max_risk_tier` | string | Highest safety tier: `"SAFE_READ"`, `"SAFE_WRITE"`, or `"DESTRUCTIVE"` |
| `metadata.tools_required` | list | MCP tool names needed for hybrid execution (empty list for knowledge-only) |
| `metadata.token_budget` | object | Estimated token cost per level |

### Token budget object

| Field | Type | Description |
|-------|------|-------------|
| `token_budget.level_1` | int | Tokens for SKILL.md (~80) |
| `token_budget.level_2` | int | Tokens for context.md (~140-350) |
| `token_budget.level_3_max` | int | Tokens for largest reference file (~1000-1200) |

## Tier Classification

| Tier | Behavior | Example skills |
|------|----------|---------------|
| `"free"` | Knowledge only, no MCP tools needed | command-reference, show-architecture |
| `"free-hybrid"` | Knowledge + optional MCP execution | macros, programming, lua-scripting, networking |

## Safety Tier Values

| Tier | Meaning |
|------|---------|
| `"SAFE_READ"` | Read-only operations (list, info, cd) |
| `"SAFE_WRITE"` | Modifying operations (go, at, clear, park) |
| `"DESTRUCTIVE"` | Data-altering operations requiring confirmation (store, delete, copy, move) |

## Body Content

After the YAML front matter, SKILL.md contains only:

```markdown
# {{Title}}

{{One-line persona description.}}
```

All instructional content (grep patterns, syntax summaries, MCP bridge behavior, mode/scope/safety) belongs in `context.md`.
