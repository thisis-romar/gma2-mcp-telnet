---
title: Contributing a New Skill
description: Step-by-step guide for adding a new skill to the ma2-onPC-MCP skill library
version: 1.0.0
created: 2026-03-15T00:00:00Z
last_updated: 2026-03-15T00:00:00Z
---

# Contributing a New Skill

## Directory structure

Each skill lives in `skills/<skill-name>/` with this layout:

```
skills/<skill-name>/
├── SKILL.md              # Level 1: Pure YAML metadata + 1-line persona
├── context.md            # Level 2: Quick answers, grep patterns, mode, scope, safety
└── references/           # Level 3: Deep reference material (loaded on demand)
    ├── <topic-1>.md
    └── <topic-2>.md
```

## Step-by-step

### 1. Create the directory

```bash
mkdir -p skills/<skill-name>/references
```

### 2. Create SKILL.md from template

Copy `skills/_templates/SKILL.md.template` and fill in all `{{placeholders}}`:

- **`name`**: Use `gma2-<skill-name>` format
- **`tier`**: `"free"` for knowledge-only, `"free-hybrid"` if MCP tools are used
- **`triggers`**: 5-10 keywords that should route to this skill
- **`depends_on`**: List other skill `name` values this skill needs (e.g. `["gma2-command-reference"]`)
- **`max_risk_tier`**: Highest safety tier any operation in this skill can invoke
- **`tools_required`**: MCP tool names needed for hybrid execution (empty for knowledge-only)
- **`token_budget`**: Estimate tokens per level (Level 1 ~80, Level 2 ~300, Level 3 varies)

### 3. Create context.md from template

Copy `skills/_templates/context.md.template` and fill in:

- **Persona**: Detailed role description
- **Quick answers**: Grep patterns pointing to specific sections in reference files
- **Mode**: Knowledge only or Hybrid
- **Scope**: Bullet list of topics covered
- **Safety**: List applicable risk tiers
- **MCP bridge**: Reference `skills/_shared/mcp-bridge-notice.md` plus skill-specific details

### 4. Write reference files

Create one or more `.md` files in `references/`. Guidelines:

- Use heading-based structure (`## Section`) for grep-friendly lookups
- Keep each file focused on one topic area
- Include code examples in monospace blocks
- Add YAML front matter (title, description, version, created, last_updated)

### 5. Update INDEX.md

Add a new section to `skills/INDEX.md` mapping topics to grep patterns:

```markdown
## <Skill Name>

| Topic | File | Grep pattern |
|-------|------|-------------|
| Topic 1 | `skills/<skill-name>/references/<file>.md` | `^## Section` |
```

### 6. Register in plugin.json

Add the SKILL.md path to the `skills` array in `plugin.json`:

```json
"skills": [
  ...existing skills...,
  "skills/<skill-name>/SKILL.md"
]
```

## Validation checklist

- [ ] SKILL.md is ≤ 25 lines (metadata + 1-line persona only)
- [ ] SKILL.md has all required metadata fields (see `skills/SCHEMA.md`)
- [ ] context.md has: Persona, Quick answers, Deep dives, MCP bridge, Mode, Scope, Safety, Boundaries
- [ ] All `.md` files have YAML front matter
- [ ] INDEX.md updated with grep patterns for new skill
- [ ] plugin.json updated with new SKILL.md path
- [ ] `make test` passes (skill changes are markdown-only, should not break tests)
