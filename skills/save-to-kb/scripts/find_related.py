#!/usr/bin/env python3
"""Find existing KB notes related to given keywords (write-time dedup helper).

Usage: find_related.py <关键词1> [关键词2 ...]
Searches filenames, headings and frontmatter of all *.md under the KB root,
prints a short ranked candidate list. The agent then judges ONLY these
candidates (O(candidates) tokens) instead of scanning the whole KB.
"""
import re
import sys
import os
from pathlib import Path

_KB_RAW = os.environ.get("KB_ROOT", "").strip()
KB = Path(_KB_RAW).expanduser() if _KB_RAW else None
SKIP_DIRS = {".obsidian", ".git"}


def main():
    if KB is None or not KB.is_dir():
        print("ERROR: 环境变量 KB_ROOT 未设置或不是有效目录。请先 `export KB_ROOT=/path/to/your/knowledge-base`。", file=sys.stderr)
        sys.exit(1)
    kws = [k.lower() for k in sys.argv[1:] if k.strip()]
    if not kws:
        print("Usage: find_related.py <keyword> [...]")
        return
    hits = []
    for md in KB.rglob("*.md"):
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
