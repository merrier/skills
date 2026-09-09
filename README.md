# Personal Codex Skills

这个仓库用于公开分享我自己编写和维护的 Codex skills。

每个 skill 都是一个独立目录，包含 `SKILL.md` 作为入口说明，并按需附带脚本、参考文档、模板或 agent 配置。仓库目标是把可复用的工作流沉淀下来，方便自己、团队或社区用户在不同项目里稳定复用。

## Skills

| Skill | 说明 | 安装 |
| --- | --- | --- |
| `plugin-store-assets` | 生成浏览器插件或扩展商店素材，包括 Chrome Web Store 文案、图标、截图、推广图、多语言 README 和通信架构图。 | `$skill-installer install https://github.com/merrier/skills/tree/main/plugin-store-assets` |
| `toy-model-info` | 从模型实拍、包装及货号识别产品，优先用 AnySearch 检索，保存逐项来源与核实状态，供封面和发布复用。 | `$skill-installer install https://github.com/merrier/skills/tree/main/toy-model-info` |
| `toy-cover` | 根据汽车模型与玩具实拍，按画幅分别选图，确认主副标题后制作多比例封面。 | `$skill-installer install https://github.com/merrier/skills/tree/main/toy-cover` |
| `ego-publish` | 使用 Ego lite 统一确认发布方案，依次向小红书、B站、抖音和视频号发布；各平台独立标签页，完成后保留结果供检查。 | `$skill-installer install https://github.com/merrier/skills/tree/main/ego-publish` |

发布到 GitHub 并设为 public 后，其他用户就可以通过上面的命令安装。

## Install

推荐使用 `$skill-installer` 从公开 GitHub 仓库安装：

```bash
$skill-installer install https://github.com/merrier/skills/tree/main/plugin-store-assets
$skill-installer install https://github.com/merrier/skills/tree/main/toy-model-info
$skill-installer install https://github.com/merrier/skills/tree/main/toy-cover
$skill-installer install https://github.com/merrier/skills/tree/main/ego-publish
```

安装完成后，重启 Codex 以加载新的 skill。

`toy-model-info` 优先复用已安装的 [AnySearch skill](https://github.com/anysearch-ai/anysearch-skill) 检索及提取原文；不可用时可使用用户允许的现有搜索工具，不自动安装或注册服务。资料保存在各模型素材目录的 `模型信息.md`，区分已核实、用户提供、待核实与冲突信息。`toy-cover` 和 `ego-publish` 优先读取这份资料，缺少关键参数时可调用已安装的 `toy-model-info` 补充；资料整理不代替文案确认或平台发布授权。

`toy-cover` 使用宿主环境提供的图像生成／编辑工具；`ego-publish` 另外依赖 Ego lite 与 `ego-browser` skill，各平台需登录并按方案获得发布授权。它使用完整正文的统一发布清单，核对素材指纹后续做；个人偏好保存在仓库外的本机配置。清单、配置和核验方法见 [发布清单约定](ego-publish/references/publish-package.md)。仓库不包含素材照片、账号登录状态或历史发布记录。

如果只是本机开发调试，也可以将 skill 目录软链接到用户 skills 目录：

```bash
mkdir -p ~/.codex/skills
ln -s /path/to/skills/plugin-store-assets ~/.codex/skills/plugin-store-assets
```

## Maintain And Sync

维护时以本地 Git 仓库为唯一源文件，将需要的 skill 目录软链接到项目的 `.agents/skills/`，这样编辑项目中的 skill 就会直接修改仓库内容，不需要维护两份副本。

在用户已明确授权持续同步的工作区，每次完成 skill 更新后，按 [AGENTS.md](AGENTS.md) 校验、检查差异、限定范围提交、推送并核验远端提交。此流程由助手完成一次更新时触发，不依赖后台文件监听。修改尚未完成或校验失败时不推送；该维护授权也不代替社交平台的发布授权。

## Repository Structure

```text
.
├── README.md
├── AGENTS.md
├── toy-model-info/
├── toy-cover/
├── ego-publish/
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
