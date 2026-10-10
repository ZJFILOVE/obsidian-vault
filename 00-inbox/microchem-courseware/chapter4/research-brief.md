# 研究核验与材料需求简报 (research-brief) —— 第四章

## 一、 材料需求清单与两道闸门核验

| 需求ID | 对应知识点 | 材料类型 | 教学功能说明 | 学生已知前置 | 计划落点 | 来源类型与证据 | 主 Agent 闸门裁决 |
|---|---|---|---|---|---|---|---|
| REQ-01 | S4-01, S4-02, S4-03 | entry / proof | 产物角分布三种形态（向前剥夺、向后回弹、前后对称络合物），总角动量守恒证明平面散射 $I(\theta)\propto 1/\sin\theta$ | 质心坐标系与相对速度 | sec1 导言与 sec1-q1~q3 | REUSE-ORIGINAL (`chapter4.tex` L36-98) | approved (CARD-01) |
| REQ-02 | S4-04, S4-05 | entry / transfer | 六极聚焦电场定向偶极分子（$\mathrm{CH_3I}$ 首尾 4 倍截面差），Walsh 规则与势能面弯曲构型导致侧向散射（$\mathrm{D+I_2}$ $105^\circ$ 峰） | 电偶极矩与分子轨道理论 | sec2 导言与 sec2-q1, sec2-q2 | REUSE-ORIGINAL (`chapter4.tex` L99-118) | approved (CARD-02) |
| REQ-03 | S4-06 | entry / proof | $\mathrm{F+H_2(D_2)}$ 产物振动激发占优（$60\%\sim 65\%$）与布居反转，Levine-Bernstein 惊奇度线性公式 $I(f_{v'})=I_0+\lambda_{v'}f_{v'}$ 及斜率 $\lambda_{v'}\approx -5.7$ 物理本质 | 统计先验几率与信息熵 | sec3 导言与 sec3-q1 | REUSE-ORIGINAL (`chapter4.tex` L119-158) | approved (CARD-03) |
| REQ-04 | S4-07, S4-08 | synthesis / counterexample | 重轻重（$\mathrm{Cl+HI}$）混合释能入振动 vs 轻重重（$\mathrm{H+Cl_2}$）推斥释能入平动；$\mathrm{K+HBr}$ 角动量守恒约束 $J\approx L\approx j'$ 导出大转动激发 | 旁观者模型与角动量合成 | sec3-q2, sec3-q3 | REUSE-ORIGINAL (`chapter4.tex` L159-203) | approved (CARD-04) |
| REQ-05 | S4-09 | transfer / boundary | 碰撞络合物出口通道特征对能量分配的影响：松弛过渡态（无垒统计指数衰减）vs 紧缚过渡态（有垒非统计增强平动与特定振动） | 单分子反应理论与过渡态 | sec3-q4 | REUSE-ORIGINAL (`chapter4.tex` L204-228) | approved (CARD-05) |
| REQ-06 | S4-10, S4-11 | synthesis / review | 反应物能量选择三大模式与 Polanyi 规则验证（$\mathrm{K+HCl}$ 激光振动选态截面暴增百倍）；态-态动力学与飞秒激光调控前沿展望 | 第二章能垒位置与微观可逆性 | sec4 导言与 sec4-q1, sec4-q2 | REUSE-ORIGINAL (`chapter4.tex` L229-273) | approved (CARD-06) |

## 二、 批准卡片清单 (Approved Cards)

| 卡片ID | 对应需求 | 核心结论与数学事实 | 核验闸门 | 状态 | 落点 |
|---|---|---|---|---|---|
| CARD-01 | REQ-01 | 向前散射对应直接剥夺，释放能量进入产物内能；向后散射对应直接回弹，释放能量转化为产物平动能；长寿命络合物多次转动失去方向记忆，轨道角动量主导下由立体角微元严格证明 $I(\theta)\propto 1/\sin\theta$（$0^\circ, 180^\circ$ 极化峰） | 两道闸门通过（能量守恒与立体角微积分解析复核） | approved | sec1-q1~q3 |
| CARD-02 | REQ-02 | 六极场微观态聚焦定向偶极分子；$\mathrm{CH_3I}$ I 端进攻产物截面为甲基端的 4 倍；Walsh 规则预言三原子稳定构型，共线势能面有利于轴向对心反应，而 $\mathrm{HX_2}$ 弯曲构型导致产物侧向散射峰移向 $105^\circ$ | 两道闸门通过（实验装置与分子构型 Walsh 规则复核） | approved | sec2-q1, sec2-q2 |
| CARD-03 | REQ-03 | $\mathrm{F+H_2(D_2)}$ 反应所释放能量中 $60\%\sim 65\%$ 进入振动并产生布居反转；惊奇度线性关系 $I(f_{v'}) = -\ln\frac{P(f_{v'})}{P^0(f_{v'})} = I_0 + \lambda_{v'} f_{v'}$，实验测得 $\lambda_{v'}\approx -5.7$，起到了广义非平衡温度参数作用 | 两道闸门通过（惊奇度数学定义与实验数据线性拟合复核） | approved | sec3-q1 |
| CARD-04 | REQ-04 | 重轻重质量组合（$\mathrm{Cl+HI}$）表现为混合释能，$\langle f_v\rangle\approx 0.70$；轻重重组合（$\mathrm{H+Cl_2}$）表现为强推斥平动释能，$\langle f_T\rangle\approx 0.54$；$\mathrm{K+HBr}$ 反应由轻 H 原子反冲导致 $J\approx L\approx j'$，产物转动能与初始碰撞能相当 | 两道闸门通过（动量守恒与角动量守恒代数推导复核） | approved | sec3-q2, sec3-q3 |
| CARD-05 | REQ-05 | 碰撞络合物反应中，松弛过渡态（出口无势垒）能量统计均分，导出指数衰减振动分布 $P(v')\propto \exp(-\beta E_v')$；紧缚过渡态（出口有额外能垒）将势垒潜能大部分转化为平动能，破坏统计分配并显著增强特定振动模式 | 两道闸门通过（单分子相空间理论与出口势垒动力学效应复核） | approved | sec3-q4 |
| CARD-06 | REQ-06 | 无阈能放能反应截面随动能下降；有阈能放能反应平动能克服早垒；吸能反应能垒在出口谷（晚垒），$\mathrm{K+HCl}$ 激光将 $v=0$ 激发至 $v=1$ 反应截面从 $0.15\ \text{\AA}^2$ 剧增到 $20\ \text{\AA}^2$，严格验证 Polanyi 规则；态-态动力学与飞秒光化学前沿 | 两道闸门通过（动力学曲线分类与激光选态实验算例复核） | approved | sec4-q1, sec4-q2 |

以上 6 张卡片全部经过来源闸门与数学/教学闸门双重核验，状态均为 `approved`。
