# Hook 绑定配方(自安装协议用)

> 使用前提:已通过 SKILL.md 第 0 步的幂等检查(当前 harness 无绑定),且**已向用户展示片段并获得同意**。
> 通用原则:脚本路径优先用 `~/.agents/skills/archive-sessions/scripts/archive_sessions.py`(跨 harness 共享副本);备份目标只选当前 harness 自己(各绑各的,避免每家退出都全量扫描)。

## 1. Qoder(`~/.qoder/settings.json`)

在顶层 JSON 中合并(已有 `hooks` 键则只追加 `SessionEnd` 数组项):

```json
"hooks": {
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 $HOME/.agents/skills/archive-sessions/scripts/archive_sessions.py qoder >> $HOME/sessionbackup/archive-hook.log 2>&1",
          "name": "auto-archive-sessions",
          "async": true,
          "timeout": 60
        }
      ]
    }
  ]
}
```

写入后:用 `python3 -c "import json; json.load(open(路径))"` 验证 JSON 合法,再独立跑一次命令确认可执行。

## 2. Claude Code(`~/.claude/settings.json`)

与 Qoder 同族 schema,事件同名。差异:命令的备份目标改为 `claude`,脚本路径用共享副本:

```json
"hooks": {
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 $HOME/.agents/skills/archive-sessions/scripts/archive_sessions.py claude >> $HOME/sessionbackup/archive-hook.log 2>&1",
          "name": "auto-archive-sessions",
          "async": true,
          "timeout": 60
        }
      ]
    }
  ]
}
```

## 3. OpenCode(JS plugin)

OpenCode 没有 shell hook,用 plugin 事件系统。创建 `~/.config/opencode/plugin/archive-sessions.js`:

```js
// auto-archive-sessions: 在 session 空闲时增量备份 OpenCode 会话
export default async ({ $ }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        await $`python3 ${process.env.HOME}/.agents/skills/archive-sessions/scripts/archive_sessions.py opencode`
          .quiet()
          .nothrow()
      }
    },
  }
}
```

注意事项:
- plugin 目录内的 `*.js` 自动发现,无需注册;改动后需重启 OpenCode 生效
- 已知边界:`opencode run` 短命进程可能在 plugin 完成前退出(上游 issue #23380);TUI 交互模式正常
- 事件名/plugin API 属产品层知识(月级半衰期),失效时以 OpenCode 内置 customize-opencode skill 或官方文档为准

## 4. 新 harness 配方模板

为未收录的 harness 添加绑定后,按此格式把配方补进本文件:

```
## N. <Harness 名>(<配置文件或机制>)
<绑定片段>
注意事项:<触发时机、已知坑、验证方式>
```

并把更新同步到你所有 harness 的本工具包安装位置。
