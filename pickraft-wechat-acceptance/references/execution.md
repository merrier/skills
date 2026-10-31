# 执行指南

## 环境与复现

仓库根目录 pnpm install 后运行 pnpm test、pnpm typecheck；这些是后端/类型检查，不代替开发者工具。

自动化依赖锁定于 tests/wechat/package-lock.json。安装 `npm ci --prefix tests/wechat --ignore-scripts`。macOS 示例（其他平台用实际安装路径）：

```sh
/Applications/wechatwebdevtools.app/Contents/MacOS/cli auto --project "$PWD/apps/miniapp" --auto-port 9420
node .agents/skills/pickraft-wechat-acceptance/scripts/prepare-run.mjs
node .agents/skills/pickraft-wechat-acceptance/scripts/smoke.mjs
```

保持当前编译产物与要验收的环境匹配。线上构建必须开发登录关闭、个人 API UI 关闭；不要为了注入测试账户上传本地 mock 包。smoke 连接当前编译项目，报告只记录项目路由和 API_BASE 来源说明，执行者必须补充实际客户端/API版本。

环境变量 WECHAT_AUTOMATOR_WS 默认 ws://127.0.0.1:9420，仅允许回环端点。报告与截图写入 .local/wechat-acceptance 下独立目录。执行 smoke 会把预览导航到发现页，保持会话和存储不变。不自动重建、不触发登录，不应在用户正在操作的开发者工具中并行运行。

## 素材

assets/manifest.json 包含每个文件的用途、尺寸和 SHA-256。assets/copy.json 提供昵称边界、反馈和生成 Prompt。

```sh
node .agents/skills/pickraft-wechat-acceptance/scripts/generate-assets.mjs --boundary
```

生成的 high-resolution.jpg（3200×2400，8–10 MiB）、over-limit.png（>10 MiB）、oriented.jpg（EXIF 6）位于 .local/wechat-acceptance/boundary；普通素材已提交，不依赖用户 resources 文件夹。超限/损坏图只能用于错误提示，不提交真实生成。

人物/脸型/姿态素材为合成示意图，用于输入角色顺序和文件链路；需要真人相似度评估时另经同意使用授权照片且不入库。

## 模拟与实际请求

用例标注 isolated 的场景在本地隔离 API/测试钱包执行，参考 apps/api/test 对应规则。后端单元测试已经存在时优先复用其 fixture 结构，但仍需在开发者工具实际点击并核对 UI；没有可控注入能力时记录 blocked，不伪造生产任务。

选择图片自动化注意：宿主绝对路径不是 wx 可读路径。使用 wx.getFileSystemManager().writeFileSync 将合成图写入 wx.env.USER_DATA_PATH，再 mock chooseImage 返回此路径；结束仅 restore 实际 mock 过的方法。不要 restore 未 mock 的方法，旧版 automator 可能删除原实现。保存原会话时只留内存，finally 恢复，不打印或写入报告。

原生 wx 方法被 mock 的场景必须标 devtools-mock；不冒充权限授权、相册保存或消息送达。不要将返回 Promise 的 wx selector 查询直接用于 automator evaluate；使用 Element.style 等公开 API读取样式。

## 费用与副作用

真实生成需要新批准的调用次数/费用预算。按整个批次统计成功、失败、未知提交；timeout不自动再发，先按同幂等键查原任务。先测无图，再单图、多图、整套；整套按输出条数算调用。免费也计入总提交次数，不把免费视为可无限测试。首张失败就定位原因，预算不能自动追加。

解锁使用专用余额，只检查20分一次性扣费，不重生图。真实反馈会发送邮件，只有当次明确允许发测试邮件才能提交。后台审核/授权/加减积分只能操作专用测试对象，保留审计；不能为测试向普通用户授权。

## 真机边界

iOS、Android分别记录设备/OS/微信版本及体验版号。朋友圈单页1154、长按分享、订阅授权及真实收件、扫码跨账户回流、相册权限、键盘昵称/头像建议、弱网/锁屏不能由 DevTools代替。原型/H5证据不能算开发者工具证据。

本次 run.json 初始全部 not-run。通过需要实际 observed + evidence；blocked 需原因；报告中保留模拟/真实区分、费用估算和账单核销区别。公开摘要不要含任务签名URL、二维码原图、手机号、邮箱、用户ID、token或密钥。

## 免费隔离回归（2026-10-17 新增）

