# agent-kb-toolkit

> A set of agent skills that turn any coding-agent harness (Qoder / Claude Code / OpenCode / Codex …) into a disciplined **personal knowledge-base builder** over a plain Markdown directory — no vector database required.
>
> 一套 agent skill,把任意 agent harness 变成纪律严明的**个人知识库工具链**,直接作用于一个 Markdown 目录,起步无需向量库。

`SKILL.md`-based, model-agnostic, works with any tool that discovers skills from `~/.agents/skills/`, `~/.claude/skills/`, or via [`npx skills`](https://github.com/vercel-labs/skills).

---

## Why (design philosophy)

Knowledge work with an agent has two distinct jobs that people usually conflate. This toolkit keeps them separate:

- **Curation(策展)** — a human/LLM *judges* what matters and writes it up. Costs tokens, needs judgment.
- **Transcription(转录)** — *mechanically* copy raw sessions verbatim. Zero tokens, needs determinism, not an LLM.

The core rule the whole toolkit follows:

> **一句话约定进 Memory,多步流程进 Skill,机械活写脚本,必然发生挂 Hook。**
> *Rules → Memory · Workflows → Skill · Deterministic work → scripts · Inevitable events → Hooks.*

That is why deterministic parts (backup, dedup search) are plain Python scripts (0 tokens), and only the judgment parts run as LLM skills.

## The three skills

| Skill | Line | Job | Cost |
|---|---|---|---|
| **save-to-kb** | curation (quick) | Curate a conversation into properly-formatted notes; write-time dedup; compaction-safe | low |
| **expand-note** | curation (deep) | Deepen one note (or a new topic) into textbook-grade content via multi-source web research | high (research) |
| **archive-sessions** | transcription | Verbatim-export session transcripts of each harness to Markdown backups | **~0 tokens** |

```
                你 / You
                   │  (natural language)
        ┌──────────┴───────────┐
   curation line          transcription line
   (LLM judgment)         (deterministic script)
        │                      │
  save-to-kb  ──deepen──▶ expand-note      archive-sessions
        │                      │                  │
        ▼                      ▼                  ▼
   $KB_ROOT (Markdown KB, MOC-indexed)      ~/sessionbackup/<harness>/
        └── grep/read = agentic retrieval ──┘   (feeds compaction-guard)
```

Design notes baked in: **write-before-dedup** keeps recording cost `O(candidates)` not `O(KB)`; **compaction guard** re-grounds curation against on-disk transcripts when context was compacted; **self-extending** adapters + **self-installing** hook recipes let `archive-sessions` grow to new harnesses on its own.

## Requirements

- Python 3.8+ (standard library only — no pip installs)
- Any agent harness that loads `SKILL.md` skills
- A Markdown knowledge base directory (e.g. an Obsidian vault)

## Install

```bash
git clone https://github.com/Criss404/agent-kb-toolkit.git
```

Make the skills discoverable by your harness — copy or symlink each skill folder into your skills directory:

```bash
# Example: shared location scanned by OpenCode / Claude-compatible harnesses
mkdir -p ~/.agents/skills
ln -s "$PWD/agent-kb-toolkit/skills/"* ~/.agents/skills/
# Or per-harness, e.g. Claude Code:  ~/.claude/skills/    Qoder:  ~/.qoder/skills/
```

Then point the toolkit at your knowledge base (add to your shell profile or the harness's `AGENTS.md`):

```bash
export KB_ROOT="/path/to/your/knowledge-base"
```

Optional — auto-backup on session end/compaction: see `skills/archive-sessions/references/hook-recipes.md` for per-harness hook/plugin snippets. The skill can install these for you, but **only after showing you the exact config and getting your confirmation** (see Security).

## Usage

- `记录本次会话` / `save to kb` → curate this session into notes
- `深化 <note>` / `expand note` → upgrade a note to textbook grade
- `备份会话` / `archive sessions` → verbatim backup of transcripts
- Or invoke explicitly: `/save-to-kb`, `/expand-note`, `/archive-sessions`

## Security

`archive-sessions` can write a session-end hook into your harness config (the "self-install" protocol). By design it is **idempotent** and **never writes silently** — it shows you the exact snippet and requires your confirmation first. Editing an agent's config is a known persistence vector; treat *any* skill that mutates your config with the same scrutiny.

## Notes on portability

- **Memory / Skill** are near-standard across harnesses; **Hooks are not** — Qoder & Claude Code share a shell-hook schema, OpenCode uses a JS plugin, Codex differs again. Recipes are provided per harness; unknown harnesses get a fallback protocol.
- Harness-specific details (config paths, event names) are product-level knowledge that changes often — the skills tell the agent to check the harness's own docs rather than hardcoding.

## License

MIT © 2026 Criss404 (KLam111)
