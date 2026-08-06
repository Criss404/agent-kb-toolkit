#!/usr/bin/env python3
"""Archive agent-harness session transcripts to markdown backups.

Output layout: <ARCHIVE_BASE>/<harness>/<YYYY-MM-DD>_<project>_<sid8>.md
ARCHIVE_BASE = $AGENT_ARCHIVE_DIR, else $HOME/sessionbackup
Incremental: a session is skipped when its output file is newer than the source.
Usage: archive_sessions.py [qoder|claude|opencode|all] [--full]
  --full  do not truncate tool inputs/outputs (default truncates at 2000 chars)
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TRUNC = None if "--full" in sys.argv else 2000
BASE = Path(os.environ.get("AGENT_ARCHIVE_DIR", Path.home() / "sessionbackup"))

CAVEAT_RE = re.compile(r"Caveat:.*?(?:explicitly asks you to\.|asks you to\.)", re.S)
CMD_BLOCK_RE = re.compile(
    r"<(command-message|command-name|command-args|local-command-stdout)>.*?</\1>", re.S
)
TAG_RE = re.compile(r"<[^>]+>")


def slugify(text, maxlen=36):
    """Make text safe and readable as a filename fragment."""
    text = CMD_BLOCK_RE.sub("", str(text))
    text = TAG_RE.sub("", text)
    text = CAVEAT_RE.sub("", text)
    text = re.sub(r'[\\/:*?"<>|\s]+', "-", text.strip()).strip("-_.")
    return text[:maxlen].strip("-_.") or ""


def derive_title(records):
    """Return (session name, has_official_title).
    优先级:官方标题记录 > 最近一次 /branch 之后的首条用户输入(fork 分支的
    第一句话,母本历史里没有它) > 全文首条用户输入。"""
    title = ""
    for rec in records:
        if rec.get("type") == "ai-title" and rec.get("aiTitle"):
            title = rec["aiTitle"]  # Qoder:取最后一条为当前标题(注:手动 /rename 的名字存于加密 state,读不到)
        elif rec.get("type") == "summary" and rec.get("summary"):
            title = rec["summary"]  # Claude Code 同族格式
    if title:
        return slugify(title), True

    def first_user_text(start):
        for rec in records[start:]:
            if rec.get("type") != "user":
                continue
            c = rec.get("message", {}).get("content", "")
            if isinstance(c, list):
                c = " ".join(
                    b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"
                )
            name = slugify(c)
            if name:
                return name
        return ""

    last_branch = -1
    for i, rec in enumerate(records):
        if rec.get("type") == "user":
            c = rec.get("message", {}).get("content", "")
            # 局限:仅识别 Qoder/Claude 的 /branch 命令痕迹;其他 harness 的
            # 会话分叉命令(如某家的 /fork)需在此另加匹配串,否则静默漏检
            if isinstance(c, str) and "<command-name>/branch</command-name>" in c:
                last_branch = i
    if last_branch >= 0:
        name = first_user_text(last_branch + 1)
        if name:
            return name, False
    return first_user_text(0), False


def log(msg):
    print(msg, flush=True)


def trunc(text):
    if TRUNC and len(text) > TRUNC:
        return text[:TRUNC] + f"\n…[truncated, total {len(text)} chars]"
    return text


def ts_to_str(ts):
    try:
        if isinstance(ts, (int, float)):
            if ts > 1e12:
                ts = ts / 1000
            return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return str(ts).replace("T", " ").split(".")[0]
    except Exception:
        return str(ts)


def render_content(content, lines):
    """Render a message content (string or block list) into markdown lines."""
    if isinstance(content, str):
        lines.append(content)
        return
    if not isinstance(content, list):
        lines.append(str(content))
        return
    for block in content:
        if not isinstance(block, dict):
            lines.append(str(block))
            continue
        btype = block.get("type", "")
        if btype == "text":
            lines.append(block.get("text", ""))
        elif btype == "thinking":
            lines.append("> [thinking omitted]")
        elif btype == "tool_use":
            name = block.get("name", "?")
            args = json.dumps(block.get("input", {}), ensure_ascii=False)
            lines.append(f"> 🔧 tool_use **{name}**: `{trunc(args)}`")
        elif btype == "tool_result":
            inner = block.get("content", "")
            if isinstance(inner, list):
                inner = "\n".join(
                    b.get("text", "") for b in inner if isinstance(b, dict) and b.get("type") == "text"
                )
            lines.append(f"> 📄 tool_result:\n```\n{trunc(str(inner))}\n```")
        else:
            lines.append(f"> [{btype} block omitted]")


def convert_jsonl(src: Path, harness: str, project: str) -> int:
    """Convert one Qoder/Claude-style JSONL session file. Returns 1 if written."""
    sid8 = src.stem[:8]
    records = []
    for raw in src.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    lines, first_ts = [], None
    for rec in records:
        rtype = rec.get("type")
        if rtype not in ("user", "assistant"):
            continue
        ts = rec.get("timestamp", "")
        first_ts = first_ts or ts
        role = "🧑 User" if rtype == "user" else "🤖 Assistant"
        lines.append(f"\n## {role} · {ts_to_str(ts)}\n")
        render_content(rec.get("message", {}).get("content", ""), lines)
    if not lines:
        return 0
    title, official = derive_title(records)
    name = title or project
    # 有官方标题:日期用会话首条消息时间(会话开始日)。
    # 无官方标题(常见于 fork 分支,历史继承自母本、连开场时间都一样):
    # 日期改用文件最后修改日,让分支按"最近活动"排序可辨认。
    if official and first_ts:
        date = ts_to_str(first_ts)[:10]
    else:
        date = datetime.fromtimestamp(src.stat().st_mtime).strftime("%Y-%m-%d")
    out = BASE / harness / f"{date}_{name}_{sid8}.md"
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Session {src.stem}\n\n- harness: {harness}\n- project: {project}\n"
        f"- source: {src}\n- exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n"
    )
    out.write_text(header + "\n".join(lines), encoding="utf-8")
    return 1


def archive_jsonl_tree(root: Path, harness: str) -> tuple[int, int]:
    done = total = 0
    if not root.is_dir():
        log(f"[{harness}] skip: {root} not found")
        return 0, 0
    for src in sorted(root.glob("*/*.jsonl")):
        total += 1
        project = src.parent.name.strip("-").replace("/", "-") or "default"
        done += convert_jsonl(src, harness, project)
    return done, total


def archive_opencode() -> tuple[int, int]:
    try:
        out = subprocess.run(
            ["opencode", "session", "list", "--format", "json"],
            capture_output=True, text=True, timeout=120,
        )
        sessions = json.loads(out.stdout)
    except Exception as e:
        log(f"[opencode] skip: cannot list sessions ({e})")
        return 0, 0
    done = 0
    for s in sessions:
        sid = s.get("id", "")
        date = ts_to_str(s.get("created", ""))[:10]
        project = (s.get("directory", "") or "global").strip("/").replace("/", "-")
        name = slugify(s.get("title", "")) or project
        dst = BASE / "opencode" / f"{date}_{name}_{sid[-8:]}.md"
        if dst.exists() and dst.stat().st_mtime * 1000 >= s.get("updated", 0):
            continue
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tf:
                tmp_path = tf.name
            try:
                with open(tmp_path, "w") as fh:
                    subprocess.run(["opencode", "export", sid], stdout=fh,
                                   stderr=subprocess.DEVNULL, timeout=120, check=True)
                data = json.loads(Path(tmp_path).read_text(encoding="utf-8", errors="replace"))
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except Exception as e:
            log(f"[opencode] export failed for {sid}: {e}")
            continue
        lines = [
            f"# Session {sid}\n\n- harness: opencode\n- title: {s.get('title', '')}\n"
            f"- project: {project}\n- exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n"
        ]
        for m in data.get("messages", []):
            info = m.get("info", m)
            role = "🧑 User" if info.get("role") == "user" else "🤖 Assistant"
            lines.append(f"\n## {role} · {ts_to_str(info.get('time', {}).get('created', ''))}\n")
            for part in m.get("parts", []):
                ptype = part.get("type", "")
                if ptype == "text":
                    lines.append(part.get("text", ""))
                elif ptype == "tool":
                    name = part.get("tool", "?")
                    state = part.get("state", {})
                    args = json.dumps(state.get("input", {}), ensure_ascii=False)
                    result = str(state.get("output", ""))
                    lines.append(f"> 🔧 tool **{name}**: `{trunc(args)}`")
                    if result:
                        lines.append(f"> 📄 result:\n```\n{trunc(result)}\n```")
                elif ptype in ("step-start", "step-finish", "reasoning"):
                    continue
                else:
                    lines.append(f"> [{ptype} part omitted]")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text("\n".join(lines), encoding="utf-8")
        done += 1
    return done, len(sessions)


# ---------------------------------------------------------------------------
# ADAPTER REGISTRY — 新增 harness 适配器只需三步:
#   1. 若其 session 是「项目目录/会话.jsonl + {type, message:{role, content}}」
#      同族格式(Qoder/Claude Code 即此类),直接注册一行:
#      "<tool>": lambda: archive_jsonl_tree(Path.home()/".<tool>"/"projects", "<tool>")
#   2. 否则仿照 archive_opencode() 写一个 archive_<tool>() 函数。
#      探测提示:~/.<tool>/(sessions|projects|history)/、~/.local/share/<tool>/、
#      或该工具自带的 session list / export CLI。
#   3. 在下方 ADAPTERS 注册,并把更新同步到各 harness 的本工具包安装位置。
# ---------------------------------------------------------------------------
ADAPTERS = {
    "qoder": lambda: archive_jsonl_tree(Path.home() / ".qoder" / "projects", "qoder"),
    "claude": lambda: archive_jsonl_tree(Path.home() / ".claude" / "projects", "claude"),
    "opencode": archive_opencode,
}


def main():
    if "--list" in sys.argv:
        log("Registered adapters: " + ", ".join(ADAPTERS))
        return
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    target = args[0] if args else "all"
    if target != "all" and target not in ADAPTERS:
        log(f"Unknown harness '{target}'. Registered: {', '.join(ADAPTERS)} (or 'all').")
        log("To add support, follow the ADAPTER REGISTRY comment in this file.")
        sys.exit(1)
    results = {}
    for name, fn in ADAPTERS.items():
        if target in (name, "all"):
            results[name] = fn()
    log(f"\nArchive base: {BASE}")
    for name, (done, total) in results.items():
        log(f"  {name}: {done} new/updated, {total - done} up-to-date (of {total})")


if __name__ == "__main__":
    main()