`tests/wechat/fixtures/server.mts` 直接构造内存 Store、合成账户、模拟生成器和模拟邮件出口；不读取 `.env.local`，不连接云数据库，监听 127.0.0.1:3019。每次完整批次重启此服务以清空测试状态。测试账户只存在于本地，不应把此构建上传或设为体验版。

1. 仓库根运行 `apps/api/node_modules/.bin/tsx tests/wechat/fixtures/server.mts`。
2. 生成边界样本：`node .agents/skills/pickraft-wechat-acceptance/scripts/generate-assets.mjs --boundary`。
3. 使用 `PICKRAFT_API_BASE=http://127.0.0.1:3019 PICKRAFT_CLOUDBASE_ENV= PICKRAFT_PERSONAL_API_UI=false PICKRAFT_DEV_LOGIN=false pnpm build:weapp` 构建。仅本地验收临时关闭开发者工具合法域名校验，保存原设置；启动自动化后先确认 `/health` 可访问。
4. 执行 `node tests/wechat/isolated.mjs`。脚本拒绝没有回环地址的构建；会暂存并恢复会话和偏好。选择文件使用原生方法模拟；业务确认弹框由 `tests/wechat/dialog-driver.mjs` 点击真实 Taroify 控件，业务请求到真实本地 API。结果必须标明 `devtools-local-api`，不能称真实模型、微信审核、真实收件或真机结果。`TEST_IDS=AUTH-02,DISC-04` 可选择子场景；部分场景依赖同轮生成或上传的本地数据，应按脚本顺序运行。
5. 每个 result 的 scope 只是本轮实际子步骤，不能自动把同 ID 的整项矩阵标 passed。例如模拟生成通过仍不证明真实供应商链路；三张中失败重试通过不等于所有并发/跨日边界通过。
6. 回归请求序列化：`node --test tests/wechat/request.test.cjs`；此测试编译实际 api.ts，分别核对直连和 cloud.callContainer 的 DELETE 空 JSON 修复。
7. 最后恢复原域名校验设置与线上目标构建（API_BASE、CLOUDBASE_ENV、SERVICE），购买/个人 API 保持关闭，再跑只读 smoke。退出本地服务；不把模拟包上传。

自动化输入后应等待状态更新，弹层打开后等待输入节点出现。失败时先检查截图与实际文案，区分选择器/脚本错误和业务错误。不得将修正断言后的结果覆盖为从未失败；报告保留故障和回归链路。

## 并发、跨日与跨账户补充

在上述隔离服务和本地构建准备好后，运行：

```sh
node tests/wechat/boundaries.mjs
# 重启隔离服务，再运行恢复用例
node tests/wechat/recovery.mjs
```

每个完整批次从新启动的内存服务开始。`TEST_IDS=AUTH-03,GEN-10` 可筛选 boundaries 子流程；不要在同一服务重复运行有余额/配额基线断言的场景。两套脚本不可同时连接同一个开发者工具。恢复脚本使用 acceptance-a/b，自动恢复原会话和生成偏好。

- boundaries 的并发请求和虚拟时间在 `fixtures/boundaries.mts` 本地执行真实业务代码，随后开发者工具以对应合成账户打开结果页。checks 是 API/服务断言，ui/evidence 是真实页面文本和截图，不能将这些 API 断言称为每一步都手工点击。
- 时钟只在单个本地场景中临时修改 Date.now，并用 finally 还原；不改操作系统或云端时间。跨日测试覆盖北京时间零点前后、前日任务成功/退款与当日三次额度。昵称测试独立修改合成账户的时间戳。
- recovery 在 API 已成功提交后用 onSend 返回一次503，实际点击页面重试，检查任务/反馈数和余额不变；另覆盖 CATALOG_CHANGED 重试和正确签名但已过期的会话。所有故障注入端点只随 loopback fixture 启动，不属于生产应用。
- 不依赖原生支付、真实二维码、模型或邮件服务；模拟头像、结果与邮件不能证明真机行为。限流测试保留实际120/分钟及路由10/分钟限制，不通过关闭限流让测试通过。
- 仍按最后的收尾步骤恢复线上目标构建、合法域名校验和用户会话，并停掉隔离服务。

## 模板参数

