---
title: "Neovim + Obsidian Snippets 使用指南"
type: reference
category:
topic:
tools:
aliases:
  - "LaTeX snippets"
  - "Neovim snippets"
status: active
source:
created: 2026-09-04
tags:
  - reference
  - neovim
  - latex
  - obsidian
updated: 2026-09-10
---

# Neovim + Obsidian Snippets 使用指南

这篇笔记对应当前 Neovim 配置，整理了 LuaSnip、LaTeX/Markdown snippets，以及 Obsidian 相关的图片、问答和 Claim 模板。

## 1. 基本用法

snippets 不是 VimTeX 的命令，而是“触发词”。基本流程是：

1. 在 `.tex` 或 `.md` 文件中进入插入模式。
2. 输入触发词。
3. 自动 snippets 会直接展开；普通 snippets 可以按 `Ctrl-Space` 打开补全，再按 `Enter` 或 `Tab` 选择。
4. 展开后用 `Tab` 跳到下一个占位符，用 `Shift-Tab` 回到上一个占位符。

当前配置中的补全按键：

| 按键 | 作用 |
| --- | --- |
| `Tab` | 展开 snippet、选择下一个补全项、跳到下一个占位符 |
| `Shift-Tab` | 上一个补全项或上一个占位符 |
| `Ctrl-Space` | 手动打开补全菜单 |
| `Ctrl-j` / `Ctrl-k` | 在补全菜单中向下/向上选择 |
| `Enter` | 确认当前补全项 |

注意：`Tab` 只有在 LuaSnip 认为当前有可展开片段或占位符时才执行 snippet 操作，否则就是普通 Tab。

## 2. Markdown 中的数学公式

你的配置对 Markdown 开启了 LaTeX snippets：

```lua
allow_on_markdown = true
```

### 2.1 公式环境

这些触发词在普通 Markdown 文本中使用：

| 触发词 | 展开结果 | 说明 |
| --- | --- | --- |
| `mk` | `$...$` | 行内公式 |
| `dm` | `$$\n  ...\n$$` | 独立公式块 |
| `eq` | `$$\n  ...\n$$` | 你自己配置的独立公式 snippet |

例如输入 `mk` 后按 `Tab`，可得到行内数学环境；光标会停在公式内容的位置。

### 2.2 数学环境中的 snippets

下面这些要在 `$...$` 或 `$$...$$` 内使用。Markdown 中的数学区域由 Treesitter 识别，代码块中的内容不会被当作数学环境。

#### 常用结构

| 触发词 | 作用 |
| --- | --- |
| `//` | 分式 `\frac{}{}` |
| `sum` | 求和 |
| `taylor` | Taylor 展开形式 |
| `lim` / `limsup` | 极限 / 上极限 |
| `prod` | 连乘 |
| `part` | 偏导数 |
| `ddx` | 普通导数 |
| `dint` | 带上下限积分 |
| `pmat` | `pmatrix` 矩阵 |
| `bmat` | `bmatrix` 矩阵 |
| `cvec` | 列向量 |
| `case` | cases 分段公式 |
| `sequence` | 从 `m` 到无穷的数列 |
| `norm` | 范数 `\|x\|` |
| `lr` / `lr(` | `\left( ... \right)` |
| `lr&#124;` | `\left\| ... \right\|`；触发词末尾是竖线 `|` |
| `lr[` | `\left[ ... \right]` |
| `lr{` / `lrb` | `\left\{ ... \right\}` |
| `lra` | `\left< ... \right>` |
| `floor` / `ceil` | 向下取整 / 向上取整 |

#### 上下标、字体和常用符号

