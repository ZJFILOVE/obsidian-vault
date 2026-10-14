# 译稿边界、图片与版面交付

本文件维护翻译/学案分界、图片证据和排版门禁。生成/修复带图学案、修改模板或交付时必读；它不替代 production 的教学验收与证据状态机。

## 忠实翻译先行，学案独立选题

同时要求教材翻译和学案时，先调用同级 `faithful-textbook-translation`，依据原 PDF 完整翻译正文、原书已解例题及其原有解答、全部章末习题和小问。普通习题不自动作答。完整译稿的核验通过后才制作学案；不要把学案的“精选、解析、重组题链”规则用于 `sections/` 译稿。

`self/` 可精选和改编，但 source-map/coverage-map 必须保存原题号、小问、来源页、改编内容与选择理由。教师版可加参考答案；不能回写为原书已有答案。学科证据以原教材为依据，不用夸张叙述补充未经核验的机制或量化结论。

用户明确要求修复现有目录，已构成对必要修复的授权：先保存可恢复快照后就地修复，不因 `self/` 已存在再询问一次。只有无法判断保留哪份相互冲突、不可恢复的内容时才需要澄清。只要求修改 pipeline/skill 时，章节产物只读。

## 图片：调用提取 skill 并核验实际证据

- 必须读取同级 `extract-pdf-figures/SKILL.md`，按其对象提取 → 精确裁剪 → 文本 span 审计 → 原生视觉流程执行。当前 Gemini 必须实际打开原页和最终单图，检查位图内文字、四边及面板完整性，按 `references/visual-review.md` 填写每张图的 `visual_review`；空文本层和旧 PASS 不能替代。
- 原图对象优先；不完整的矢量/混合图用精确裁剪。图题另排中文，图内标签完整保留。只做 trim_white 或在 manifest 声称用了 skill 均不合格。
- 完整翻译的插图已审读也要核对学案的实际使用文件；复制、替换、重裁后重新绑定哈希。在 `.pd/figure-review.json` 中只登记本学案实际使用的图。格式与验证由提取 skill 的 `references/review-contract.md`、`scripts/verify_figure_review.py` 统一维护。
- 不为获得无正文的裁图而裁掉坐标、图例、箭头、基因型或面板。必要时逐面板提取再排版。

## 排版：宽高、可分页与可读性

- `\includegraphics` 同时限制 `width<=\linewidth`、`height<=0.65\textheight`，保留 `keepaspectratio`。当前模板给 Gin 设置该默认值，正文局部显式设置不得覆盖为超页高度。`0.65` 只是单图起始预算，图题、上下文和多图累计高度仍须实测；读不清则拆面板或用整页，不能继续缩小。
- 栏内不能用 `\textwidth` 充当栏宽。三张照片纵排导致超页时，应分面板、缩到可读尺寸、换页或用专页，不能裁掉第三张图。图题不能被挤到另一栏、与图失去关联；短图+短图题可用小型组合并预留空间，整个组合必须小于当前完整栏高。
- `microknowledge/knowledgebox/sectiondialogue/exampledialogue` 使用支持 multicol 的 `tcolorbox` breakable 实现，默认可分页，保持黑白灰和标题，避免依赖本机缺失的 skins 扩展。仅把旧 mdframed 的 nobreak 改为 false 并不足以处理超长双栏框。长说明、长题干、解答和图题禁止整体塞进 `minipage/parbox/resizebox/fbox/lrbox` 或 `nobreak=true`；这些盒子只适用于实测能放下的短元素。multicols 中复杂框即便允许分页也可能需要人工拆成有语义的续框。
- 长表格按列/行合理拆表，长公式用 aligned/split 等断行，长英文/DNA 序列在不改变内容的边界允许换行。不能用极小字号、负间距、增大纸张、抬高日志阈值或删除内容掩盖问题。
- 学生留白可能产生 Underfull，这是稀疏排版诊断；Overfull 表示内容超界，两者不能混淆。纵向 >0.5pt、横向 >2pt、mdframed bad break 阻止交付。细小告警也须视觉确认；不是小于阈值就无需看。

## 构建和视觉验收

1. 运行新版 `build.py`（默认两版各两遍），记录当前日志、输入与 PDF 哈希。脚本现在同时检查 hbox/vbox，报告中必须带当前 `layout_policy`。放宽阈值的构建仅可诊断，`deliver.py --skip-checks` 也不接受它作交付依据。
2. 逐页渲染学生版与教师版；联系表用于导航，含图、长表/框/公式、跨页题和日志告警页面必须原尺寸细看。所有页检查页边界、栏边界、页眉页脚、阅读顺序、图题关系、面板/标记完整性、留白与字号。PDF 能打开、文本可抽取或日志通过都不等于版面通过。
3. 实际完成后填写 `.pd/layout-review.json`。不能从页数自动生成 PASS，也不能伪称用户已 review。此记录只表明具名执行者的检查；无审读记录保持待验收。
4. 再做教学验收和 `deliver.py`。构建、排版、图片和教学验收分别成立；任何一项缺失则保留草稿，旧 release 不会被替换。禁止运行自动写满 PASS 或循环把所有 compare 疑似项都标成 false_positive 的“封版脚本”。问题须逐项用真实证据判定。

```json
{
  "schema_version": 1,
  "status": "pass",
  "reviewer": "实际审读者",
  "input_digest": "当前 build.json input_digest",
  "pdf_sha256": {"student":"当前 SHA256", "teacher":"当前 SHA256"},
  "pages": {
    "student": [{"page":1, "notes":"记录本页边界、双栏、图题及可读性的具体观察"}],
    "teacher": [{"page":1, "notes":"记录本页单栏、解答长框及图题的具体观察"}]
  },
  "issues": []
}
```

实际记录必须覆盖两版所有页，不只是示例第 1 页。任何输入、图片、配置、宏或 PDF 变化都使旧审读失效；重新构建并复核，不能只改 JSON 摘要。图片/版面记录的哈希会进入 release manifest。

## 验证 skill 改动

```bash
python scripts/test_templates.py
python scripts/test_runtime.py
python scripts/test_quality_gates.py
```

使用临时合成工程，不修改已有章节。模板测试是真实 XeLaTeX 编译；新门禁测试要包含长图/长知识框分页、纵向溢出、旧构建证据和漏页审读的失败样本。
