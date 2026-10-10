# 第 I 节批准材料包 (material-pack-sec1)

本材料包由主 Agent 经两道闸门核验后冻结，仅含第 I 节写作所需且状态为 `approved` 的材料卡片。切片子 Agent 严禁使用未批准材料或自行检索编造。

## 批准卡片

### 卡片 CARD-01
- **卡片 ID**: `CARD-01` | **对应需求**: `REQ-01` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter3.tex` L47-99 来源闸门核验通过，超声绝热膨胀极限速度与轻载气加速动能放大计算复核通过。
- **落点**: sec1-q1, sec1-q2
- **核心事实与数学公式**:
  1. 气体绝热流动能量方程：$\frac12 V^2 + C_p T = C_p T_0$。
  2. 声速表达式：$a = (\frac{\gamma k_B T}{m})^{1/2}$，Mach 数 $M = V/a$ 满足 $\frac{T_0}{T} = 1 + \frac{\gamma-1}{2}M^2$。
  3. 极限速度：$V_t = (\frac{2k_B T_0}{m}\frac{\gamma}{\gamma-1})^{1/2}$。
  4. 载气加速效应：大量轻载气分子（如 $\mathrm{H_2}$）带动少量重反应分子（分子量为 100），重分子速度接近轻分子极限流速 $(V_t)_h \approx (V_t)_l \approx 3\times 10^3\ \mathrm{m\,s^{-1}}$，动能放大至载气的 50 倍，高达 $4.7\ \mathrm{eV}$。
- **不得提前泄露的信息**: 不要提前给出速度矢量 Newton 图的雅可比变换公式。

### 卡片 CARD-02
- **卡片 ID**: `CARD-02` | **对应需求**: `REQ-02` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter3.tex` L122-207 来源闸门核验通过，Newton 速度矢量图与相体积元守恒雅可比转换复核通过。
- **落点**: sec1-q4, sec1-q5
- **核心事实与数学公式**:
  1. 质心平动速度 $V_{\mathrm{C.M.}} = \frac{m_1 V_1 + m_2 V_2}{m_1 + m_2}$，两粒子相对速度 $V = V_1 - V_2$。
  2. 质心坐标系中质点速度：$u_1 = \frac{m_2}{m_1+m_2}V,\ u_2 = -\frac{m_1}{m_1+m_2}V$。
  3. 反应散射能量守恒：$\frac12 \mu V^2 + E_{\mathrm{int}} + \Delta D_0 = \frac12 \mu' V'^2 + E_{\mathrm{int}}'$。
  4. 速度空间相体积元粒子数守恒：$\dd\tau_{\mathrm{C.M.}} = u_{AB}'^2\dd u'\dd^2\omega = \dd\tau_{\mathrm{Lab}} = V_{AB}'^2\dd V'\dd^2\Omega$。
  5. 雅可比行列式与截面变换式：$J = \frac{u_{AB}'^2}{V_{AB}'^2}$，即 $I_r(\theta,u') = \frac{u_{AB}'^2}{V_{AB}'^2} I_r(\Theta,V')$。
- **不得提前泄露的信息**: 不要直接给出雅可比转换因子的最终形式，留给学生推导证明。
