# 第 III 节批准材料包 (material-pack-sec3)

本材料包由主 Agent 经两道闸门核验后冻结，仅含第 III 节写作所需且状态为 `approved` 的材料卡片。切片子 Agent 严禁使用未批准材料或自行检索编造。

## 批准卡片

### 卡片 CARD-07
- **卡片 ID**: `CARD-07` | **对应需求**: `REQ-07` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter1.tex` L638-703 来源闸门核验通过，单能向宏观速率加权积分与分部积分独立重算通过。
- **落点**: sec3-q1, sec3-q2
- **核心事实与数学公式**:
  1. 单能速率常数 $k(v) = v\sigma_r(v)$。
  2. 麦克斯韦热平衡相对速度加权积分：$K(T) = \int_0^\infty f(v,T)v\sigma_r(v)\dd v$。
  3. 平动能形式积分：$K(T) = (\frac{1}{\pi\mu})^{1/2}(\frac{2}{kT})^{3/2}\int_0^\infty E_T\exp(-\frac{E_T}{kT})\sigma_r(E_T)\dd E_T$。
  4. SCT 代入积分（分部积分）：$K_{\mathrm{SCT}}(T) = (\frac{8kT}{\pi\mu})^{1/2}\pi d^2\exp(-\frac{E_0}{kT}) = \langle v\rangle\pi d^2\exp(-\frac{E_0}{kT})$。
  5. Langevin 代入积分：$K(T) = 2\pi e(\frac{\alpha}{\mu})^{1/2}$（速率常数与温度无关）。

### 卡片 CARD-08
- **卡片 ID**: `CARD-08` | **对应需求**: `REQ-08` | **状态**: `approved`
- **材料类型**: `REUSE-ORIGINAL`
- **核验结论**: `chapter1.tex` L708-754 来源闸门核验通过，Tolman活化能对数微分商求导与温度依赖独立重算通过。
- **落点**: sec3-q4, sec3-q5
- **核心事实与数学公式**:
  1. 实验活化能定义：$E_a = RT^2\frac{\dd\ln K(T)}{\dd T}$。
  2. SCT 活化能与指前因子：$E_a = NE_0 + \frac12RT$，$A = (\frac{8kT}{\pi\mu})^{1/2}\pi d^2 e^{1/2}$。
  3. Tolman 统计解释一般表达式：
     $$E_a = N\frac{\int_0^\infty \sigma_r(E_T)E_T^2\exp(-E_T/kT)\dd E_T}{\int_0^\infty \sigma_r(E_T)E_T\exp(-E_T/kT)\dd E_T} - \frac32RT = \bar E_r - \bar E_T$$
     其中 $\bar E_r$ 为反应分子的平均能量，$\bar E_T$ 为全部热平衡分子的平均平动动能。
  4. 活化能随温度变化的规律：
     - 当 $\sigma_r(E_T) \propto (E_T - E_0)^{1/2}/E_T$ 时，$E_a = E_0$，活化能与温度无关；
     - 当 $\sigma_r$ 为常数时，$E_a < E_0$ 且随温度升高而下降；
     - 其它形式激发函数通常 $E_a > E_0$ 且随温度升高而微弱增加；
     - 低温下 $E_a \approx NE_0$。
