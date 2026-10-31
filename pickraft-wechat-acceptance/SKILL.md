---
name: pickraft-wechat-acceptance
description: 验收拾作微信小程序的浏览、生成、积分、邀请、反馈及运营流程，复用仓库测试图片、文案和场景清单，区分开发者工具、模拟与真机证据。
---

# 拾作微信验收

在仓库根目录执行命令。技能及附件随仓库维护，不依赖创建者的绝对路径、登录会话或 .local 历史脚本。

1. 先读 [验收矩阵](references/cases.json) 与 [执行指南](references/execution.md)。按本次改动选择用例，优先 P0；历史证据不是当前版本通过结果。
2. `node .agents/skills/pickraft-wechat-acceptance/scripts/prepare-run.mjs` 生成全部待验收记录和复核素材哈希；默认输出 .local/wechat-acceptance。记录 Git、客户端/API版本、模式、账户别名，不能把 API 测试写成 UI 验收。
3. 安装自动化依赖：`npm ci --prefix tests/wechat --ignore-scripts`。在微信开发者工具开启服务端口并启动项目自动化端口，参考执行指南。`node .agents/skills/pickraft-wechat-acceptance/scripts/smoke.mjs` 执行不提交数据的实际页面冒烟。失败即退出非零；截图保存在忽略目录。
4. 无费用异常回归可运行 `tests/wechat/isolated.mjs`，先按执行指南启动隔离 API 并构建本地目标。并发、跨日、跨账户使用 `tests/wechat/boundaries.mjs`；响应丢失后的实际页面重试使用 `tests/wechat/recovery.mjs`。结果按 scope/checks 记录，部分覆盖不能标整项通过。
5. 用例中每个步骤、预期结果都要核对；执行后将本次 run.json 的 status 改为 passed/failed/blocked，并附 evidence、mode、原因。未执行保留 not-run。付费测试必须记录实际提交次数（失败也计数）、usage和积分前后变化；没有预算则 blocked，不自动重试。
6. `node .agents/skills/pickraft-wechat-acceptance/scripts/summarize.mjs <run.json>` 校验记录并汇总通过、失败和阻塞，引用证据；passed 必须填写实际观察和证据。推送前只提交脱敏摘要，原始截图、个人资料、会话和完整云配置留在 .local。部署、设体验版与 Git 推送按用户当次授权执行。

## 页面返回

列表到详情、填写到确认优先使用独立路由和微信原生左上角返回，不叠加“返回列表／返回上一步”按钮。返回后保留分类、滚动位置和未提交草稿；业务动作（如失败后返回模板、返回编辑创意）单独判断。修改导航时执行 NAV-01，参见执行指南的原生返回回归。

## 边界

- 购买、支付沙盒和个人 API 默认保持线上关闭；技能不授权开启、真实转账、发邮件或对外分享。线上生成累计限制 -1 不等于测试预算无限。
- 生成、照片分析、真实邮件、解锁扣分及后台写操作先确认本轮范围；此前 8 次/¥2 已用完，不复用授权。模拟应在独立本地服务进行，不能给生产故障注入。
- 自动化 smoke 不登录、不读会话、不点生成/解锁/提交。需要写入的场景只用专用测试账户 A/B/管理员，记录基线并清理本次新增数据；不清空用户存储。
- 头像、微信昵称建议、相册权限、分享收件、订阅通知和真实弱网必须按 [真机边界](references/execution.md) 另测。
- 测试素材在 assets；都是程序生成的合成图，不用于证明真实人物相似度或模型美学质量。大文件边界样本按需生成，不提交巨型随机文件。
