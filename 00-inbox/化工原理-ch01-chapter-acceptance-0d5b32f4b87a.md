scope: chapter
conclusion: PASS
digest: 0d5b32f4b87acade864b9a1b92ec12e60e2e3b27e6e637e53ef7ac8947b786e9

================================================================================
化工原理学案 第一章 独立教学验收阶段二审读报告
================================================================================

【基本信息】
• 范围: scope=chapter (覆盖全部 21 个 QID)
• 版本摘要: 0d5b32f4b87acade864b9a1b92ec12e60e2e3b27e6e637e53ef7ac8947b786e9
• 学生版 PDF 哈希: bfe2fc04d3572fd4308d713bce353569f48e3c72956658c215f60fb59714745c
• 教师版 PDF 哈希: bdc46121cc83d26e85961ba59a8c08d478794e5c5d095888e13d572119db4dcc
• 角色: 独立教学验收专员 (gemini-3.8-flash-high，新上下文，未参与规划写作)
• 阶段一记录: stage1.json (21题已冻结，0实质问题，PASS)
• 阶段二结论: PASS | 遗留实质问题: 0

【前轮实质问题复验裁决】
• ISSUE-17A-01 (sec4-combustion-heat, Part a, answer-leak):
  前轮第8页题17(a)题干泄露待求空气量"2857 g·mol/h"。本轮复查 sec4.tex 第246行已删除该泄露，改为"计算实际供入的空气流量 A（以 kg·mol/h 表示）及出炉烟道气中各组分（CO2, O2, N2）的摩尔流量。"。经实测审读学生版渲染图 page-08.png，题干无泄露，图1.7-2标注为符号变量 A，图文自洽，学生依 20% 过量空气率独立求解。
  裁决结果: fixed (复验摘要: 0d5b32f4b87acade864b9a1b92ec12e60e2e3b27e6e637e53ef7ac8947b786e9)。

【21 题独立数值复算与教学核对】
编写并运行独立脚本 independent-calculations.py 验证闭环，全部吻合：
1. sec1-entry: 动量/热量/质量传递识别准确；机械分离与传质分离热力学机理严密。
2. sec1-id-units: 黏度 Pa·s (kg·m^-1·s^-1)、1 cP=10^-3 Pa·s、表面张力 1 dyn/cm=10^-3 N/m 闭合。
3. sec1-calc-gc: 地球重力 100.0 lbf、月球 16.53 lbf、加速度 8.0435 ft/s^2 (2.452 m/s^2) 准确。
4. sec1-dim-homo: 自然对流公式换元常数 1.320 准确。
5. sec1-prac-unprompt: 湍流管压降公式换元常数 0.4885 准确。
6. sec2-entry: 状态温度 293.15 K, 353.15 K；过程温差 60.0 ℃ = 60.0 K = 108.0 °F；加273.15辨析正确。
7. sec2-mixture-mw: 混合气 M_avg=28.12 g/mol、标态密度 1.15 kg/m^3 及质量分数准确。
8. sec2-solution-conc: 15 wt% NaCl 溶液 x=0.0516、166.2 g/L、2.844 mol/L 准确。
9. sec2-antoine-p: 正庚烷常压沸点 98.4 ℃、80 kPa 真空下沸点 53.0 ℃ 准确。
10. sec3-entry: 浓缩汁 122.07 kg/h、蒸发水 877.93 kg/h，水分独立闭环验算无误。
11. sec3-recycle-cryst: 晶体 208.33 kg/h、水 791.67 kg/h、循环母液 766.67 kg/h、浓缩液 975.00 kg/h 准确。
12. sec3-bypass-juice: 调和产品 168.57 kg/h、旁路流 66.94 kg/h、主进料 933.06 kg/h、分流比 6.69% 准确。
13. sec3-combustion-rxn: 净理论氧 14.65 kmol、空气 83.71 kmol、干烟气 CO2 19.82% 准确。
14. sec4-entry: 变温显热积分 110072 kJ、平均热容 29.35 kJ/(kmol·K)、潜热 1.129×10^6 kJ 准确。
15. sec4-hx-balance: 换热负荷 324800 kJ/h (90.22 kW)、水流量 7715.0 kg/h (含3%损失 7946.4 kg/h) 准确。
16. sec4-evap-enthalpy: 蒸发器 L=333.33 kg/h、W=666.67 kg/h、Q=487.87 kW、生蒸汽 797.64 kg/h、经济性 0.836 准确。
17. sec4-combustion-heat: 空气 A=2.857 kg·mol/h、Hin=11417.9 kJ/h、反应放热 282990 kJ/h、Hout=121074.8 kJ/h、移热负荷 48.15 kW 准确。
18. sec5-entry: 辛普森求积 1795.50 kJ/kmol、梯形 1795.75 kJ/kmol、相对偏差 0.0139% 准确。
19. sec5-sewage-flow: 污水 4813.33 m^3 (超标)、COD 1203.33 kg、步长缩短截断误差降至 1/256 准确。
20. sec5-unprompted-integ: PFR 积分 8.1133、空时 16.23 s、体积 0.811 m^3 准确。
21. sec5-review: 大边界宏观解耦与全循环惰性杂质累积破坏稳态机理分析深刻。

【题目来源与主控脚本核查】
• 题目来源准确对应 EPUB 重排 PDF 页序，原书例题工况图表一致；自编题均明确标明教学假设，未混称印刷页或虚构实测。
• 主控 verify_calculations.py 经检查数据与公式正确对应当前版本。本验收以独立脚本为准。

【双版视觉排版审读】
实际渲染 student.pdf (10页) 与 teacher.pdf (35页) 全部图片审读：双栏高度均衡，总结框完整无跨页，第8页排版整洁自洽，留白充足无溢出。真实排版记录已写入 .pd/layout-review.json 并绑定当前双版 PDF 哈希。

【验收结论】
PASS。全章教学闭环，数值独立验证通过，排版合格，无遗留问题。
