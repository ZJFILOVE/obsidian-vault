# 第一章第 III 节切片制作详细任务书 (prompt-sec3)

## 1. 任务身份
- run_id: `20261004-003032-30c4`
- task_id: `sec3`
- attempt_id: `1`
- input_digest: `2ba81110ace32fed84e2a15c712fd1f4d2bb2d6739a1de2902b4abdbb46e3d76`
- 候选目录: `微观化学反应_第一章/self/.pd/candidates/sec3/attempt-0001/`
- 输出文件: `sec3.tex` 与 `result.json`

## 2. 编写规范
1. **标题与小节编号**:
   - `\section*{III 反应截面的热平均与化学反应速率}`
   - 严禁包含 `\documentclass`、导言区或 `\begin{document}`。
2. **对话层规范（黑白印刷，零剧透，悬置收尾）**:
   - `sectiondialogue`: 4-6 句，角色 $\Psi,\alpha,\gamma,\beta$，含 2-4 处认知冲突词（“难道”、“不对”、“凭什么”），末句含悬置指示词以设问（“？”）收尾，暴露“微观单分子碰撞截面如何跨越尺度转化为宏观温度相关的阿伦尼乌斯速率常数”。
   - `exampledialogue`: 3-4 句，绑定 `% dialogue: qid=sec3-q1`，置于 `\begin{probchain}` 之前，含 1-2 处认知冲突词，末句以感叹号（“！”）悬置收尾，严禁泄露麦克斯韦-玻尔兹曼能量积分形式。
3. **题目规划（严格对应 coverage-map.md）**:
   - `sec3-q1` (进入题，guided，配卡片 `CARD-07`)：单能速率常数 $k(v) = v\sigma_r(v)$；以麦克斯韦相对速度分布 $f(v)\dd v$ 加权，利用变量代换 $\Etr = \frac12\mu v^2$ 推导平动能形式的宏观反应速率常数积分：
     $$K(T) = \left(\frac{1}{\pi\mu}\right)^{1/2}\left(\frac{2}{k_B T}\right)^{3/2}\int_0^\infty \Etr\exp\left(-\frac{\Etr}{k_B T}\right)\sigma_r(\Etr)\dd \Etr$$
   - `sec3-q2` (形式化计算与证明题，guided，配卡片 `CARD-07`)：配备 `\textbf{证明策略：}`；两大经典模型的闭式积分推导：
     1. 将 SCT 激发函数 $\sigma_r(\Etr) = \pi d^2(1 - E_0/\Etr)$（$\Etr \ge E_0$）代入速率常数积分，运用分部积分法严格证明 $K_{\mathrm{SCT}}(T) = \langle v\rangle \pi d^2 \exp(-E_0/k_B T)$；
     2. 将 Langevin 离子-分子激发函数 $\sigma_r(\Etr) = \pi(2\alpha e^2/\Etr)^{1/2}$ 代入积分，证明速率常数 $K(T) = 2\pi e(\alpha/\mu)^{1/2}$，理论上与反应温度严格无关。
   - `sec3-q3` (辨认与解释题，unprompted，依赖 sec3-q1, sec3-q2)：标 `\practicemode{unprompted}`，题内无提示；结合热平衡玻尔兹曼因子 $\Etr\exp(-\Etr/k_BT)$ 与微观激发函数 $\sigma_r(\Etr)$，深入剖析两曲线乘积形成的“反应窗口”：分析为什么反应速率不是由最高能分子单独决定，解释温度升高如何促使窗口向高能方向移动并展宽。
   - `sec3-q4` (证明题，guided，配卡片 `CARD-08`)：配备 `\textbf{证明策略：}`；Arrhenius 活化能与 Tolman 统计诠释推导：
     1. 根据 $E_a = RT^2\frac{\dd\ln K}{\dd T}$，对 SCT 速率常数求对数导数，证明 $E_a = N_A E_0 + \frac12 RT$ 与指前因子 $A = \langle v\rangle \pi d^2 e^{1/2}$；
     2. 对一般能量积分式进行对数微分商求导，严格证明 Tolman 关系式：
        $$E_a = N_A\frac{\int_0^\infty \sigma_r(\Etr)\Etr^2\exp(-\Etr/k_B T)\dd\Etr}{\int_0^\infty \sigma_r(\Etr)\Etr\exp(-\Etr/k_B T)\dd\Etr} - \frac32 RT = \bar E_r - \bar E_T$$
        揭示活化能微观本质是反应分子平均能量与体系热平衡分子平均平动能之差。
   - `sec3-q5` (综合辨认题，guided，配卡片 `CARD-08`)：剖析活化能的温度依赖性与微观反应阈能本质：对比不同激发函数曲线下活化能随温度的变化（图1-20），深入辨析宏观阿伦尼乌斯活化能（系综统计量）与微观反应阈能（单对力学量）的本质异同，阐明低温极限下 $E_a\to N_A E_0$ 的物理根源。
4. **节末结论框**:
   - `\begin{knowledgebox}[本章核心总结与下一章接口]`，系统总结第一章三大板块（微观碰撞截面、偏转角与轨线、热平均与活化能本质），明确引出第二章核心课题：三体反应势能面与经典 Hamilton 轨线计算。

## 3. 单源双输出与宏约束
- 题干使用 `\item[Q\arabic{probcount}]`，提示使用 `\hint{...}`，解析使用 `\solution{...}`。
- 公式必须严谨，使用 `\Etr`, `\dd`, `\Ueff`, `\kB`, `\bm` 等定义宏。
- 输出 `sec3.tex` 后计算 SHA256 并生成合规 `result.json`。
