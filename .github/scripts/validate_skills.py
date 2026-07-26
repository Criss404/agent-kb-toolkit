#!/usr/bin/env python3
"""CI guard: validate every skills/*/SKILL.md frontmatter.

Catches the failure class where invalid YAML or missing fields make a
harness silently drop the whole skill (e.g. OpenCode strict parsing).
"""
import re
import sys
from pathlib import Path

import yaml

errors = []
skill_dirs = sorted(p for p in Path("skills").iterdir() if p.is_dir())

for d in skill_dirs:
    f = d / "SKILL.md"
    if not f.is_file():
        errors.append(f"{d}: missing SKILL.md")
        continue
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{f}: no YAML frontmatter block")
        continue
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        errors.append(f"{f}: invalid YAML — {e}")
        continue
    name = meta.get("name", "")
    desc = meta.get("description", "")
    if not name:
        errors.append(f"{f}: missing 'name'")
    elif not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        errors.append(f"{f}: name '{name}' must be lowercase hyphen-case (<=64 chars)")
    elif name != d.name:
        errors.append(f"{f}: name '{name}' != folder '{d.name}'")
    if not desc:
        errors.append(f"{f}: missing 'description'")
    elif "\n" in str(desc):
        errors.append(f"{f}: description must be single-line")
    elif len(str(desc)) > 1024:
        errors.append(f"{f}: description exceeds 1024 chars")

if errors:
    print("SKILL.md validation FAILED:")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
print(f"OK: {len(skill_dirs)} skills validated.")
