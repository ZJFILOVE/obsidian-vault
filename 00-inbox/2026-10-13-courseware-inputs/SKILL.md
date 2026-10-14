---
name: problem-driven-courseware
description: 将教材、论文、讲义改造成问题驱动的研学案或自学稿，单源生成学生版与教师版。用于问题链、8K 作业纸、教材问题化改造、课堂对话式引例，以及已有学案的续做和修复。
---

# 问题驱动学案

问题产生认知需要，必要解释保持动机与精度，完整论证建立可迁移的方法。学生版隐藏解答并留白，教师版呈现解答与教学批注；两版来自同一套 TeX。

## 默认入口：按状态继续

适用于 Antigravity 对话框直接启动，无需先经 GPT 规划或启动外层常驻进程。复用用户已给的书目、范围、模型、标题与对话开关；不硬编码模型或旧会话 ID。

1. 确定本次章节的 `self/`。已有工程先运行 `python <skill>/scripts/pipeline_status.py <self>`，读取当前状态与下一步提示；新材料进入规划。状态输出只导航，不替代验收。只改 skill/pipeline 时不重跑课件。
2. 只读下表中**当前角色、当前阶段**需要的文件。已读规则在本会话不变时不再加载；子 Agent 只收对应原文片段、材料包与接口，不复制整个 skill 或历史日志。
3. 按 [production.md §零](references/production.md#零运行效率与恢复) 从缺失或失效步骤继续，完成用户授权范围。阶段结束保存磁盘断点；有下一步且可继续时直接推进，不逐阶段停下来等确认。

用户可以直接说：“使用 problem-driven-courseware，处理这个目录的第 N 章；已有内容从断点继续，按默认增量流程执行。”

## 按角色加载

| 当前工作 | 读取范围 |
|---|---|
| 主执行者首次规划 | [production.md](references/production.md) §零至四；原文按章完整读取并建立三张映射表。对话层仅启用时读 §五 |
| 主执行者续做、返修 | production §零及当前步骤；已有映射、材料包、断点与所需原文，不重读整书或重新规划已有效章节 |
| 研究核验 | [research_prompt.md](prompts/research_prompt.md)、需求与对应原文；仅缺外部事实时检索 |
| 小节写作者 | [subagent_prompt.md](prompts/subagent_prompt.md)、[tex-interface.md](references/tex-interface.md)、对应冻结任务包；无需 production 全文、验收提示或其它小节全文 |
| 独立验收 | [acceptance_prompt.md](prompts/acceptance_prompt.md)，先仅学生输入，阶段一落盘后再接收阶段二材料 |
| 插图、布局、交付 | [source-and-layout.md](references/source-and-layout.md)；需要提图时加载 extract-pdf-figures；写 TeX 时读 tex-interface |
| 课堂实施 | 仅此时读 [flow.md](flow.md)、[teacher-guide.md](teacher-guide.md) 与课堂模板 |

## 必须保留的约束

- 先完整读取本次源材料，建立 `source-map`、`dependency-map`、`coverage-map`，再按依赖组织题链；来源页、题号、图号不可编造。翻译与学案分界见 source-and-layout。
- 所需前置必须对学生可见；每小问仍有待完成的认知动作。保留核心论证，例子/反例由主执行者独立核验。材料须有批准与回溯链。
- 一节一独立写作者，冻结接口后按依赖并行；主执行者单写全局台账与装配。沿用 `pdstate` 的 start/submit/checked 与 attempt 校验，不伪造提交。
- 单源双输出；qid 全章唯一，引用用 label/ref。宏与配置规则仅在 tex-interface 维护。
- 真实逐图及双版逐页视觉审读、独立教学验收、当前摘要绑定和原子发布均保留。输入变化使旧 PASS 失效，缓存不生成或修改 PASS。
- 遵守工作区写入规则；要求 Markdown 先入 inbox 时，在 inbox 写原件，再于工程使用可追溯链接。

## 输入准备加速

需要从 PDF 取原文或图片时，先用 `scripts/source_cache.py` 核对并复用机械提取结果；派发写作者前用 `scripts/task_pack.py` 将已确定的原文范围、三映射摘录、批准材料和前置接口组装成冻结包。具体命令和任务配置见 [input-preparation.md](references/input-preparation.md)，只在准备输入时读取。缓存不批准材料，不替代读原文、图片审读或教学验收。

## 默认技术入口

以下 `<skill>` 为本 skill 所在目录；使用已可用的 Python 3.10+，无需为每阶段新建环境。

```bash
# 只读状态；优先执行一次，避免靠旧会话摘要猜进度
python <skill>/scripts/pipeline_status.py <self>
# 写作/修复完成后：只运行缺失、失效的技术步骤；内容和证据不变则复用
python <skill>/scripts/technical.py <self>
# 实际完成图件/逐页视觉审读、疑似项处置后，先检查全部非教学门禁
python <skill>/scripts/deliver.py <self> --preflight
# 独立两阶段教学验收完成后，核验当前全部证据并原子发布
python <skill>/scripts/deliver.py <self> --skip-checks
```

`technical.py` 完成不表示可交付；`--preflight` 只读、不发布，允许教学验收尚未完成。`deliver.py --check-only` 只读核验包括教学验收在内的全部门禁。不要在验收后无条件重建 PDF，让刚完成的证据失效。详细状态机、失效与恢复只在 production 维护。

修改模板/脚本后运行 `test_templates.py`、`test_runtime.py`、`test_quality_gates.py` 及对应新增脚本测试，使用临时工程，不触碰真实章节。
