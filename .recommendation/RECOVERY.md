# 发布中断恢复与验收边界

2026-11-04 Journal 补充：现已接入统一冻结包、恢复决策与全局 CI；旧 `journal-frozen-v1` 保留原文及摘要，由严格兼容层验证。新期使用 `schema_version: 1` 的标准包。详见 PUBLISHING.md 的 Journal support。Journal 永久历史也纳入追加保护，当前笔记、索引、DOI/标题/版本去重与 Markdown 标签空格由 `scripts/validate_journal.py` 校验。11 月 2–4 日的排版修正有独立 correction 记录，不改原 PREPARED、曝光历史或用户 Notes。

2026-10-14 补充。不得删除历史、重新选一批内容掩盖失败、覆盖手工 Notes，或把结构通过写成来源已验证。

## 已部署的检查

`python3 scripts/validate_daily_recommendations.py` 检查 Daily、Weekly、TV 来源及历史登记，工作日三件套，音乐逐首章节/元数据/资源顺序。日期门槛读取 policy.strict_from。等价 Markdown 写法可接受，永久资源身份规则不放松。

`python3 scripts/check_daily_integrity.py --base-ref FULL_ANCESTOR_SHA` 对比三份 JSONL 历史原始字节前缀及音乐 state 的全部旧值。还扫描所有现存音乐 Manifest 和笔记，不因 strict_from 跳过旧记录。历史已撤下曲目可以只存在于 state；仍永久禁止复用。旧 YouTube 重复如实报告，不能删除来改善统计。

`.github/workflows/recommendation-health.yml` 是只读 CI：push/PR/手动及每日 UTC 00:47（上海 08:47）。没有发布、部署、自动提交或跨私库凭据。成功只表示列出的本库检查通过。

## 生产者接入协议（不会因这个文件存在而自动接入）

1. 写前读取 policy、全部永久历史、当日文件、已有事务记录及两个仓库的当前提交。同项目同业务日期使用同一个 `operation_id`，格式 `music:2026-10-12` 等。重试沿用已有计划，不能用“现在已经在历史里”把本次已曝光曲目误判为应当替换的新重复。
2. 在展示/写正式内容前，持久化 `.recommendation/transactions/PROJECT/DATE.json` 的不可变计划：业务日期、原始资源集合、目标仓库/路径、写前 blob SHA、预期完整内容 blob SHA、阶段编号。记录原计划 SHA-256；重试从原始 PREPARED 记录读取，而不是重新计算后替换。规划中的资源也应纳入候选阻止集合。计划及曝光记录永久保留。
3. 目标完整内容必须先保留用户 Notes 及 AUTO 标记之外的文字。相同仓库尽量在一个普通 Git commit 中更新相关文件；禁止 force。继续使用串行 Contents API 时，每个 update 带刚刚核对的当前 SHA。
4. 两仓库不是一个原子事务。按阶段写入、回读、比较；结果不明先回读。目标 SHA 已出现就 no-op；仍是写前 SHA 才可重试；任何第三个 SHA 都是并发冲突，停下合并。没有读取结果或权限错误不能当成“文件不存在”。
5. 只有能确认仓库/分支可访问、目标确实不存在，才允许 create。404 的原因未区分、403、429、5xx 或传输错误均保留为未验证；依错误类型处理，不盲目重试。
6. 每个阶段日志记录真实提交与回读摘要，失败只续写缺失步骤。历史只增不减；即使发布失败，已展示/预留的资源也不能在以后重新推荐。
7. `artifacts_match` 只表示文件哈希匹配，不是内容 QA。所有适用的来源、资源身份、数量、语义去重、跨库、历史包含和回读检查通过后，才记录独立成功 QA。旧来源当前失效另列历史维护事项，不靠重选旧日内容修复。

## 可执行的恢复决策工具

`scripts/publication_recovery.py` 是只读决策器，不持有凭据，不替代 GitHub 写入连接器。必须由实际生产者提供真实新回读结果，不能把错误转换为成功观察。

计划包含 `schema_version: 1`、`project`（music / english / news-youtube-reddit）、`date`、`operation_id`、`exposed_resource_ids` 和非空 `targets`。每个目标包含 `repository`、`path`、`base_sha`（确认新建时为 null）、`target_sha` 和整数 `stage`。SHA 是完整 Git blob SHA，不是 commit SHA 或文本 SHA-256。

观察 JSON 按 `仓库:路径` 索引。成功回读为 `{"status":"ok","sha":"完整blob SHA"}`；确认不存在为 `{"status":"missing","confirmed":true}`；失败保留 `{"status":"error","http_status":403}`。省略观察也会阻止写入。

```bash
# 检查准备计划，并输出需要持久保存的原始 plan_sha256。
python3 scripts/publication_recovery.py plan.json
# 每次重试使用原始摘要和新的真实观察；blocked 时非零退出。
python3 scripts/publication_recovery.py plan.json \
  --observations readback.json --expected-digest ORIGINAL_PREPARED_DIGEST
```

输出 next_stage 指出当前最早缺失阶段，decisions 区分 create/update/no_op/conflict/unverified。冲突或未知会阻断全部写动作；回读全匹配仍输出 content_qa=not_evaluated。

## 尚未自动完成的链路

此 CI 无权读取另一个私库，不能宣称跨仓库日检通过。跨库已有检查入口在 music-daily：`python3 scripts/check_consistency.py --vault-root ../obsidian-vault`，需要两个已授权 checkout。计划工具通过单元测试不等于三个 ChatGPT 生产任务已采用协议。恢复任务前应分别验证接入和当日实际内容，不把只读健康 CI 当作开启发布的授权。