| 触发词 | 展开结果 |
| --- | --- |
| `sq` | `\sqrt{}` |
| `hat` / `bar` | `\hat{}` / `\overline{}` |
| `td` / `rd` | 上标 `^{}` / 带括号上标 |
| `sr` / `cb` | 平方 `^2` / 立方 `^3` |
| `__` | 下标 `_{}` |
| `invs` | 逆 `^{-1}` |
| `mcal` | `\mathcal{}` |
| `tt` | `\text{}` |
| `stt` | 文本下标 |
| `RR` / `QQ` / `ZZ` / `NN` | `\mathbb{R}` / `\mathbb{Q}` / `\mathbb{Z}` / `\mathbb{N}` |
| `DD` / `HH` | `\mathbb{D}` / `\mathbb{H}` |
| `OO` | 空集 `\O` |
| `inf` / `ooo` | `\infty` |
| `inn` | `\in` |
| `notin` | `\not\in` |
| `EE` / `AA` | `\exists` / `\forall` |
| `cc` / `Nn` | `\subset` / `\cap` |
| `UU` / `uuu` | `\cup` / `\bigcup` |
| `||` | `\mid` |
| `lll` | `\ell` |
| `nabl` | `\nabla` |
| `xx` / `**` | `\times` / `\cdot` |
| `<>` | `\diamond` |
| `<<` / `>>` | `\ll` / `\gg` |

#### 逻辑、关系和箭头

| 触发词 | 展开结果 |
| --- | --- |
| `->` / `-->` | `\to` / `\longrightarrow` |
| `<->` | `\leftrightarrow` |
| <code>&#61;></code> / `simp` | `\implies` / `\Rightarrow` |
| <code>&#61;<</code> | `\impliedby` |
| `iff` / `siff` | `\iff` / `\Leftrightarrow` |
| <code>&#61;&#61;</code> | 对齐环境中的 `&`<code>&#61;</code>` ... \\\\` |
| `!`<code>&#61;</code> | `\neq` |
| <code>&#60;&#61;</code> / <code>&#62;&#61;</code> | `\le` / `\ge` |
| `:`<code>&#61;</code> | `\coloneqq` |
| `~~` | `\sim` |
| `compl` | 补集上标 `^{c}` |
| `...` | `\ldots` |
| `!>` | `\mapsto` |
| `\texttt{\\\\\\}` | `\setminus`；这是连续三个反斜杠的触发词，建议通过补全菜单选择 |

#### 集合、函数和其他

| 触发词 | 展开结果 |
| --- | --- |
| `set` | 集合括号 |
| `fun` | 函数映射形式 |
| `abs` | `\abs{}` |
| `letw` | 插入 “Let `\Omega ...` be open.” |
| `nnn` / `uuu` | `\bigcap` / `\bigcup` |
| `SI` | `\SI{}{}` |
| `rij` | 带指标和自然数条件的表达式 |
| `conj` | 共轭 `\overline{}` |
| `cvec` | 列向量 |

#### 自动模式：输入变量后接后缀

这些属于自动 snippets，通常不需要按 `Ctrl-Space`：

| 输入形式 | 结果 |
| --- | --- |
| `xbar` | `\overline{x}` |
| `xybar` | `\overline{xy}` |
| `xund` | `\underline{x}` |
| `xdot` | `\dot{x}` |
| `xhat` | `\hat{x}` |
| `xora` / `xola` | `\overrightarrow{x}` / `\overleftarrow{x}` |
| `x2` | `x_{2}` |
| `x_12` | `x_{12}` |
| `x/` | `\frac{x}{}` |
| `(x+y)/` | `\frac{x+y}{}` |
| `a.` / `ab.` | `\vec{a}` / `\vec{ab}` |

函数和希腊字母也支持后缀形式。例如在数学环境中输入 `alpha`、`beta`、`sin`、`cos`、`int`，会自动变成对应的 `\alpha`、`\beta`、`\sin`、`\cos`、`\int`。支持的函数包括：

```text
sin cos tan csc sec cot ln log exp star perp int
```

另外还定义了一个间距触发词 `q?quad`。它包含特殊字符，建议在补全菜单中确认后再使用。

支持的希腊字母包括：

```text
alpha beta chi delta epsilon eta gamma iota kappa lambda mu
nu omega phi pi psi rho sigma tau theta zeta
varepsilon varphi varrho vartheta
```

通常不要在已有反斜杠后重复触发，例如已经写了 `\alpha` 时不要再输入 `alpha`。

## 3. Markdown 普通文本 snippets

这些是你自己在 `/home/zhu/.config/nvim/lua/zhu/markdown.lua` 中配置的 snippets，作用于 Markdown 普通文本区域。

