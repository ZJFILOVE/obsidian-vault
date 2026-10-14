# 原文缓存与小节任务包

本文件只管输入的机械准备。主执行者仍负责完整读取本次材料、冻结三映射、确定范围与学生前置、批准材料；脚本不推断教学顺序，也不生成审读 PASS。

## 1. 按当前源 PDF 取得缓存

`<skill>` 表示 problem-driven-courseware 根目录。缓存放在本书 `metadata/extraction-cache/`，不要放进原始 `source/`。text 使用现有 poppler 的 `pdfinfo`/`pdftotext`；figures/clip 使用已装 PyMuPDF 和 Pillow 的 Python 运行，脚本不会联网装依赖。

```bash
python <skill>/scripts/source_cache.py text <原书.pdf> --pages 6-12 --cache-dir <本书>/metadata/extraction-cache
python <skill>/scripts/source_cache.py figures <原书.pdf> --pages 6-12 --contact-sheet --cache-dir <本书>/metadata/extraction-cache
python <skill>/scripts/source_cache.py clip <原书.pdf> --page 8 --rect 80,100,400,350 --dpi 240 --cache-dir <本书>/metadata/extraction-cache
```

页范围均为 **1-based PDF 页序**，不是印刷页码。上面的页码/矩形仅是命令格式示例，必须按本次来源填写。

结果 JSON 的 `status=hit/miss`、`cache_path` 与 `manifest` 指向实际产物：

- text：`source-text.txt`（逐页标记）、`text/page-NNNN.txt`、`text-manifest.json`；空白/扫描页仍保留页记录，未知印刷页码为 null。
- figures：`figures/manifest.json`、原对象图片，可选联系表。仍由 extract-pdf-figures 的原脚本执行，保留 PDF 来源哈希、page、xref 等。
- clip：`clip.png`、`clip-report.json`；使用原裁剪工具，保留文本 span、来源与图像摘要。原工具判为 blocked 的裁剪不会进入已完成缓存。

缓存键绑定源文件完整 SHA256、来源路径、规范化页范围/裁剪参数及相关工具版本/脚本内容；命中还核对全部输出哈希。源、参数或工具变化使用新缓存，缺失/篡改产物重新提取。失败保留诊断，不能当作完成。每次准备任务时重新调用缓存入口取得当前路径，不凭旧会话里的缓存路径推断源文件未变。

图片命中不等于图片审核通过。按 extract-pdf-figures 完成原页与单图实际审读；在工程实际引用的图片上绑定证据，不能因缓存命中自动填 `visual_review` 或继承旧 PASS。

## 2. 由已冻结规划自动配齐任务包

自动组包适用于 `sec1` 及之后的小节；`sec0` 开篇仍按现有专属模板和入口约定派发，避免把普通题链规则套给叙述性开篇。

按 [task-spec.example.json](../templates/task-spec.example.json) 结构写本节 JSON（推荐 `<self>/.pd/task-specs/secN.json`）：

- `sources` 指定原 TeX/TXT 或缓存 `source-text.txt` 的路径与实际行范围，`start/end` 均为 1-based，包含首尾行。使用缓存文本时可设 `metadata_path` 为对应 `text-manifest.json`，将原 PDF 来源与页序记录一并冻结。
- `maps.source/dependency/coverage` 只选本节所需记录；保持全局三张表为权威来源，不用任务 JSON 替代它们。
- 写明 `goal`、`prerequisites`、输入/输出与前后节接口，以及每题的 `qid/action/feedback`；不要让写作者再次研究这些已确定信息。
- `materials.pack` 指向本节 `material-pack-secN.md`，`cards` 明确列出批准卡及关联 qid。无补充材料时提供空包、`cards: []` 与非空 `empty_reason`；有卡片时先由已有 evidence 命令生成当前 `.pd/materials.json`。
- `dialogue.enabled` 与工程配置一致；启用时提供本节蓝图。来源书名、原页、图号等不知道则留空，不从行号猜页码。

```bash
python <skill>/scripts/task_pack.py <self> --spec <self>/.pd/task-specs/secN.json --json
```

输出 `<self>/.pd/task-packs/secN/<摘要>/`，包含本节原文与映射摘录、批准材料、配置、必要写作/TeX规则、`task-prompt.txt` 和逐文件来源/哈希 manifest。重复输入复用同包；输入、范围、配置、材料或相关规则变化生成新包。越界范围、缺文件、未批准材料或已篡改包会明确报错，不能伪装成功。

主执行者确认依赖已满足并按 pdstate 将任务置 ready 后，执行返回的 `start_command`（即同一组包命令加 `--start`）；它在派发时重新核验/组装当前输入，并调用原 `pdstate start` 关联冻结包和实际来源。输出的 `pdstate_command` 只用于查看底层参数，不直接执行历史命令。再把这次 start 返回的 attempt 绝对路径交给对应写作者。写作者的身份与候选输出以该 attempt/task.json 为准，提交仍由 `pdstate submit` 验证；任务包不会启动模型、批准卡片、标 checked 或生成教学 PASS。

提交候选前再次运行同一 task_pack 命令并核对包摘要。若已变化，先失效旧任务、重新准备 attempt，不把旧候选提升到新输入上。只有确认摘要未变才提交。完成后继续既有技术预检与独立验收流程。
