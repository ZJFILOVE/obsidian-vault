# 第 II 节批准材料包 (material-pack-sec2)

本材料包由主 Agent 经两道闸门核验后冻结，仅含第 II 节写作所需且状态为 `approved` 的材料卡片。切片子 Agent 严禁使用未批准材料或自行检索编造。

## 批准卡片

### 卡片 CARD-03
- **卡片 ID**: `CARD-03` | **对应需求**: `REQ-03` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter1.tex` L210-241 来源闸门核验通过，偏转积分与极值导数独立重算通过。
- **落点**: sec2-q1
- **核心事实与数学公式**:
  1. 偏转角 $\chi = \pi - 2\phi_0$。
  2. 微分方程相除：$\frac{\dd\phi}{\dd r} = -\frac{b}{r^2}[1 - \frac{U(r)}{E_T} - \frac{b^2}{r^2}]^{-1/2}$。
  3. 积分得到偏转函数：$\chi = \pi - 2b\int_{r_{\min}}^\infty \frac{1}{r^2}[1 - \frac{U(r)}{E_T} - \frac{b^2}{r^2}]^{-1/2}\dd r$。
  4. 轨线分类：高能推斥（正偏转）、低能吸引（负偏转）、临界能量达到离心垒顶时环行（orbiting，$\chi\to-\infty$）。
  5. 虹角 $\chi_r$（$\dd\chi/\dd b^* = 0$ 处的极值负偏转角）、荣角 $\chi_g$（$\chi=0$）。

### 卡片 CARD-04
- **卡片 ID**: `CARD-04` | **对应需求**: `REQ-04` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter1.tex` L242-324 来源闸门核验通过，立体角微元通量平衡与刚球截面积分独立重算通过。
- **落点**: sec2-q2
- **核心事实与数学公式**:
  1. 柱对称散射立体角元 $\dd\omega = 2\pi\sin\theta\dd\theta$；散射角 $\theta = |\chi(b)|$。
  2. 微分截面定义：$I(\theta,E_T) = \frac{\dd\sigma}{\dd\omega} = \frac{b}{\sin\theta}|\frac{\dd b}{\dd\theta}|$。
  3. 刚球模型偏转角 $\chi = \pi - 2\arcsin(b/d)$（$b\le d$）。
  4. 刚球微分截面：$I(\theta,E_T) = \frac14d^2$（各向同性，与 $\theta$ 及能量无关）。
  5. 总截面积分：$\sigma(E_T) = 2\pi\int_0^\pi I\sin\theta\dd\theta = \pi d^2$。

### 卡片 CARD-05
- **卡片 ID**: `CARD-05` | **对应需求**: `REQ-05` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter1.tex` L409-526 来源闸门核验通过，SCT、MSCT与Langevin激发函数公式独立重算通过。
- **落点**: sec2-q5
- **核心事实与数学公式**:
  1. SCT 模型：中心连线平动能 $E_{1C} = E_T(1 - b^2/d^2) \ge E_0$；最大碰撞参数 $b_{\max} = d(1 - E_0/E_T)^{1/2}$；激发函数 $\sigma_r(E_T) = \pi d^2(1 - E_0/E_T)$。
  2. MSCT 模型：$r=D$ 界面取向势能 $U(D) = E_0 + 2E'(1-\cos\phi)$；激发函数 $\sigma_r(E_T) = \frac{\pi D^2(E_T - E_0)^2}{4E_T E'}$。
  3. Langevin 模型：极化势 $U(r) = -\frac{\alpha e^2}{2r^4}$；越过离心垒 $r_{\max} = (\frac{\alpha e^2}{E_Tb^2})^{1/2}$；最大碰撞参数 $b_{\max} = (\frac{2\alpha e^2}{E_T})^{1/4}$；激发函数 $\sigma_r(E_T) = \pi(\frac{2\alpha e^2}{E_T})^{1/2}$（截面随平动能增加而下降）。

### 卡片 CARD-06
- **卡片 ID**: `CARD-06` | **对应需求**: `REQ-06` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter1.tex` L541-596 来源闸门核验通过，鱼叉交叉距离与旁观者动量守恒独立重算通过。
- **落点**: sec2-q6
- **核心事实与数学公式**:
  1. 剥夺型（前向散射，大 $b$，大截面，如 $\mathrm{K+I_2}$）vs 回弹型（后向散射，小 $b$，小截面，如 $\mathrm{K+CH_3I}$）。
  2. 鱼叉机理：电子转移发生在共价曲线与离子对曲线交叉点 $r_c = \frac{e^2}{I(M) - E(X_2)}$；反应截面 $\sigma_r \approx \pi r_c^2$。
  3. 旁观者模型：转移轻原子，重原子速度不变，平动能比值 $\frac{E'_T}{E_T} = \frac{m_Am_C}{m_{AB}m_{BC}} = \cos^2\beta$；剩余反应放能进入产物内部振转能态。