本地构建与隔离 API 准备完成后，运行 `node tests/wechat/parameters.mjs`。覆盖重复参数合并、空值与长度校验、安全拒绝及详情提交到结果页，使用模拟生成器；后端参数快照、幂等和整套补生成由 `apps/api/test/prompt-parameters.test.ts` 验证。真实模型及微信安全服务须另记证据，不混为本地 UI 通过。

## 分享、半星与官方事件

本地构建和隔离 API 准备后运行 `node tests/wechat/sharing-rating.mjs`，复用已完成合成任务，不调用模型。实际点击半星/整星并读取 API 核对，检查分享弹层的原生按钮属性；reportEvent 被模拟捕获，仅验证调用，不证明微信后台收数。恢复会话和原生方法后重新构建线上包。微信统计上报服务启用、事件定义、真机收到分享卡片和 We分析收数单独记录。

该脚本另覆盖五档相似度、旧反馈原文保留及评分不刷新图片。`node tests/wechat/feedback-layout.mjs` 验证两/三按钮的区别说明、抽屉滚动和「我的」底部安全区；当前 GPT 提示入口始终显示，不能将两/三按钮通过写成单按钮场景已验收。

## GPT 生图

本地构建和隔离 API 启动后运行 `node tests/wechat/gpt-generation.mjs`。检查统一“生成”按钮、自动使用限免、模拟生成与 100 积分扣费，以及长等待提示和套餐文案。测试钱包与模型均为本地模拟，不证明云端 OpenAI 可达性；真实调用需另记预算。收尾恢复线上构建和用户会话。

## 协议与作品 Tab

以 `PICKRAFT_GALLERY_FIXTURE=true` 启动隔离 API，再构建本地目标并运行 `node tests/wechat/legal-gallery.mjs`。合成结果覆盖横图、竖图、整套、失败和待核对任务；不调用模型。测试临时替换会话并在 finally 恢复。覆盖作品展示、详情返回、跨 Tab 的 Feed 内容/滚动保持和未登录协议阅读；完成后恢复线上构建及合法域名校验。

### 每日首张优惠

使用 `PICKRAFT_DAILY_FIRST_FIXTURE=true` 启动隔离 fixture API，构建指向 127.0.0.1:3019 的客户端后运行 `node tests/wechat/daily-first.mjs`。验证 90/100、整套 290、失败恢复及补生成，真实模型调用为 0。旧限免场景只用于历史兼容，不代表当前产品规则。

## 2026-10-28 反馈回归

以 `PICKRAFT_FEEDBACK_20261028=true PICKRAFT_LOGIN_FIXTURE=true` 启动本地 fixture，构建本地目标后运行 `node tests/wechat/feedback-followup-20261028.mjs`。覆盖奖励通知直达投稿、投稿卡片、作品详情无其他效果推荐、无照片公开申请、链接投稿、费用确认前会话过期。测试不提交生成任务、不发真实奖励，结束恢复会话、两份项目域名校验设置和线上目标构建。短链审核去重及危险跳转另由 sharing-campaign API 测试覆盖。


## 原生返回回归（NAV-01）

`WECHAT_AUTOMATOR_WS=ws://127.0.0.1:9431 node tests/wechat/native-navigation.mjs` 在开发者工具中检查套图列表→详情→填写→确认、用户投稿列表→详情和管理员活动审核列表→详情。先构建当前代码并确认自动化连接的是该项目。脚本替换后端与相册响应，不提交生成、上传、扣分或审核；结果及截图默认写入 `.local/native-navigation`。不得将此结果写成生产接口或真机通过。

检查独立路由与页面栈、无重复返回按钮、必填校验不跳页、返回后尺寸/照片/授权/文字保留、重新进入填写页保留草稿，以及列表分类和滚动位置恢复。自动化跳转后必须重新获取 `currentPage()`，不要继续操作上一页。

真机另查左上角按钮和 iOS 侧滑返回、照片预览回来草稿不丢、从通知/分享直接进入详情后的返回路径。保留有明确业务意义的编辑或失败恢复按钮。

## 登录续期回归（AUTH-05）

`node --test tests/wechat/session-restore.test.cjs tests/wechat/login.test.cjs tests/wechat/request.test.cjs` 检查续期、并发、失败和不重放写请求。`node tests/wechat/session-restore.mjs` 使用开发者工具及模拟微信凭证/后端响应检查已过期账号恢复后展示“我的”；不是真实微信登录证明。真机另测关闭数小时后重进、断网恢复和更换微信账号。
