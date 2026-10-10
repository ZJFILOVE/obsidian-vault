# 第 I 节批准材料包 (material-pack-sec1)

本材料包由主 Agent 经两道闸门核验后冻结，仅含第 I 节写作所需且状态为 `approved` 的材料卡片。切片子 Agent 严禁使用未批准材料或自行检索编造。

## 批准卡片

### 卡片 CARD-01
- **卡片 ID**: `CARD-01` | **对应需求**: `REQ-01` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter4.tex` L36-98 来源闸门核验通过，产物角分布三种形态与 $1/\sin\theta$ 立体角推导复核通过。
- **落点**: sec1-q1, sec1-q2, sec1-q3
- **核心事实与数学公式**:
  1. 向前散射（直接剥夺机理，如 $\mathrm{K+I_2}$）：角分布峰值位于 $\theta\approx 0^\circ$，产物相对速度接近圆心，释放能量绝大部分转化为产物内部振转能态，直接碰撞时间极短。
  2. 向后散射（直接回弹机理，如 $\mathrm{K+CH_3I}$）：角分布峰值位于 $\theta>150^\circ$，接近最大相对平动能 $E'_{T,\max}$，释放能量绝大部分转化为产物相对平动能；反应截面随碱金属电离势降低而增大（鱼叉机理）。
  3. 前后对称散射（长寿命碰撞络合物机理，如 $\mathrm{Cs+RbCl}$）：络合物寿命远大于转动周期 $\tau_{\mathrm{comp}}\gg \tau_{\mathrm{rot}}$，失去初生方向记忆。
  4. 轨道角动量主导下，相对速度局限于垂直总角动量的平面内，由空间立体角微元转换式 $I(\theta)\propto \frac{\dd N(\theta)}{2\pi\sin\theta\dd\theta}$ 严格导出极角分布遵循 $I(\theta)\propto \frac{1}{\sin\theta}$，在 $\theta=0^\circ$ 和 $180^\circ$ 方向最强，而在 $90^\circ$ 最弱。
- **不得提前泄露的信息**: 不要提前泄露后续章节的反应物方位效应与 Walsh 规则。
