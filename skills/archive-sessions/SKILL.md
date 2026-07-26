---
name: archive-sessions
description: 把各家 agent harness(Qoder/OpenCode/Claude Code)的 session 对话记录逐字导出为 markdown 备份档案,存到 ~/sessionbackup/<harness>/ 下。触发场景:用户说"备份会话/归档对话/导出session/完全记录/archive sessions"等。这是确定性转录(transcription),与知识库策展(save-to-kb)互补,备份档案不进知识库。
argument-hint: "[qoder|claude|opencode|all] [--full]"
---

# Archive Sessions(会话备份归档)

## Overview

运行捆绑脚本,把 agent harness 的原始 session 记录转成可读的 markdown 备份。这是**机械转录任务,全部逻辑在脚本里**——不要用 LLM 复述对话内容(context 压缩后无法保证逐字保真)。

## 执行方式

```bash
python3 <本skill目录>/scripts/archive_sessions.py [qoder|claude|opencode|all] [--full]
```

- 不带参数 = `all`(依次处理 Qoder、Claude Code、OpenCode)
- `--full`:不截断工具调用的输入/输出(默认截断到 2000 字符)
- 脚本自带增量逻辑:输出文件比源新则跳过,可放心重复执行

## 输出位置

```
${AGENT_ARCHIVE_DIR:-~/sessionbackup}/<harness>/<日期>_<项目>_<sessionID后8位>.md
```

- 默认 `~/sessionbackup/`;设置环境变量 `AGENT_ARCHIVE_DIR` 可重定向(如 WSL 上指向 /mnt/d 防止 WSL 重置丢失)
- 备份档案**不进知识库**,与 save-to-kb 的策展笔记严格分离

## 数据来源(适配器)

| Harness | 来源 | 方式 |
|---|---|---|
| Qoder | `~/.qoder/projects/**/*.jsonl` | 直接解析 |
| Claude Code | `~/.claude/projects/**/*.jsonl` | 直接解析(同族格式,目录不存在则跳过) |
| OpenCode | `opencode session list/export` | 调 CLI 导出(需 opencode 在 PATH) |

## 自扩展协议(接入新 harness,如 Codex)

当用户要求备份一个**尚无适配器**的 harness 时,不要拒绝,按此流程新增适配器(一次性判断工作,之后转录全归脚本):

1. 探测该 harness 的 session 存储:依次检查 `~/.<tool>/(sessions|projects|history)/`、`~/.local/share/<tool>/`,以及该工具自带的 `session list` / `export` 命令
2. 抽样读 1~2 个 session 文件,确认消息结构(role / content / timestamp 字段在哪)
3. 打开 `scripts/archive_sessions.py`,按文件内 **ADAPTER REGISTRY** 注释的三步说明新增并注册适配器
4. 用真实数据测试:`python3 scripts/archive_sessions.py <新harness>`,抽查输出 markdown 是否完整
5. 若你在多个 harness 安装了本工具包,把更新同步到各安装位置

`--list` 参数可查看当前已注册的适配器。

## Hook 自安装协议(首次在新 harness 使用时执行)

本 skill 支持把"session 结束自动备份"的绑定落地到当前 harness。每次执行本 skill 时,先走第 0 步:

0. **幂等检查**:按下表命令检测当前 harness 是否已有绑定。已有 → 跳过本节;没有 → 读取 `references/hook-recipes.md` 中对应配方,**向用户展示将写入的完整配置片段,征得明确同意后**再写入。
   **安全红线:禁止静默修改任何配置文件**——自改配置是持久化攻击的常见载体,必须全程透明、用户确认。

| Harness | 幂等检查命令 | 配方 |
|---|---|---|
| Qoder | `grep -q auto-archive-sessions ~/.qoder/settings.json` | recipes 第 1 节(hooks.SessionEnd) |
| Claude Code | `grep -q auto-archive-sessions ~/.claude/settings.json` | recipes 第 2 节(同族 schema) |
| OpenCode | `ls ~/.config/opencode/plugin/archive-sessions.js` | recipes 第 3 节(JS plugin) |
| 其他 harness | — | 查该家官方文档的 session 生命周期 hook/plugin 机制,做等效绑定;完成后把新配方补进 recipes 并同步两份 skill 副本 |

## 执行后必做

1. 把脚本输出的统计(各 harness 新增/跳过数)报告给用户
2. 若出现 "export failed" 或 "skip" 行,原样告知用户并解释原因

## 已知边界

- session 文件格式属产品/厂商层知识(月级半衰期),harness 大版本升级后若解析失败,需检查格式变化并更新脚本适配器
- 正在进行中的 session 每次运行都会重新导出(源文件持续增长,属正常增量行为)
- Qoder 与 OpenCode 适配器经真实数据验证;Claude Code 适配器基于同族格式实现,**尚未经真实数据验证**,首次使用时抽查输出

## Resources

- `scripts/archive_sessions.py`:全部转换逻辑(路径解析、三个适配器、增量判断)
- `references/hook-recipes.md`:各 harness 的自动备份绑定配方(自安装协议用)
