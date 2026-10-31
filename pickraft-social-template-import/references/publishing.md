# 拾作发布核对

以下为代码入口，执行前重读实际实现，勿把历史云版本或字段当成永久契约。

## 既有入口

- `apps/api/src/content.ts`：`draft` 校验名称、prompt、说明、分类、风格、size、sourceUrl/sourceType、inputRequirements/outputCount。
- `apps/api/src/template-shape.ts`、`photo-tags.ts`：输入用途、主体标签与生成兼容性；必须查看实际枚举。
- `apps/api/src/catalog.ts`：当前 `system/taxonomy`，只选择启用项。
- `apps/api/src/github-import.ts`：`ImportCandidate`、`normalizeExample`、`importExamples`。
- `apps/api/src/import-routes.ts`：`POST /admin/imports/:id/review`，当前要求 version、approve、reason、rightsConfirmed、compatibilityConfirmed 和 draft；负责公开素材派生、审核、审计、模板发布。
- `apps/api/src/cloudbase.ts`、`storage.ts`：CloudStore/CloudStorage，模板事务会更新目录版本及指纹。
- `apps/api/src/public-images.ts`：公开封面/预览派生，不用第三方临时图链作为成品。
- `apps/api/src/template-submissions.ts`（若名称变化先搜索）：用户链接申请的处理与通知。已有用户申请要复用其实际处理接口，不另造申请或直接改完成状态。

## 最小执行步骤

1. 核对当前线上 API/环境和实际管理员身份。凭据只从现有安全配置读取，不打印、不写进 skill。先查同源 imports/templates，已有记录就验证/续处理。
2. `draft.parse` 校验后，额外确认 `inputRequirements` 至少有一个 `required:true` 的照片输入、实际提示词使用该照片，并核对必填 role 在每组样例中都有图片；通用 schema 接受空输入不代表符合本录入规则。无需照片的来源须先按技能正文完成改造及成对样片验证，无法合理改造则说明原因并停止，不上传候选或发布。存储来源与适配说明，不冒用 Apache 等第三方许可证。用户授权上架不代表原作者授予授权，分别记录；若明确不可复用则保持草稿。
3. 使用当前录入接口；若仍无后台手工创建候选接口，可通过项目已有 CloudStore/CloudStorage **仅暂存 imports 候选**，保留版本和来源；正式发布调用审核 API。不得直接写公开 templates，也不得伪造审核成功。
4. 将新生成的输入/输出上传到不可变路径；记录文件哈希以确认配对和重试复用。源帖图片只用于内部核对，未经确认不复用到公开样片。明确 licenseFile 内的内容是来源与样片说明时，不宣称它证明原作者许可。
   有离散 `options` 的模板，每个 `examples` 分组必须写入 `parameterValues`，完整记录这组图片实际采用的全部选项；审核请求携带与分组顺序一致的 `exampleParameters` 数组。补齐所有选项组合的样片，逐组核对参考图与效果图，不能根据默认值猜测历史样片。输出比例及自由输入内容不参与示例匹配。既有素材只补绑定可用 `POST /admin/templates/:id/example-parameters`，携带当前 `version`、`tagRevision`；新增素材仍走 imports 审核。
5. 发布超时先读 imports 和 templates 确认是否成功；不要自动再创建。校验公开详情的 isPublic、输入必填、标签、输出数及实际 prompt；检查 cover 和 examples 的 HTTP 状态、图片类型、非空内容。
6. 使用 `pickraft-wechat-acceptance` 技能核对开发者工具详情：标题、图片切换、参考照片、上传入口；有选项时确认切换到对应效果图、原图正确配对，切换比例不改示例；不调用模型。保留原会话，截图写 `.local`。工具不可用时区分 API 已通过与 UI 未验证。
7. 若存在用户提交任务，核对处理结果已关联模板，并按当前通知实现完成通知；单独的管理员录入不需要制造用户申请或发无关消息。

## 已验收案例

2026-10-24 教堂广场油画棒案例资料目录：
`.local/douyin-import-7699095136606154826/`。
该目录仅用于当前机器追溯，不是 skill 的运行依赖，也不能复用其中凭据或固定版本。

- 原帖为照片/插画上下对照；改为单张 3:4 插画。
- 一张必填场景照片，可适用人物、动物、车辆、风景与室内。
- 新生成教堂广场参考照片，再用定稿 prompt 生成插画；两者均非原帖照片。
- 分类 `poster`、风格 `illustration` 只是本案例选择，后续按实际内容和启用 taxonomy 判断。
