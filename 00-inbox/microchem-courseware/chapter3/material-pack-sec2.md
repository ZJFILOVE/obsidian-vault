# 第 II 节批准材料包 (material-pack-sec2)

本材料包由主 Agent 经两道闸门核验后冻结，仅含第 II 节写作所需且状态为 `approved` 的材料卡片。切片子 Agent 严禁使用未批准材料或自行检索编造。

## 批准卡片

### 卡片 CARD-03
- **卡片 ID**: `CARD-03` | **对应需求**: `REQ-03` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter3.tex` L208-242 来源闸门核验通过，阻抑弛豫法装置与稳态速率平衡正比性证明复核通过。
- **落点**: sec2-q1, sec2-q2
- **核心事实与数学公式**:
  1. 产物振转激发态自发辐射发射红外化学发光（IRC）。
  2. 阻抑弛豫法采用快速抽空（约 $10^{-4}\ \mathrm{torr}$）与液氮冷壁，气相与器壁碰撞弛豫均被大大阻抑。
  3. 卤化氢分子振动辐射寿命为毫秒量级，远大于分子通过视场的平均停留时间 $\tau$（小一个数量级）。
  4. 稳态平衡方程化简为生成速率等于抽走速率：$R(v',J') \approx N_{v'J'}\tau^{-1}$。
  5. 细致速率常数与能级布居数严格成正比：$k(v',J',T)\propto N_{v'J'}$。
- **不得提前泄露的信息**: 不要提前泄露 $\mathrm{Cl+HI}$ 反应各个振动能级上的具体布居反转数值。

### 卡片 CARD-04
- **卡片 ID**: `CARD-04` | **对应需求**: `REQ-04` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter3.tex` L249-274 来源闸门核验通过，Tolman 可利用能量推导与能量分配分数复核通过。
- **落点**: sec2-q4
- **核心事实与数学公式**:
  1. 依据 Tolman 活化能定义，反应总的可利用能量：$E_{\mathrm{tot}} = -\Delta H_0^\circ + E_a + \frac52 RT$（包含零点放热、活化能与反应物平均热能）。
  2. 振动平均能量分配分数：$\langle f_{v'}\rangle = \frac{\langle E_{v'}\rangle}{E_{\mathrm{tot}}} = \frac{1}{E_{\mathrm{tot}}}\frac{\sum_{v'} k(v',T)E_{v'}}{\sum_{v'} k(v',T)}$。
  3. 平动平均能量分配分数由能量守恒互补求得：$\langle f_{T'}\rangle = 1 - \langle f_{v'}\rangle - \langle f_{R'}\rangle$。
  4. $\mathrm{Cl+HI\to HCl+I}$ 实验测得：$\langle f_{v'}\rangle=0.70,\ \langle f_{R'}\rangle=0.13,\ \langle f_{T'}\rangle=0.17$。
- **不得提前泄露的信息**: 不要直接给出各分数数值，由学生通过公式逐步代入求出。