| 触发词 | 用法 |
| --- | --- |
| `beg` | 在行首生成 `\begin{...}` 和 `\end{...}` |
| `ali` | 在行首生成 `align*` 环境 |
| `bigfun` | 在行首生成一个函数映射的 `align*` 模板 |
| `q` | 生成 Obsidian 的 question callout |
| `claim` | 生成 Claim / Evidence 结构 |
| `eq` | 生成 `$$...$$` 独立公式 |

`beg`、`ali`、`bigfun` 要尽量在新行行首触发；它们只在非数学环境中生效。

## 4. Obsidian 图片 snippets

### 4.1 用 `img` 选择图片

在 Markdown 插入模式中输入：

```text
img
```

然后按 `Tab`。Neovim 会打开 `Vault images` Telescope 窗口，搜索并选择 vault 中已有的图片，最后插入：

```markdown
![[图片相对路径.png]]
```

图片搜索范围是整个 vault：

```text
/home/zhu/knowledge/vault
```

支持的图片格式：`png`、`jpg`、`jpeg`、`webp`、`gif`、`svg`、`bmp`、`avif`。

### 4.2 用 `imgc` 选择图片并添加图注

输入：

```text
imgc
```

按 `Tab` 选择图片后，会弹出“图注”输入框。结果类似：

```markdown
![[图片相对路径.png]]

*这是一条图注*
```

图注可以留空。

### 4.3 直接使用快捷键

在 Markdown 普通模式中：

| 快捷键 | 作用 |
| --- | --- |
| `Space o i` | 打开 vault 图片选择器并插入图片 |
| `Space o f` | 在 vault 中搜索 Markdown 笔记 |
| `:Vault` | 执行 vault 笔记搜索 |

`Space o i` 相当于 `img`，默认不添加图注；需要图注时使用 `imgc`。

### 4.4 使用 Obsidian 模板插入图片

vault 中还有一个 Templater 模板：

```text
99-templates/insert-image.md
```

运行这个模板后，会选择已有图片并询问图注。它和 Neovim 的 `imgc` 功能类似，但属于 Obsidian Templater 工作流。

## 5. 如何查看当前实际加载的 snippets

先打开一个 `.md` 文件，并进入过一次插入模式，然后在 Neovim 命令行执行：

```vim
:lua local ls=require("luasnip"); for _,typ in ipairs({"snippets","autosnippets"}) do print("== "..typ.." =="); for _,s in ipairs(ls.get_snippets("markdown", {type=typ})) do print(s.trigger, s.name or "") end end
```

查看 LaTeX 文件中的 snippets，把 `markdown` 换成 `tex`：

```vim
:lua local ls=require("luasnip"); for _,typ in ipairs({"snippets","autosnippets"}) do print("== "..typ.." =="); for _,s in ipairs(ls.get_snippets("tex", {type=typ})) do print(s.trigger, s.name or "") end end
```

检查当前文件类型：

```vim
:set ft?
```

Markdown 应该显示 `filetype` 为 `markdown`。如果显示不正确，LaTeX snippets 和 Obsidian snippets 都可能不会加载。

## 6. 相关配置位置

| 内容 | 文件 |
| --- | --- |
| LaTeX snippets 插件启用 | `~/.config/nvim/lua/zhu/plugins/latex.lua` |
| Tab、补全和自动 snippets | `~/.config/nvim/lua/zhu/plugins/coding.lua` |
| Obsidian 图片、callout、Claim、公式 snippets | `~/.config/nvim/lua/zhu/markdown.lua` |
| VimTeX 配置 | `~/.config/nvim/lua/zhu/plugins/latex.lua` |
| Obsidian 图片模板 | `99-templates/insert-image.md` |
| LaTeX snippets 插件源码 | `~/.local/share/nvim/lazy/luasnip-latex-snippets.nvim/lua/luasnip-latex-snippets/` |

插件自带 snippets 位于插件目录中，直接修改可能在插件更新时被覆盖；需要新增自己的 snippets 时，建议放到 Neovim 配置中单独维护。
