# Contributing

Thanks for improving **agent-kb-toolkit**! Issues and PRs are welcome — especially new harness adapters for `archive-sessions`.

## Repo layout

- `skills/<name>/SKILL.md` — the skill itself (required)
- `skills/<name>/scripts/` — deterministic Python helpers (stdlib only)
- `skills/<name>/references/` — long specs, read on demand
- `skills/<name>/assets/` — templates used when producing output

## Adding or editing a skill

Each skill is a folder under `skills/` whose `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: my-skill              # lowercase [a-z0-9-], <=64 chars, MUST equal the folder name
description: One single line, <=1024 chars, third person; lead with trigger phrases.
---
```

The CI (`.github/scripts/validate_skills.py`) enforces:

- `name` is lowercase hyphen-case, `<=64` chars, and equals the folder name
- `description` is present, single-line, and `<=1024` chars

**YAML gotcha:** any frontmatter value with special characters (`:`, `|`, `[`, `]`, quotes …) must be quoted, e.g. `argument-hint: "[a|b]"`. Some harnesses parse YAML strictly and will *silently drop* a skill whose frontmatter is invalid.

Keep skills portable: don't hardcode harness-specific paths or event names in the skill body — tell the agent to consult the harness's own docs, because that knowledge goes stale quickly. Writing rules live in `skills/save-to-kb/references/standards.md`, with good/bad samples in `style-examples.md`.

## Adding a harness adapter (archive-sessions)

See the `ADAPTER REGISTRY` comment in [`archive_sessions.py`](skills/archive-sessions/scripts/archive_sessions.py) — a three-step recipe:

1. If the harness stores sessions as `<project>/<session>.jsonl` in the Qoder/Claude family format, register a one-liner in `ADAPTERS`.
2. Otherwise write an `archive_<tool>()` function (use `archive_opencode()` as a template).
3. Register it in `ADAPTERS`.

## Before opening a PR

```bash
pip install pyyaml
python .github/scripts/validate_skills.py     # SKILL.md frontmatter check
python -m compileall -q skills                # bundled scripts byte-compile
python -m unittest discover -s tests           # script smoke tests
```

All three must pass — CI runs the same. Keep changes focused, and add a bullet under `[Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md).

## Reference

- Agent Skills / SKILL.md spec: https://github.com/anthropics/skills

## License

By contributing, you agree your work is released under the [MIT License](LICENSE).
