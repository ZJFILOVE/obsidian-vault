# 研究需求与材料核验清单 (research-brief)

本章教材《分子碰撞与微观化学反应》（`chapter1.tex`）本身具有高度完整、自洽的物理模型推导、数学证明与实验引例数据（图1-1至图1-20，表1-1）。根据 `references/production.md` 步骤 2 的跳过检索条件：**原材料中已完整包含所有教学所需的引例、反例与推导模型，无需从外部文献补充未经授权的材料。全部正文材料均来自原材料本身（来源类型：REUSE-ORIGINAL），由主 Agent 进行数学重算与两道闸门核验。**

## 一、 材料需求与核验清单

| 需求ID | 知识点/原文节点 | 材料类型 | 要改变的判断或暴露的边界 | 学生已知前置 | 允许的新对象/记号 | 计划落点 | 必须避免的误解 | 材料来源类型 | 核验状态 |
|---|---|---|---|---|---|---|---|---|---|
| REQ-01 | S1-03 交叉分子束强度衰减 | entry | 暴露宏观热平衡平均的局限，建立单次微观碰撞几率度量 | 粒子流数密度 $n_A$、相对速度 $v$ | 碰撞截面 $\sigma(v)$ | sec1-q1 | 误将散射强度减弱当成光学介质吸收 | REUSE-ORIGINAL (`chapter1.tex` L59-76, 图1-1) | approved |
| REQ-02 | S1-06~08 L-J有效势与离心垒 | counterexample/boundary | 改变“只要动能足够大两粒子就一定能无限接近”的简单直觉，揭示离心推斥阻碍作用与临界参数 | 质心系相对运动方程、守恒动能 | 离心势、有效势 $U_{\mathrm{eff}}(r)$、转向点 $r_{\min}$ | sec1-q4, sec1-q5 | 误认为转向点动能全为零（实为径向速度为零） | REUSE-ORIGINAL (`chapter1.tex` L138-209, 图1-4, 图1-5) | approved |
| REQ-03 | S1-09~10 L-J偏转函数与虹角荣角 | entry/counterexample | 破坏“碰撞偏转角只能是像刚球一样的正角”经验直觉，展现长程吸引导致的负偏转与环行奇点 | 极角微分方程、转向点 $r_{\min}$ | 偏转角 $\chi$、虹角 $\chi_r$、荣角 $\chi_g$ | sec2-q1 | 误认为偏转角发散代表真实物理粒子速度无穷大 | REUSE-ORIGINAL (`chapter1.tex` L210-241, 图1-6, 图1-7) | approved |
| REQ-04 | S1-11~12 刚球微分截面解析证明 | entry | 从圆柱对称立体角微元通量守恒严格证明各向同性散射 $I(\theta)=\frac14d^2$ | 立体角微元 $\dd\omega$、通量守恒 | 微分截面 $I(\theta,E_T)$ | sec2-q2 | 混淆微分截面与总截面物理量纲 | REUSE-ORIGINAL (`chapter1.tex` L242-324, 图1-8) | approved |
| REQ-05 | S1-17~19 SCT/MSCT/Langevin三大模型 | entry/transfer | 对比有能垒反应（SCT/MSCT截面随动能增加）与无能垒放能反应（Langevin截面随动能下降）动力学差异 | 动能几何投影、极化势 | 中心连线动能 $E_{1C}$、极化率 $\alpha$、激发函数 $\sigma_r(E_T)$ | sec2-q5 | 误将所有化学反应都假设具有活化能垒 | REUSE-ORIGINAL (`chapter1.tex` L409-526, 图1-11~1-14) | approved |
| REQ-06 | S1-21~22 鱼叉机理与旁观者模型 | transfer/synthesis | 揭示电子转移超大截面形成机制及轻原子转移下产物内部能态分配 | 库仑引力势、两体/三体动量守恒 | 交叉距离 $r_c$、质量因子 $\cos^2\beta$ | sec2-q6 | 误认为超大截面违背了分子物理尺寸限制 | REUSE-ORIGINAL (`chapter1.tex` L541-596, 图1-16, 表1-1) | approved |
| REQ-07 | S1-24~25 Maxwell-Boltzmann统计加权 | entry/synthesis | 解决微观单碰撞态-态截面与宏观大量热平衡分子速率常数之间的跨尺度桥梁 | 麦克斯韦速度分布、分部积分 | 单能速率常数 $k(v)$、宏观速率 $K(T)$ | sec3-q1, sec3-q2 | 误认为宏观速率等于微观截面乘以简单平均速度 | REUSE-ORIGINAL (`chapter1.tex` L638-703, 图1-19) | approved |
| REQ-08 | S1-26~27 Tolman统计诠释严格证明 | synthesis/review | 阐明活化能 $E_a$ 的微观本质并非恒定常数，而是反应物平均能量与平均热能之差 | Arrhenius 活化能微分定义、商求导 | 活化能 Tolman 解释 $E_a=\bar E_r-\bar E_T$ | sec3-q4, sec3-q5 | 误以为宏观活化能与微观反应阈能数值与概念等同 | REUSE-ORIGINAL (`chapter1.tex` L708-754, 图1-20) | approved |

