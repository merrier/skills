---
name: easel-social-publisher
description: 使用已有 Easel 安装准备、适配、制作封面并发布社交媒体内容，支持小红书、抖音、微信公众号、B站、快手、微信视频号和知乎。用户要求多平台发布、一稿多发、制作发布封面或向这些平台投稿时使用。
---

# Easel 社交媒体发布

在用户已有的 Easel 安装上提供 Codex 入口。Easel 负责平台约束、发布脚本和结果核验；本 Skill 补充便携运行时发现、跨平台编排、固定封面阶段与不可跳过的发布确认。

## 个人配置

公开 Skill 不保存账号、浏览器空间、登录态或本机路径。每次任务开始时按以下顺序读取可选的个人配置：

1. `EASEL_SOCIAL_PREFS` 指向的 Markdown 文件。
2. `~/.config/easel-social-publisher/preferences.md`。

配置可以记录 Easel 运行路径、默认 Ego 空间、常用账号显示名、主题目录和用户长期确认过的内容适配偏好。当前请求始终优先于配置；配置缺失或字段未写时不猜测。不得在回复、日志或公开仓库中输出其中的凭据或浏览器存储。

## 前置条件

需要完整 Easel 源码及其发布依赖。本 Skill 不捆绑 Easel、浏览器、平台登录态或 `biliup`。

按顺序确定运行时：

1. 优先使用用户已设置的 `EASEL_ROOT`、`EASEL_PYTHON` 和 `EASEL_BILIUP`，其次使用个人配置中的对应路径。
2. 仍未确定 `EASEL_ROOT` 时，只在当前目录及父目录查找同时包含 `skills/builtin/`、`skills/shared/` 的 Easel 根目录。
3. 找不到时请用户提供 Easel 根目录；不要猜测本机绝对路径，也不要擅自克隆或运行 Easel/OpenClaw 安装器。
4. Python 优先使用 `EASEL_PYTHON`，其次使用 `$EASEL_ROOT/.venv/bin/python` 或 Windows 对应路径，最后才使用通过依赖检查的 `python3`。

所有 Easel 命令均把工作目录设为 `$EASEL_ROOT`。产物写入本次任务目录或用户指定目录，不写进 Skill 安装目录。

如果用户明确要求使用 Ego 中某个空间，或个人配置指定默认 Ego 空间，读取已安装的 `ego-browser` Skill，并在该空间检查和操作真实网页。当前请求指定的空间优先。Ego 与 Easel Playwright 登录态彼此独立，不把一方的登录状态当成另一方已登录。

## 路由

执行前完整读取当前任务对应的 Easel 原始 Skill：

- 多平台：`$EASEL_ROOT/skills/builtin/skill-cross-platform-publish/SKILL.md`
- 小红书：`$EASEL_ROOT/skills/builtin/skill-xhs-publisher/SKILL.md`
- 抖音：`$EASEL_ROOT/skills/builtin/skill-douyin-upload/SKILL.md`
- 微信公众号：`$EASEL_ROOT/skills/builtin/skill-wechat-publisher/SKILL.md`
- B站：`$EASEL_ROOT/skills/builtin/skill-bilibili-upload/SKILL.md`
- 快手：`$EASEL_ROOT/skills/builtin/skill-kuaishou-upload/SKILL.md`
- 微信视频号：`$EASEL_ROOT/skills/builtin/skill-channels-upload/SKILL.md`
- 知乎：`$EASEL_ROOT/skills/builtin/skill-zhihu-publisher/SKILL.md`

原 Skill 不支持用户选择的内容形态时先说明缺口。例如只有文章却要求视频投稿，需要先确认是否制作视频或跳过该平台；不要静默改成另一种内容。

## 内容适配

发布文章、长文、图文卡或需要事实修正时，读取 [内容适配与确认规则](references/content-adaptation.md)。核心原则是优先平台原生内容形态、保护原文、集中确认且不猜测。

使用 Ego 发布公众号文章、B站专栏、小红书图文或抖音文章时，另读 [Ego 平台实操与回读规则](references/ego-platform-workflows.md)。它记录真实页面已经验证过的草稿、封面、声明、验证码和结果回读路径；平台页面变化时以当前页面为准。

制作微信公众号正文时读取 [公众号留白禅意排版规则](references/wechat-layout.md)。默认使用 Easel `gzh-design` 的「留白禅意风」组件库及本 Skill 确认的克制变体；用户当次指定其他主题时以当次要求为准。

