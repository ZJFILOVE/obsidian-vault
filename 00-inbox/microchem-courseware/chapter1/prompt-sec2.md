# 第一章第 II 节切片制作详细任务书 (prompt-sec2)

## 1. 任务身份
- run_id: `20261004-003032-30c4`
- task_id: `sec2`
- attempt_id: `1`
- input_digest: `0877929fb309819309bd9316bb0995dc47810c2716edb57a25cdadcb520b4038`
- 候选目录: `微观化学反应_第一章/self/.pd/candidates/sec2/attempt-0001/`
- 输出文件: `sec2.tex` 与 `result.json`

## 2. 编写规范
1. **标题与小节编号**:
   - `\section*{II 经典碰撞散射与反应微观截面}`
   - 严禁包含 `\documentclass`、导言区或 `\begin{document}`。
2. **对话层规范（黑白印刷，零剧透，悬置收尾）**:
   - `sectiondialogue`: 4-6 句，角色 $\Psi,\alpha,\gamma,\beta$，含 2-4 处认知冲突词（“难道”、“不对”、“凭什么”），末句含悬置指示词以设问（“？”）收尾，暴露“为什么相同的碰撞能量会有截然不同的散射角”。
   - `exampledialogue`: 3-4 句，绑定 `% dialogue: qid=sec2-q1`，置于 `\begin{probchain}` 之前，含 1-2 处认知冲突词，末句以感叹号（“！”）悬置收尾，严禁剧透偏转积分公式。
3. **题目链规划（严格对应 coverage-map.md）**:
   - `sec2-q1` (进入题，guided，配卡片 `CARD-03`)：利用角动量守恒与能量守恒消去时间参量，推导偏转角积分 $\chi(\Etr,b) = \pi - 2b\int_{r_{\min}}^\infty \frac{1}{r^2}[1 - U(r)/\Etr - b^2/r^2]^{-1/2}\dd r$；区分推斥、吸引与环行（$\chi\to-\infty$）；定义虹角 $\chi_r$ 与荣角 $\chi_g$。
   - `sec2-q2` (形式化证明题，guided，配卡片 `CARD-04`)：柱对称散射立体角元 $\dd\omega = 2\pi\sin\theta\dd\theta$；从微元通量平衡推导微分截面定义 $I(\theta,\Etr) = \frac{b}{\sin\theta}|\frac{\dd b}{\dd\theta}|$；代入刚球偏转角 $\chi = \pi - 2\arcsin(b/d)$ 严格证明刚球微分截面 $I = \frac14 d^2$（各向同性），并积分证明总截面为 $\pi d^2$。
   - `sec2-q3` (辨认题，unprompted，依赖 sec2-q2)：标 `\practicemode{unprompted}`，分析弹性散射中经典发散奇点的量子修正：德布罗意物质波波长、前向荣角小角衍射消除经典截面发散、虹角处不同碰撞参数散射轨线的量子干涉振荡、离心势垒穿隧。
   - `sec2-q4` (构造题，guided)：定义反应几率（不透明函数 $P(b)$）与反应截面积分 $\sigma_r = 2\pi\int_0^{b_{\max}} b P(b)\dd b$；分析刚球阶跃模型与空间取向因子 $p$；根据非反应弹性散射角分布减弱反推微观反应几率曲线。
   - 插入实线知识卡片 `\begin{microknowledge}[反应阈能与化学激发函数]`，界定活化阈能 $E_0$ 与激发函数 $\sigma_r(\Etr)$ 的核心定义。
   - `sec2-q5` (综合证明题，guided，配卡片 `CARD-05`)：三大化学激发函数模型对比与严格推导：
     1. SCT 模型：中心连线平动能 $E_{1C} = \Etr(1-b^2/d^2) \ge E_0$，证明激发函数 $\sigma_r(\Etr) = \pi d^2(1 - E_0/\Etr)$；
     2. MSCT 模型：引入空间取向势能 $U(D) = E_0 + 2E'(1-\cos\phi)$，推导激发函数 $\sigma_r(\Etr) = \frac{\pi D^2(\Etr - E_0)^2}{4\Etr E'}$，对比平缓上升特征；
     3. Langevin 模型：极化吸引势 $U(r) = -\frac{\alpha e^2}{2r^4}$，离心势垒极值导出最大碰撞参数 $b_{\max} = (2\alpha e^2/\Etr)^{1/4}$，证明离子-分子反应激发函数 $\sigma_r(\Etr) = \pi(2\alpha e^2/\Etr)^{1/2}$（随碰撞能量升高反而单调下降）。
   - `sec2-q6` (迁移应用题，guided，配卡片 `CARD-06`)：微观反应机理与动力学行为诊断：
     1. 剥夺型（前向散射、大 $b$、大截面，如 $\mathrm{K+I_2}$）vs 回弹型（后向散射、小 $b$、小截面，如 $\mathrm{K+CH_3I}$）；
     2. 鱼叉机理：库仑长程引力势能与中性共价能级交叉点 $r_c = \frac{e^2}{I(M) - E(X_2)}$ 估算反应截面；
     3. 旁观者模型：转移轻原子时重原子速度近似不变，三体动量守恒证明产物平动能比值 $\Etr'/\Etr = \cos^2\beta = \frac{m_Am_C}{m_{AB}m_{BC}}$，定量分析剩余反应放能向产物内部振转激发能的转化。
4. **节末结论框**:
   - `\begin{knowledgebox}[本节核心结论与下节接口]`，总结偏转角、微分截面、三大激发函数与反应机理，并明确引出下一节：如何对单能微观截面进行 Maxwell-Boltzmann 统计热平均，导出宏观反应速率常数 $K(T)$ 与 Tolman 活化能诠释。

## 3. 单源双输出与宏约束
- 题干使用 `\item[Q\arabic{probcount}]`，提示使用 `\hint{...}`，解析使用 `\solution{...}`。
- 公式必须严谨，使用 `\Etr`, `\dd`, `\Ueff`, `\bm` 等定义宏。
- 输出 `sec2.tex` 后计算 SHA256 并生成合规 `result.json`。
