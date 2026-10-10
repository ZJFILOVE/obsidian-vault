# 研究核验与材料需求简报 (research-brief) —— 第三章

## 一、 材料需求清单与两道闸门核验

| 需求ID | 对应知识点 | 材料类型 | 教学功能说明 | 学生已知前置 | 计划落点 | 来源类型与证据 | 主 Agent 闸门裁决 |
|---|---|---|---|---|---|---|---|
| REQ-01 | S3-02, S3-03 | entry | 超声喷嘴源绝热流动能量方程推导，极限速度 $V_t$ 及轻载气加速重分子动能放大数十倍机制 | 理想气体热力学与声速 | sec1 导言与 sec1-q1, sec1-q2 | REUSE-ORIGINAL (`chapter3.tex` L47-99) | approved (CARD-01) |
| REQ-02 | S3-05, S3-06 | proof | 质心系动量守恒 Newton 速度矢量图与相体积元守恒推导雅可比反应截面转换式 $I_r(\theta,u')=\frac{u'^2}{V'^2}I_r(\Theta,V')$ | 向量几何与立体角微元 | sec1-q4, sec1-q5 | REUSE-ORIGINAL (`chapter3.tex` L122-207) | approved (CARD-02) |
| REQ-03 | S3-07, S3-08 | entry / proof | 稳态速率平衡方程推导，比较自发辐射寿命与视场停留时间证明细致速率正比性 $k(v',J',T)\propto N_{v'J'}$ | 动力学稳态近似与光谱自发辐射 | sec2 导言与 sec2-q1, sec2-q2 | REUSE-ORIGINAL (`chapter3.tex` L208-242) | approved (CARD-03) |
| REQ-04 | S3-10, S3-11 | synthesis | 依据 Tolman 定义推导总可利用能 $E_{\mathrm{tot}}=-\Delta H_0^\circ + E_a + \frac52RT$ 并定量计算产物 $\langle f_v\rangle, \langle f_R\rangle, \langle f_T\rangle$ 分数 | 热化学与玻尔兹曼统计 | sec2-q4 | REUSE-ORIGINAL (`chapter3.tex` L249-274) | approved (CARD-04) |
| REQ-05 | S3-12, S3-13 | entry / proof | LIF 双电子态激发光谱吸收-发射 Franck-Condon 因子求和，证明 BaX 近似 $\Delta v=0$ 时荧光与基态布居线性正比 | 电子跃迁光谱与选择定则 | sec3 导言与 sec3-q1, sec3-q2 | REUSE-ORIGINAL (`chapter3.tex` L275-303) | approved (CARD-05) |
| REQ-06 | S3-14 | transfer / review | 解释 $\mathrm{Ba+HX}$ 产物非平衡初始分布，推导双脉冲延迟时间分辨 LIF 测量自由基态-态衰减速率常数动力学方程 | 延迟激发与一级反应动力学 | sec3-q3 | REUSE-ORIGINAL (`chapter3.tex` L304-310) | approved (CARD-06) |

## 二、 批准卡片清单 (Approved Cards)

| 卡片ID | 对应需求 | 核心结论与数学事实 | 核验闸门 | 状态 | 落点 |
|---|---|---|---|---|---|
| CARD-01 | REQ-01 | 绝热流动能量方程 $\frac12 V^2 + C_p T = C_p T_0$ 导出极限流速 $V_t = (\frac{2kT_0}{m}\frac{\gamma}{\gamma-1})^{1/2}$；$\mathrm{H_2}$ 载气加速分子量为 100 的重反应物使其平动能高达数个电子伏 | 两道闸门通过（绝热流体能量方程与动能放大算例复核） | approved | sec1-q1, sec1-q2 |
| CARD-02 | REQ-02 | 质心系相对速度矢量关系；速度空间相体积元守恒 $\dd\tau = u_{AB}'^2\dd u'\dd^2\omega = V_{AB}'^2\dd V'\dd^2\Omega$ 严格证明微分截面转换式 $I_r(\theta,u') = \frac{u_{AB}'^2}{V_{AB}'^2} I_r(\Theta,V')$ | 两道闸门通过（相体积元守恒与雅可比行列式解析复核） | approved | sec1-q4, sec1-q5 |
| CARD-03 | REQ-03 | 稳态速率平衡方程在冷壁低压下辐射寿命与碰撞弛豫远慢于视场抽走时间 $\tau$，严格证明细致速率常数正比于能级粒子数 $k(v',J',T)\propto N_{v'J'}$ | 两道闸门通过（稳态动力学近似与毫秒级辐射寿命对比复核） | approved | sec2-q1, sec2-q2 |
| CARD-04 | REQ-04 | Tolman 可利用总能量公式 $E_{\mathrm{tot}}=-\Delta H_0^\circ + E_a + \frac52RT$；$\mathrm{Cl+HI}$ 产物平均能量分配分数 $\langle f_v\rangle=0.70,\langle f_R\rangle=0.13,\langle f_T\rangle=0.17$ | 两道闸门通过（统计热力学平均热能与加权求和算例复核） | approved | sec2-q4 |
| CARD-05 | REQ-05 | LIF 双跃迁求和式 $I_{v''v'} = K[N_{v'} q_{v''v'} \rho]\sum \nu^4 q S$；BaX 近似 $q_{v''v'}\approx \delta_{v''v'}$ 严格证明相对荧光强度与基态粒子数线性正比 $N_{v'}\propto I_{v''v'}$ | 两道闸门通过（Franck-Condon 对角占优近似解析复核） | approved | sec3-q1, sec3-q2 |
| CARD-06 | REQ-06 | $\mathrm{Ba+HX}$ 产物非平衡初始分布；双脉冲延迟时间分辨 LIF 扫描延迟时间 $\Delta t$ 拟合荧光衰减斜率求出自由基与反应物基元碰撞的态-态细致速率常数 | 两道闸门通过（二级反应准一级伪恒定模型与实验流程复核） | approved | sec3-q3 |

以上 6 张卡片全部经过来源闸门与数学/教学闸门双重核验，状态均为 `approved`。
