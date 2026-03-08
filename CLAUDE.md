---
title: Project Rules
description: Agent conventions and standards for the gma2-mcp-telnet repository
version: 1.2.0
created: 2026-03-01T00:00:00Z
last_updated: 2026-03-07T00:00:00Z
---

# Project Rules

## Markdown Front Matter

All `.md` files in this repository **must** include YAML front matter (`---` fences) at the top of the file.

### Required fields

| Field | Format | Description |
|-------|--------|-------------|
| `title` | string | Document title (matches the `# H1` heading) |
| `description` | string | One-line summary of the document's purpose |
| `version` | semver | `MAJOR.MINOR.PATCH` — bump PATCH for fixes, MINOR for new content, MAJOR for restructures |
| `created` | ISO 8601 | `YYYY-MM-DDTHH:MM:SSZ` — set once when the file is created, never changed |
| `last_updated` | ISO 8601 | `YYYY-MM-DDTHH:MM:SSZ` — update every time the file content changes |

### Rules

1. **New `.md` files** — add front matter before writing any content.
2. **Editing existing `.md` files** — update `last_updated` to the current date/time. Bump `version` if the change is non-trivial (typo fixes don't require a bump).
3. **Do not** backfill `created` dates — use the actual date the file was created.
4. **Template:**

```yaml
---
title: Document Title
description: Brief purpose of this document
version: 1.0.0
created: YYYY-MM-DDTHH:MM:SSZ
last_updated: YYYY-MM-DDTHH:MM:SSZ
---
```

---

## Project Identity

- **Canonical local path:** `C:\Users\romar\gma2-mcp-telnet`
- **Remote:** `https://github.com/thisis-romar/gma2-mcp-telnet.git`
- **Note:** A secondary clone exists at `C:\Users\romar\onPC-Telnet-mcp` pointing to the same remote. Always work in `gma2-mcp-telnet` unless explicitly told otherwise.

---

## Development Workflow

### Running tests
```bash
uv run pytest --tb=short -q
```
- Expected baseline on `main`: **754 passed, 27 skipped** (live telnet tests skip without a console)
- Never force live tests to run; the skip is intentional

### Dependency management
```bash
uv sync   # install/update all deps including dev
```

### Never commit
- `.claude/settings.local.json` — machine-specific Claude Code permissions, always keep out of commits

### Branch conventions
- Feature branches branch from `main`
- Remote branches `claude/*` are Claude-authored; `copilot/*` are Copilot-authored
- After merging a branch: delete both local and remote (`git push origin --delete <branch>` + `git branch -d <branch>`)

---

## Architecture Quick Reference

| Layer | Path | Notes |
|-------|------|-------|
| MCP server | `src/server.py` | FastMCP, 28 `@mcp.tool` definitions |
| Command builders | `src/commands/` | Pure functions → MA2 command strings |
| Vocabulary / safety | `src/vocab.py` | Schema v2.0, 148 keywords, `classify_token()` |
| Keyword JSON | `src/grandMA2_v3_9_telnet_keyword_vocabulary.json` | Schema v2.0 with categories + aliases |
| Telnet client | `src/telnet_client.py` | Async telnet I/O |
| Navigation | `src/navigation.py` | High-level async cd/list API (orchestrates command builder + telnet + prompt parser) |
| Prompt parser | `src/prompt_parser.py` | Extracts current object-tree location from raw telnet output |
| Client manager | `src/tools.py` | Global GMA2 client instance used by server.py |
| Tests | `tests/` | pytest, no live console required for unit tests |
