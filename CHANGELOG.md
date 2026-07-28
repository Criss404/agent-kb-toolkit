# Changelog

All notable changes to **agent-kb-toolkit** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-07-27

### Added
- **`skills/save-to-kb/references/style-examples.md`** — a style-calibration file with paired *good / bad* writing samples (acronym-piling, missing glosses for terms and proper nouns, over-dense sentences). Agents read it before writing so notes stay low-density and readable.
- **`CONTRIBUTING.md`** — how to add a skill or an `archive-sessions` harness adapter, the `SKILL.md` frontmatter rules (including the YAML-quoting gotcha), and the pre-PR checks.
- **`tests/`** — smoke tests for the bundled scripts (`find_related.py`, `archive_sessions.py`), run in CI via `unittest discover`.

### Changed
- **`skills/save-to-kb/references/standards.md` — §3 Writing rules** — added four rules and a pointer to `style-examples.md`:
  - **Prose, not compressed bullets** — arrows (`→`), slash-lists, and `×` must not act as sentence connectors; they are allowed only in tables, code blocks, and checklists.
  - **Avoid coined jargon** — any in-house slogan or metaphor gets a plain-language explanation on first use.
  - **Don't pile terms** — introduce at most one new term/acronym per sentence; unpack parallel terms, each with its full name.
  - **Gloss proper nouns** — organizations, products, models, tools, libraries, protocols, and datasets get a one-line "what it is" on first mention.
- **`README.md` / `README.zh-CN.md`** — Quick Start now lists the per-harness skills directory (Claude Code, Qoder, OpenCode, shared).

[Unreleased]: https://github.com/Criss404/agent-kb-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Criss404/agent-kb-toolkit/releases/tag/v0.1.0
