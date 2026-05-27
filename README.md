# Personal Codex Skills

这个仓库用于公开分享我自己编写和维护的 Codex skills。

每个 skill 都是一个独立目录，包含 `SKILL.md` 作为入口说明，并按需附带脚本、参考文档、模板或 agent 配置。仓库目标是把可复用的工作流沉淀下来，方便自己、团队或社区用户在不同项目里稳定复用。

## Skills

| Skill | 说明 | 安装 |
| --- | --- | --- |
| `plugin-store-assets` | 生成浏览器插件或扩展商店素材，包括 Chrome Web Store 文案、图标、截图、推广图、多语言 README 和通信架构图。 | `$skill-installer install https://github.com/merrier/skills/tree/main/plugin-store-assets` |

发布到 GitHub 并设为 public 后，其他用户就可以通过上面的命令安装。

## Install

推荐使用 `$skill-installer` 从公开 GitHub 仓库安装：

```bash
$skill-installer install https://github.com/merrier/skills/tree/main/plugin-store-assets
```

安装完成后，重启 Codex 以加载新的 skill。

如果只是本机开发调试，也可以将 skill 目录软链接到用户 skills 目录：

```bash
mkdir -p ~/.codex/skills
ln -s /Users/bytedance/repos/mine/skills/plugin-store-assets ~/.codex/skills/plugin-store-assets
```

## Repository Structure

```text
.
├── README.md
└── plugin-store-assets/
    ├── SKILL.md
    ├── LICENSE.txt
    ├── agents/
    ├── references/
    └── scripts/
```

## Skill Layout

推荐每个 skill 使用下面的结构：

```text
skill-name/
├── SKILL.md          # skill 入口，包含名称、触发描述和工作流
├── LICENSE.txt       # skill 许可证
├── agents/           # 可选，Codex App UI 元数据
├── references/       # 可选，规格、示例、参考资料
├── scripts/          # 可选，可复用脚本
└── assets/           # 可选，模板或静态资源
```

## Create A New Skill

新增 skill 时建议保持目录独立、职责单一：

1. 创建 `skill-name/SKILL.md`。
2. 在 frontmatter 中补充清晰的 `name` 和 `description`。
3. 把确定性、重复性高的逻辑放到 `scripts/`。
4. 把规格、尺寸、示例和检查清单放到 `references/`。
5. 补充 `LICENSE.txt`。
6. 在本 README 的 `Skills` 表格中登记。

## Public Release Checklist

- 确认仓库不包含私有信息、内部路径、密钥、token 或客户数据。
- 确认脚本不会依赖本机私有配置，必要时在 `SKILL.md` 中写清依赖。
- 确认 `SKILL.md` 的触发描述覆盖典型用户说法，并说明边界。
- 确认每个公开 skill 都带有 `LICENSE.txt`。
- 在真实项目中试跑一次典型任务，确认工作流可用。

## License

每个 skill 的许可证放在对应 skill 目录内的 `LICENSE.txt`。