个人配置指定文章池时，发布选题前读取 [按时间选择待发布文章](references/article-source-queue.md)。先刷新远端目录，按配置方向选择下一篇未发布内容并推荐给用户；选题确认不等于发布授权。

每次发布前必须读取 [合集规划与加入规则](references/collection-workflow.md)，向用户确认本次是不使用合集、加入已有合集还是创建新合集。用户没有指定时，可以根据内容主题和当前合集列表推荐，但不能替用户创建或加入。

源内容来自 notes 或其他 Markdown 知识库时，发布完成后读取 [Notes 元数据回写规则](references/notes-metadata.md)，把最终确认的合集写入 `category`，把最终话题写入 `tags`，并维护首次公开日期 `published_at`、简短英文路径 `urlname` 与实际公开平台 `platforms`。不得覆盖原有无关属性或把未执行的发布计划写成已完成。

## 工作流

1. **盘点**：读取个人配置、原稿与媒体，确认目标账号、平台、内容形态、原创和素材授权、立即发布或草稿、发布时间、不可修改的文字，以及各平台合集方案。能从当前请求或已确认配置得到的信息不重复询问。
2. **合集**：检查当前平台是否支持本次内容形态，列出现有合集并给出推荐；按用户确认选择不使用、加入已有或创建新合集。不存在精确同名合集时才创建，不能创建空合集代替不兼容的内容形态。
3. **封面**：目标平台需要封面或首图时，读取 [封面工作流](references/cover-workflow.md)。先确认主副标题和素材使用权，再制作各画幅封面并展示预览。已有合格封面时直接复用，不为流程完整而重做。
4. **适配**：运行跨平台 `plan`，按各平台当前内容形态、标题、正文、标签、画幅与分类要求生成独立版本。用户要求原文时只分页和排版，不删改正文。
5. **预检**：逐平台执行 `check` 和 `plan` 或 dry-run，展示账号、标题、正文或摘要、标签、分类、媒体、封面和合集方案。
6. **确认**：列出平台差异、合集、草稿与公开发布范围。只有用户对本次具体内容明确确认后，才能增加 `--exec`、提交草稿或点击最终发布按钮。
7. **执行**：逐平台调用原 publisher Skill，或按已确认的 Ego 工作流操作。每个平台使用独立标签页，首次真实操作优先有头模式；选择器、页面或必填项与预检不符时停止询问。
8. **核验**：按原 publisher 的读回规则确认结果。逐平台报告成功、草稿、合集归属、失败或未核实，不把点击完成当成发布成功。
9. **回写**：目标平台达到用户要求的终态后，更新源 notes 文章的 `category`、`tags`、`published_at`、`urlname` 和 `platforms`，同步用户已经确认的事实修正，并按源仓库要求验证索引、Markdown 和隐私边界。

跨平台规划示例：

```bash
"$EASEL_PYTHON" "$EASEL_ROOT/skills/builtin/skill-cross-platform-publish/scripts/publish_dispatch.py" \
  plan --manifest /absolute/path/content.json
```

未设置 `EASEL_PYTHON` 时，用前置条件中已经解析并验证的 Python 绝对路径替换。

## 发布边界

- 检查登录状态不等于授权发布；制作封面、上传素材或保存草稿也不等于授权公开发布。
- 不读取、输出或提交 Cookie、Token、验证码载荷、二维码载荷、平台凭据和浏览器存储。
- 发布前必须展示最终账号、平台、内容、媒体和封面。用户只确认部分平台时只执行已确认部分。
- 创建合集、修改合集或把内容加入合集都需要本次确认；它们不由发布授权自动包含。
- 用户未明确允许改写时，不精简正文、改标题、改事实、补标签或替换素材。长文转卡片默认只分页和排版，正文逐字保留。
- 发布超时、读回未核实或页面状态不明时不得自动重试，先人工核对，避免重复发布。
- 多平台部分成功时逐平台报告，不自动撤回、删除或补发。
- 不保证归档版本持续适配平台最新页面；首次执行或平台改版后必须目视校验。

## 依赖边界

- 小红书、抖音、快手、视频号和知乎通常依赖 Playwright 浏览器登录态。
- B站视频投稿通常依赖 `biliup` Cookie；B站专栏等未被原 Skill 覆盖的形态需要在用户确认后使用当前可用的安全浏览器工作流。
- 公众号默认只创建草稿，不自动群发；群发需要单独确认。
- 封面生成使用宿主环境已有的图片生成或编辑工具；需要精确中文时使用确定性排版，不让图片模型直接生成正文文字。

Easel 本体及其原始 Skill 使用各自上游许可证，本仓库只发布兼容入口与补充工作流。
