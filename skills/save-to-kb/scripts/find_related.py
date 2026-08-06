#!/usr/bin/env python3
"""Find existing KB notes related to given keywords (write-time dedup helper).

Usage: KB_ROOT=<知识库根目录> find_related.py <关键词1> [关键词2 ...]
KB_ROOT env var is required (agent passes it explicitly); missing -> hard error,
never guess a path.
Scans only curated dirs declared in <KB>/知识库结构.md (```curated-dirs block);
if the structure file is missing, scans the whole KB root minus SKIP_DIRS.
Prints a short ranked candidate list. The agent then judges ONLY these
candidates (O(candidates) tokens) instead of scanning the whole KB.
"""
import os
import re
import sys
from pathlib import Path

_kb_env = os.environ.get("KB_ROOT")
if not _kb_env:
    sys.exit("ERROR: 未设置环境变量 KB_ROOT / KB_ROOT is not set. Usage: KB_ROOT=<path> find_related.py <keyword...>")
KB = Path(_kb_env).expanduser()
SKIP_DIRS = {".obsidian", ".git", ".trash"}
STRUCTURE_FILES = ("知识库结构.md", "STRUCTURE.md")


def curated_dirs():
    """Read curated dir list from the structure file's ```curated-dirs block."""
    for name in STRUCTURE_FILES:
        f = KB / name
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"```curated-dirs\n(.*?)```", text, re.S)
        if m:
            dirs = [KB / line.strip() for line in m.group(1).splitlines() if line.strip()]
            return [d for d in dirs if d.is_dir()]
    return None


def main():
    kws = [k.lower() for k in sys.argv[1:] if k.strip()]
    if not kws:
        print("Usage: find_related.py <keyword> [...]")
        return
    if not KB.is_dir():
        print(f"ERROR: 知识库根目录不存在 / KB root does not exist: {KB}(用环境变量 KB_ROOT 指定 / set via KB_ROOT)", file=sys.stderr)
        sys.exit(1)
    roots = curated_dirs()
    if roots is None:
        print("WARN: 结构文件缺失或未声明 curated-dirs,扫描整个知识库 / structure file missing curated-dirs, scanning whole KB.", file=sys.stderr)
        roots = [KB]
    hits = []
    seen = set()
    for root in roots:
        for md in root.rglob("*.md"):
            if md in seen:
                continue
            seen.add(md)
            if any(part in SKIP_DIRS for part in md.parts):
                continue
            try:
                head = md.read_text(encoding="utf-8", errors="replace")[:2000]
            except OSError:
                continue
            headings = " ".join(re.findall(r"^#{1,3} .+$", head, re.M))
            fm = head.split("---")[1] if head.startswith("---") and head.count("---") >= 2 else ""
            surface = f"{md.name} {headings} {fm}".lower()
            score = sum(1 for k in kws if k in surface)
            if score:
                m = re.search(r"^# (.+)$", head, re.M)
                hits.append((score, str(md.relative_to(KB)), m.group(1) if m else md.stem))
    hits.sort(key=lambda x: (-x[0], x[1]))
    if not hits:
        print("NO_MATCH: 无相关既有笔记,可新建。")
        return
    print(f"发现 {len(hits)} 篇候选(按命中数排序,请逐个判断是否已覆盖待记录知识点):")
    for score, rel, title in hits[:10]:
        print(f"  [{score}] {rel} — {title}")
    if len(hits) > 10:
        print(f"  …(其余 {len(hits) - 10} 篇略,命中数更低)")


if __name__ == "__main__":
    main()
