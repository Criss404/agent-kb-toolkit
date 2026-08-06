# Changelog

All notable changes to **agent-kb-toolkit** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **`skills/save-to-kb` — cold-start bootstrap** — when the KB root has no structure file (`知识库结构.md` / `STRUCTURE.md`), the skill asks the user and scaffolds one from `assets/structure-template.md` instead of guessing the layout.
- **`skills/save-to-kb/assets/ops-template.md`** — skeleton/recipe template for How-to operation manuals (骨架-配方分离: cross-tool skeleton + per-harness recipe with verification dates).
- **`skills/save-to-kb` — operation-manual mode (模式 C)** — records operations as skeleton + per-harness recipes; plain-language sentences with minimal jargon, knowledge linked not expanded.
- **`skills/save-to-kb/references/standards.md` — §6 depth calibration** — L0–L5 tech-stack depth rules; summary-level and teaching-level notes share the same writing quality bar.
- **`skills/save-to-kb/scripts/find_related.py` — curated-dirs scanning** — reads the ````curated-dirs```` block of the structure file; falls back to whole-KB scan when absent; missing `KB_ROOT` is now a hard error.
- **`skills/archive-sessions` — fork-aware session titles** — prefers the first user message after a `/branch` fork marker, so forked sessions no longer inherit the parent's title.
- **`skills/expand-note` — write-time dedup for new topics** — runs `find_related.py` before creating a new-topic note; human-navigation-layer maintenance is now a conditional clause driven by the structure file.

### Changed
- **`skills/save-to-kb/SKILL.md`** — the 1.5 compression-guard clause now invokes archive-sessions via an install-dir placeholder instead of a hardcoded path; human-navigation-layer step is conditional on the structure file declaring one.
- **`skills/save-to-kb/references/standards.md`** — prose rules keep their generic form without personal examples.
- **`skills/save-to-kb/references/style-examples.md`** — example command uses a repo-relative path.
- **`skills/expand-note/SKILL.md`** — removed personal series prefix from the description; internal references use in-toolkit relative paths.
- **`skills/archive-sessions/*`** — install-sync instructions generalized to "sync to all installed harnesses".

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