## 二、 批准卡片清单 (Approved Cards)

| 卡片ID | 对应需求 | 核心结论与数学事实 | 核验闸门 | 状态 | 落点 |
|---|---|---|---|---|---|
| CARD-01 | REQ-01 | 交叉分子束衰减方程 $-\dd I_A = \sigma(v)I_An_B\dd x$ 积分得 $I_A(x)=I_A(0)\exp(-\sigma(v)n_Bx)$；刚球截面 $\pi d^2$ | 两道闸门通过（独立微元积分复核） | approved | sec1-q1 |
| CARD-02 | REQ-02 | 有效势 $U_{\mathrm{eff}}(r)=U(r)+E_Tb^2/r^2$；转向点方程 $r_{\min}=b[1-U(r_{\min})/E_T]^{-1/2}$；L-J势临界参数 $E_T^*b^{*2}=2.4624$ | 两道闸门通过（极值导数与代数验算） | approved | sec1-q4 |
| CARD-03 | REQ-03 | 偏转角积分 $\chi = \pi - 2b\int_{r_{\min}}^\infty \frac{1}{r^2}[1-U/E_T-b^2/r^2]^{-1/2}\dd r$；虹角 $\dd\chi/\dd b^*=0$ 处导数为零 | 两道闸门通过（微商相除消时间复核） | approved | sec2-q1 |
| CARD-04 | REQ-04 | 刚球偏转角 $\chi = \pi - 2\arcsin(b/d)$，微分截面 $I(\theta)=\frac14d^2$（各向同性），总截面 $\int I\dd\omega = \pi d^2$ | 两道闸门通过（立体角积分解析复核） | approved | sec2-q2 |
| CARD-05 | REQ-05 | SCT 激发函数 $\sigma_r(E_T)=\pi d^2(1-E_0/E_T)$；Langevin 离子-分子激发函数 $\sigma_r(E_T)=\pi(2\alpha e^2/E_T)^{1/2}$ | 两道闸门通过（中心连线动能投影与离心垒求导复核） | approved | sec2-q5 |
| CARD-06 | REQ-06 | 鱼叉机理交叉距离 $r_c = e^2/[I(M)-E(X_2)]$；旁观者模型相对平动能比值 $E_T'/E_T = \cos^2\beta = \frac{m_Am_C}{m_{AB}m_{BC}}$ | 两道闸门通过（库仑能补偿与三体动量守恒复核） | approved | sec2-q6 |
| CARD-07 | REQ-07 | 宏观速率常数积分 $K(T)=(\frac{1}{\pi\mu})^{1/2}(\frac{2}{kT})^{3/2}\int_0^\infty E_T\exp(-E_T/kT)\sigma_r(E_T)\dd E_T$；SCT 导出 $K(T)=\langle v\rangle\pi d^2\exp(-E_0/kT)$ | 两道闸门通过（雅可比换元与分部积分复核） | approved | sec3-q1 |
| CARD-08 | REQ-08 | Tolman 活化能关系式 $E_a = RT^2\frac{\dd\ln K}{\dd T} = \bar E_r - \bar E_T$；SCT 活化能 $E_a = NE_0 + \frac12RT$ | 两道闸门通过（积分商对数微分推导复核） | approved | sec3-q4 |

以上 8 张卡片全部经过来源闸门与数学/教学闸门双重核验，状态均为 `approved`。
