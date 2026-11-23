---
name: easel-social-publisher
description: 使用已有 Easel 安装准备、适配、制作封面并发布社交媒体内容，支持小红书、抖音、微信公众号、B站、快手、微信视频号和知乎。用户要求多平台发布、一稿多发、制作发布封面或向这些平台投稿时使用。
---

# Easel 社交媒体发布

在用户已有的 Easel 安装上提供 Codex 入口。Easel 负责平台约束、发布脚本和结果核验；本 Skill 补充便携运行时发现、跨平台编排、固定封面阶段与不可跳过的发布确认。

## 前置条件

需要完整 Easel 源码及其发布依赖。本 Skill 不捆绑 Easel、浏览器、平台登录态或 `biliup`。

按顺序确定运行时：

1. 优先使用用户已设置的 `EASEL_ROOT`、`EASEL_PYTHON` 和 `EASEL_BILIUP`。
2. 未设置 `EASEL_ROOT` 时，只在当前目录及父目录查找同时包含 `skills/builtin/`、`skills/shared/` 的 Easel 根目录。
3. 找不到时请用户提供 Easel 根目录；不要猜测本机绝对路径，也不要擅自克隆或运行 Easel/OpenClaw 安装器。
4. Python 优先使用 `EASEL_PYTHON`，其次使用 `$EASEL_ROOT/.venv/bin/python` 或 Windows 对应路径，最后才使用通过依赖检查的 `python3`。

所有 Easel 命令均把工作目录设为 `$EASEL_ROOT`。产物写入本次任务目录或用户指定目录，不写进 Skill 安装目录。

如果用户明确要求使用 Ego 中某个空间，读取已安装的 `ego-browser` Skill，并在该空间检查和操作真实网页。Ego 与 Easel Playwright 登录态彼此独立，不把一方的登录状态当成另一方已登录。

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

## 工作流

1. **盘点**：读取原稿与媒体，确认目标账号、平台、内容形态、原创和素材授权、立即发布或草稿、发布时间及不可修改的文字。
2. **封面**：目标平台需要封面或首图时，读取 [封面工作流](references/cover-workflow.md)。先确认主副标题和素材使用权，再制作各画幅封面并展示预览。已有合格封面时直接复用，不为流程完整而重做。
3. **适配**：运行跨平台 `plan`，按各平台当前内容形态、标题、正文、标签、画幅与分类要求生成独立版本。用户要求原文时只分页和排版，不删改正文。
4. **预检**：逐平台执行 `check` 和 `plan` 或 dry-run，展示账号、标题、正文或摘要、标签、分类、媒体和封面绝对路径。
5. **确认**：列出平台差异、草稿与公开发布范围。只有用户对本次具体内容明确确认后，才能增加 `--exec`、提交草稿或点击最终发布按钮。
6. **执行**：逐平台调用原 publisher Skill。首次真实操作优先有头模式；选择器、页面或必填项与预检不符时停止询问。
7. **核验**：按原 publisher 的读回规则确认结果。逐平台报告成功、草稿、失败或未核实，不把点击完成当成发布成功。

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
- 用户未明确允许改写时，不精简正文、改标题、改事实、补标签或替换素材。
- 发布超时、读回未核实或页面状态不明时不得自动重试，先人工核对，避免重复发布。
- 多平台部分成功时逐平台报告，不自动撤回、删除或补发。
- 不保证归档版本持续适配平台最新页面；首次执行或平台改版后必须目视校验。

## 依赖边界

- 小红书、抖音、快手、视频号和知乎通常依赖 Playwright 浏览器登录态。
- B站视频投稿通常依赖 `biliup` Cookie；B站专栏等未被原 Skill 覆盖的形态需要在用户确认后使用当前可用的安全浏览器工作流。
- 公众号默认只创建草稿，不自动群发；群发需要单独确认。
- 封面生成使用宿主环境已有的图片生成或编辑工具；需要精确中文时使用确定性排版，不让图片模型直接生成正文文字。

Easel 本体及其原始 Skill 使用各自上游许可证，本仓库只发布兼容入口与补充工作流。
