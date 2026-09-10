---
title: "tmux 与 Neovim 快捷键总览"
type: reference
category:
topic:
tools:
aliases:
  - "tmux shortcuts"
  - "Neovim shortcuts"
status: active
source:
created: 2026-09-10
tags:
  - reference
  - tmux
  - neovim
  - obsidian
updated: 2026-09-10
---

# tmux 与 Neovim 快捷键总览

这篇笔记对应当前配置文件：`~/.tmux.conf` 和 `~/.config/nvim/`。

本文尽量完整列出你主动配置的快捷键、当前启用插件的主要默认快捷键，以及不同模式/文件类型下的差异。Vim/Neovim 原生自带的全部按键数量很多，本文不重复抄录；需要时可在 Neovim 使用 `:help normal-index`、`:help insert-index` 和 `:help visual-index` 查看。

## 1. 记号和核心前缀

| 记号 | 含义 |
| --- | --- |
| `C-x` | 按住 Ctrl 再按 x |
| `M-x` | 按住 Alt 再按 x；也叫 Meta-x |
| `<leader>` | Neovim 中为空格 `Space` |
| `<localleader>` | 当前也是空格 `Space` |
| `Prefix` | tmux 前缀，目前是 `C-a` |

tmux 的快捷键一般要先按 `C-a`，松开后再按后面的键。例如 `Prefix |` 就是先按 `Ctrl-a`，再按 `Shift-\`。

`C-a` 本身会被 tmux 发送给下一级程序，因此在嵌套 tmux 中可以用 `C-a C-a` 把前缀继续传进去。

Neovim 的 `<leader>ff` 就是依次按 `Space`、`f`、`f`，不是同时按。

### 1.1 常用程度标记

- ⭐ **常用**：建议优先记住，日常编辑基本会用到。
- 未标记：完整配置或插件功能，按需要使用。

## 1.2 每天优先记住的快捷键

| 环境 | 快捷键 | 作用 |
| --- | --- | --- |
| tmux | `C-a &#124;` / `C-a -` | 左右/上下分割 pane |
| tmux | `C-h` / `C-j` / `C-k` / `C-l` | 在 tmux pane 和 Neovim split 间移动 |
| tmux | `C-a m` | 最大化/恢复 pane |
| Neovim | `jk` | ⭐ 插入模式回到普通模式 |
| Neovim | `Space w` | ⭐ 保存 |
| Neovim | `Space ff` / `Space fs` | ⭐ 搜索文件/全文搜索 |
| Neovim | `Space ee` | ⭐ 打开文件树 |
| Neovim | `Space q` | ⭐ 关闭窗口 |
| Neovim | `gd` / `K` | ⭐ 跳到定义/查看文档 |
| Neovim | `u` / `C-r` / `.` | ⭐ 撤销/重做/重复操作 |
| Markdown | `Space oi` | ⭐ 选择并插入 vault 图片 |
| LaTeX | `Space ll` / `Space lv` | ⭐ 编译/查看 PDF |

下面的表格中，描述以 `⭐` 开头的项目就是高频常用操作。

## 2. tmux 快捷键

### 2.1 窗格（pane）

| 快捷键 | 作用 |
| --- | --- |
| `C-a &#124;` | ⭐ 左右分割窗格；新窗格继承当前路径 |
| `C-a -` | ⭐ 上下分割窗格；新窗格继承当前路径 |
| `C-a h` | 向左扩大当前窗格 5 格 |
| `C-a j` | 向下扩大当前窗格 5 格 |
| `C-a k` | 向上扩大当前窗格 5 格 |
| `C-a l` | 向右扩大当前窗格 5 格 |
| `C-a m` | ⭐ 最大化/恢复当前窗格 |

`h/j/k/l` 在 tmux 中是调整大小，不是切换窗格。切换窗格使用下面的 `vim-tmux-navigator` 快捷键。

### 2.2 Neovim 与 tmux 窗格之间移动

`christoomey/vim-tmux-navigator` 同时安装在 Neovim 和 tmux 中，因此不需要 tmux 前缀：

| 快捷键 | 作用 |
| --- | --- |
| `C-h` | ⭐ 移到左侧 Neovim split 或 tmux pane |
| `C-j` | ⭐ 移到下方 Neovim split 或 tmux pane |
| `C-k` | ⭐ 移到上方 Neovim split 或 tmux pane |
| `C-l` | ⭐ 移到右侧 Neovim split 或 tmux pane |
| `C-\` | 回到上一个 Neovim split 或 tmux pane |

这组键在 Neovim 内部 split 和 tmux pane 之间连续工作。

在 Neovim 终端模式中，`C-h`、`C-j`、`C-k`、`C-l` 也可以离开终端 pane 并移动到相邻 pane；`C-\` 主要是普通模式映射。

### 2.3 配置和会话

| 快捷键 | 作用 |
| --- | --- |
| `C-a r` | ⭐ 重新加载 `~/.tmux.conf` |
| `C-a M-c` | 以当前 pane 的路径作为 session 工作目录并 attach |
| `C-a C-s` | tmux-resurrect 保存当前 tmux 环境 |
| `C-a C-r` | tmux-resurrect 恢复已保存的 tmux 环境 |

注意：`C-a r` 是重新加载配置，而 `C-a C-r` 是恢复 tmux 环境，两者不同。

当前启用的 tmux 行为：

- 鼠标已开启，可以用鼠标选择窗格、调整边界和进入滚动模式。
- 新 pane 使用 `/usr/bin/zsh`。
- tmux 使用 vi copy mode。
- tmux-continuum 每 15 分钟自动保存，并在 tmux server 启动时自动恢复。
- `escape-time` 设为 10ms，减少 Neovim 按 `Esc` 时的延迟。

### 2.4 复制模式

| 快捷键 | 作用 |
| --- | --- |
| `C-a [` | ⭐ 进入 copy mode |
| `v` | ⭐ 开始选择文本 |
| `y` | ⭐ 复制选择内容 |
| `q` | 退出 copy mode（tmux 默认） |

鼠标拖动结束后不会自动执行 tmux 默认的复制动作；建议用 `v` 选择、`y` 复制。

### 2.5 TPM 插件管理

| 快捷键 | 作用 |
| --- | --- |
| `C-a I` | 安装/获取插件 |
| `C-a U` | 更新插件 |
| `C-a M-u` | 删除不在插件列表中的插件 |

当前 tmux 插件：TPM、vim-tmux-navigator、Tokyo Night 主题、tmux-resurrect、tmux-continuum。

### 2.6 tmux 常用内置快捷键

下面这些是 tmux 自带的常用按键，不是你在 `.tmux.conf` 中重新定义的；由于配置没有取消它们，也可以使用：

| 快捷键 | 作用 |
| --- | --- |
| `C-a ?` | 查看 tmux 按键帮助 |
| `C-a d` | ⭐ 脱离当前 session，session 继续后台运行 |
| `C-a c` | ⭐ 新建 window |
| `C-a n` / `C-a p` | ⭐ 下一个/上一个 window |
| `C-a 0` 至 `C-a 9` | 跳到对应编号的 window |
| `C-a ,` | 重命名当前 window |
| `C-a w` | 选择 window |
| `C-a &` | 关闭当前 window |
| `C-a x` | ⭐ 关闭当前 pane |
| `C-a z` | 最大化/恢复当前 pane；你的 `C-a m` 也有同样作用 |
| `C-a o` | 切换到下一个 pane |
| `C-a ;` | 回到上一个 pane |
| `C-a q` | 临时显示 pane 编号 |
| `C-a ]` | 粘贴 tmux 缓冲区内容 |

## 3. Neovim 基本快捷键

除特别说明外，以下都是普通模式（Normal mode）。插入模式按 `Esc` 或 `jk` 回到普通模式。

### 3.1 文件和窗口

| 快捷键 | 作用 |
| --- | --- |
| `jk`（插入模式） | ⭐ 退出插入模式 |
| `Space w` | ⭐ 保存文件 |
| `Space q` | ⭐ 关闭当前窗口 |
| `Space +` | 增加数字 |
| `Space -` | 减少数字 |
| `Space sv` | ⭐ 垂直分割窗口 |
| `Space sh` | ⭐ 水平分割窗口 |
| `Space se` | 平均分配窗口大小 |
| `Space sx` | 关闭当前 split |
| `Space to` | 新建 tab |
| `Space tx` | 关闭当前 tab |
| `Space tn` | ⭐ 下一个 tab |
| `Space tp` | ⭐ 上一个 tab |
| `Space tf` | 在新 tab 打开当前文件 |
| `Space sm` | 最大化/恢复当前 split |
| `Space wr` | 恢复当前目录的 Neovim session |
| `Space ws` | 保存当前目录的 Neovim session |

可视模式下：

| 快捷键 | 作用 |
| --- | --- |
| `J` | 将选中行向下移动 |
| `K` | 将选中行向上移动 |

### 3.2 Alpha 启动页

启动页上的按钮也有快捷键：

| 快捷键 | 作用 |
| --- | --- |
| `e` | 新建文件 |
| `Space ee` | ⭐ 打开文件树 |
| `Space ff` | ⭐ 搜索文件 |
| `Space fs` | ⭐ 全文搜索 |
| `Space wr` | 恢复目录 session |
| `q` | 退出 Neovim |

### 3.3 Flash 快速跳转

| 快捷键 | 模式 | 作用 |
| --- | --- | --- |
| `s` | Normal/Visual/Operator-pending | 中文或英文快速跳转 |
| `S` | Normal/Visual/Operator-pending | Treesitter 结构快速跳转 |

按下 `s` 或 `S` 后，再按屏幕显示的标签即可跳转。

### 3.4 Surround 环绕操作

`nvim-surround` 使用默认按键：

| 快捷键 | 作用 |
| --- | --- |
| `ys{motion}{char}` | 用指定符号环绕 motion，例如 `ysiw)` |
| `yss{char}` | 环绕整行 |
| `ds{char}` | 删除周围的符号 |
| `cs{old}{new}` | 将旧符号替换成新符号 |
| `S{char}`（Visual） | 用指定符号环绕选中内容 |
| `C-g s`（Insert） | 在光标处插入一对符号 |

注意：Visual 模式的 `S` 同时被 Flash 配置使用；当前实际生效的映射可以用 `:verbose xmap S` 检查。

### 3.5 插入模式补全（nvim-cmp）

你的补全来源包括 LSP、LuaSnip、当前 buffer 和路径。补全菜单出现时：

| 快捷键 | 作用 |
| --- | --- |
| `Tab` | 选择下一项；如果有 snippet 则展开或跳到下一个占位符 |
| `Shift-Tab` | 选择上一项或跳到上一个占位符 |
| `C-j` / `C-k` | 下移/上移补全项 |
| `C-b` / `C-f` | 向上/向下滚动补全文档 |
| `C-Space` | 打开补全菜单 |
| `C-e` | 取消补全菜单 |
| `Enter` | 确认当前项目；不会强制选择未选中的项目 |

`nvim-autopairs` 会自动补全括号、引号等成对字符；`nvim-ts-autotag` 会在支持的文件类型中自动补全 HTML 标签。

### 3.6 Telescope 搜索

| 快捷键 | 作用 |
| --- | --- |
| `Space ff` | ⭐ 搜索文件 |
| `Space fr` | 最近打开的文件 |
| `Space fs` | ⭐ 全文搜索 |
| `Space fc` | 搜索光标下的单词 |
| `Space fb` | 搜索已打开的 buffer |
| `Space fk` | 查看 Neovim 快捷键 |

Telescope 搜索窗口中：

| 按键 | 作用 |
| --- | --- |
| `C-j` | 下一个结果 |
| `C-k` | 上一个结果 |
| `C-q` | 将结果发送到 quickfix 列表 |

### 3.7 文件树和 Git

| 快捷键 | 作用 |
| --- | --- |
| `Space ee` | ⭐ 打开/关闭文件树 |
| `Space ef` | 在文件树中定位当前文件 |
| `Space ec` | 折叠文件树目录 |
| `Space er` | 刷新文件树 |
| `Space lg` | ⭐ 打开 Lazygit |
| `]h` / `[h` | 下一个/上一个 Git hunk |
| `Space hs` | 暂存当前 hunk |
| `Space hr` | 重置当前 hunk |
| `Space hp` | 预览当前 hunk |
| `Space hb` | 查看当前行 blame |
| `Space hd` | 查看当前文件 diff |

文件树打开后，`nvim-tree` 还提供以下 buffer-local 默认按键：

| 按键 | 作用 |
| --- | --- |
| `<Enter>` / `o` | 打开文件或目录 |
| `<Tab>` | 预览文件 |
| `q` | 关闭文件树 |
| `a` | 新建文件或目录 |
| `r` / `e` / `u` | 重命名（完整路径/文件名/省略文件名） |
| `d` / `D` / `<Delete>` | 删除/移入回收站 |
| `c` / `x` / `p` | 复制/剪切/粘贴 |
| `y` / `Y` / `gy` / `ge` | 复制文件名/相对路径/绝对路径/基本名 |
| `m` | 切换书签 |
| `bd` / `bt` / `bmv` | 删除/回收/移动书签 |
| `-` / `P` | 转到父目录/选择父目录 |
| `<BS>` | 关闭当前目录 |
| `C-]` | 将当前节点设为根目录 |
| `C-e` / `C-t` / `C-v` / `C-x` | 原位打开/新 tab/垂直 split/水平 split |
| `C-k` | 显示节点信息 |
| `.` / `s` | 执行命令/用系统程序打开 |
| `O` / `L` | 无 window picker 打开/切换空目录组显示 |
| `f` / `F` / `S` | 开始过滤/清除过滤/搜索节点 |
| `H` / `I` / `B` / `M` / `U` / `C` | 显示隐藏文件/忽略文件/无 buffer/无书签/自定义/干净 Git 文件过滤 |
| `J` / `K` / `>` / `<` | 最后/第一个/下一个/上一个同级节点 |
| `E` / `W` | 展开全部/折叠全部 |
| `R` | 刷新文件树 |
| `g?` | 查看文件树帮助 |

### 3.8 格式化和 TODO

| 快捷键 | 作用 |
| --- | --- |
| `Space mp` | ⭐ 格式化当前文件或选中内容 |
| `]t` / `[t` | 下一个/上一个 TODO |
| `Space ft` | 搜索所有 TODO |

### 3.9 LSP、定义和诊断

这些快捷键只在对应的 LSP 已连接到当前 buffer 时生效。

| 快捷键 | 作用 |
| --- | --- |
| `gd` | ⭐ 跳到定义 |
| `gD` | 跳到声明 |
| `gR` | 查找引用 |
| `gi` | 查找实现 |
| `gt` | 跳到类型定义 |
| `K` | ⭐ 显示光标下的文档 |
| `Space ca` | 代码操作 |
| `Space rn` | 重命名符号 |
| `Space d` | 显示当前行诊断信息 |
| `[d` / `]d` | ⭐ 上一个/下一个诊断 |

在 `.tex` 文件中，VimTeX 也会使用 `K` 显示 LaTeX 宏/包文档；如果两者冲突，以当前 buffer 中实际显示的映射为准。

### 3.10 which-key 菜单

在普通模式按一下 `Space`，等待约 500ms，which-key 会显示当前可用的前缀和快捷键。当前配置登记的分组包括：

| 前缀 | 分组 |
| --- | --- |
| `Space c` | Code |
| `Space e` | Explorer |
| `Space f` | Find |
| `Space h` | Git hunk |
| `Space l` | Lazygit |
| `Space m` | Format |
| `Space o` | Obsidian |
| `Space r` | Refactor |
| `Space s` | Split |
| `Space t` | Tab |
| `Space w` | Write / Session |

## 4. Obsidian / Markdown 快捷键

这些快捷键主要在 Markdown 文件中启用。你的 vault 是：

```text
/home/zhu/knowledge/vault
```

### 4.1 Obsidian 笔记操作

| 快捷键 | 作用 |
| --- | --- |
| `Space on` | 新建笔记，默认进入 `00-inbox` |
| `Space ot` | 从模板新建笔记 |
| `Space oT` | 插入模板 |
| `Space os` | 搜索 Obsidian 笔记 |
| `Space oq` | 快速切换笔记 |
| `Space ob` | 查看 backlinks |
| `Space or` | 重命名当前笔记 |
| `Space od` | 打开今日笔记 |
| `Space of` | ⭐ 用 Telescope 搜索整个 vault 的 Markdown 笔记 |
| `:Vault` | 执行 vault 笔记搜索 |

### 4.2 插入图片

| 用法 | 作用 |
| --- | --- |
| `Space oi`（普通模式） | ⭐ 打开 vault 图片选择器并插入图片 |
| 插入模式输入 `img`，按 `Tab` | ⭐ 选择已有图片并插入 `![[图片路径]]` |
| 插入模式输入 `imgc`，按 `Tab` | ⭐ 选择图片并询问图注 |

图片选择器会搜索整个 vault 中的 `png`、`jpg`、`jpeg`、`webp`、`gif`、`svg`、`bmp`、`avif` 文件。

其他 Markdown snippets、图片模板和完整用法见：[[30-concepts/latex使用指南|Neovim + Obsidian Snippets 使用指南]]。

## 5. LaTeX / VimTeX 快捷键

在 `.tex` 文件中，VimTeX 的 `<localleader>` 也是空格：

| 快捷键 | 作用 |
| --- | --- |
| `Space ll` | ⭐ 编译 |
| `Space lv` | ⭐ 查看 PDF |
| `Space le` | ⭐ 打开错误列表 |
| `Space li` | 查看 VimTeX 信息 |
| `Space lI` | 查看完整信息 |
| `Space lq` | 查看编译日志 |
| `Space lo` | 查看编译输出 |
| `Space lk` | 停止编译 |
| `Space lK` | 停止全部编译 |
| `Space lc` | 清理辅助文件 |
| `Space lC` | 完整清理 |
| `Space lt` | 打开目录 |
| `Space lT` | 切换目录 |
| `Space lr` | 反向搜索（从 PDF 定位到源码） |
| `Space lL` | 编译选中的部分（Normal/Visual） |
| `Space lS` | 单次编译（single-shot compile） |
| `Space lg` | 查看 VimTeX 状态 |
| `Space lG` | 查看全部 VimTeX 状态 |
| `Space ls` | 切换主 tex 文件 |
| `Space lx` | 重新加载 VimTeX |
| `Space lX` | 重新加载 VimTeX 状态 |
| `Space lm` | 查看输入映射 |
| `Space la` | 打开 VimTeX 上下文菜单 |

常用 VimTeX 普通模式动作：

| 快捷键 | 作用 |
| --- | --- |
| `]]` / `[[` | ⭐ 下一个/上一个 section |
| `]m` / `[m` | ⭐ 下一个/上一个 environment |
| `]n` / `[n` | ⭐ 下一个/上一个数学环境 |
| `]r` / `[r` | 下一个/上一个 frame |
| `]/` / `[/` | 下一个/上一个 comment |
| `K` | ⭐ 查看当前 LaTeX 命令或包的文档 |
| `%` | ⭐ 跳到匹配的 LaTeX 环境/括号 |
| `tsc` | 切换命令的星号形式 |
| `tsf` | 切换分式形式 |
| `tsb` | 切换命令换行形式 |
| `tss` | 切换 environment 的星号形式 |
| `tse` | 切换 environment |
| `ts$` | 切换数学 environment |
| `tsd` / `tsD` | 正向/反向切换 `\left` 等定界符修饰 |
| `dsd` | 删除数学定界符 |
| `dse` | 删除 environment |
| `dsc` | 删除命令 |
| `ds$` | 删除数学 environment |
| `cse` | 修改 environment 类型 |
| `csc` | 修改 LaTeX 命令 |
| `cs$` | 修改数学 environment 类型 |
| `csd` | 修改数学定界符 |
| `F6` | 用 environment 环绕当前行/选中内容 |
| `F7` | 创建 LaTeX 命令 |
| `F8` | 给定界符添加 `\left`/`\right` 修饰 |

VimTeX 的 LaTeX 文本对象可以和操作符组合使用：

| 文本对象 | 对象 |
| --- | --- |
| `ac` / `ic` | 外部/内部 LaTeX command |
| `ad` / `id` | 外部/内部数学 delimiter |
| `ae` / `ie` | 外部/内部 environment |
| `a$` / `i$` | 外部/内部数学环境 |
| `aP` / `iP` | 外部/内部 section |
| `am` / `im` | 外部/内部 item |

例如 `vie` 选择当前 environment 内部，`vae` 选择整个 environment；`yie` 可以复制 environment 内容。

### 5.1 VimTeX 插入模式映射

VimTeX 还有一套默认的插入模式映射，前缀是反引号 `` ` ``，只在数学环境中生效。完整列表可以用 `Space lm` 或 `:VimtexImapsList` 查看。

常用映射：

| 输入 | 结果 |
| --- | --- |
| `` `a `` / `` `b `` / `` `g `` | `\alpha` / `\beta` / `\gamma` |
| `` `d `` / `` `e `` / `` `f `` | `\delta` / `\epsilon` / `\phi` |
| `` `l `` / `` `m `` / `` `n `` | `\lambda` / `\mu` / `\nu` |
| `` `p `` / `` `q `` / `` `r `` | `\pi` / `\theta` / `\rho` |
| `` `s `` / `` `t `` / `` `w `` | `\sigma` / `\tau` / `\omega` |
| `` `x `` / `` `y `` / `` `z `` | `\xi` / `\psi` / `\zeta` |
| `` `A `` / `` `B `` / `` `E `` | `\forall` / `\boldsymbol` / `\exists` |
| `` `N `` / `` `H `` | `\nabla` / `\hbar` |
| `` `D `` / `` `F `` / `` `G `` | `\Delta` / `\Phi` / `\Gamma` |
| `` `L `` / `` `P `` / `` `Q `` | `\Lambda` / `\Pi` / `\Theta` |
| `` `S `` / `` `U `` / `` `W `` / `` `X `` / `` `Y `` | `\Sigma` / `\Upsilon` / `\Omega` / `\Xi` / `\Psi` |
| `` `0 `` / `` `2 `` / `` `6 `` / `` `8 `` | `\emptyset` / `\sqrt` / `\partial` / `\infty` |
| `` `+ `` / <code>&#61;</code> / `` `. `` / `` `* `` | `\dagger` / `\equiv` / `\cdot` / `\times` |
| `` `< `` / `` `> `` | `\langle` / `\rangle` |
| `` `[ `` / `` `] `` | `\subseteq` / `\supseteq` |
| `` `( `` / `` `) `` | `\subset` / `\supset` |
| `` `jh `` / `` `jl `` | `\leftarrow` / `\rightarrow` |
| `` `jk `` / `` `jj `` | `\uparrow` / `\downarrow` |
| `` `jH `` / `` `jL `` | `\Leftarrow` / `\Rightarrow` |
| `` `jK `` / `` `jJ `` | `\Uparrow` / `\Downarrow` |
| `` `#b `` / `` `#c `` | `\mathbf{}` / `\mathcal{}` |
| `` `#f `` / `` `#B `` | `\mathfrak{}` / `\mathbb{}` |
| `` `#- `` / `` `#/ `` | `\overline{}` / `\slashed{}` |

插入模式下按 `F7` 可以创建命令；输入 `]]` 可以关闭数学定界符。VimTeX 的插入映射和 LuaSnip snippets 可以同时使用，但两者触发词不同。

LaTeX snippets 的触发词、Markdown 公式和 Obsidian 图片 snippets 见：[[30-concepts/latex使用指南|Snippets 使用指南]]。

## 6. 当前配置中的快捷键覆盖

有些快捷键在不同 buffer 或模式中有不同作用：

| 快捷键 | 普通情况 | 特殊情况 |
| --- | --- | --- |
| `Space lg` | 打开 Lazygit | `.tex` 中由 VimTeX 用作查看编译状态 |
| `K` | LSP hover 文档 | `.tex` 中由 VimTeX 用作查看 LaTeX 命令/包文档；文件树中是跳到第一个同级节点 |
| `S`（Visual） | nvim-surround 环绕选区 | Flash 也声明了 `S`；实际生效者用 `:verbose xmap S` 检查 |
| `C-k` / `C-j` | tmux/Neovim 窗格移动 | 补全或 Telescope 打开时用于选择候选项 |
| `Space l...` | which-key 显示前缀菜单 | `.tex` 中主要是 VimTeX 的 buffer-local 映射 |

查看映射时要注意模式：`nmap` 是普通模式，`imap` 是插入模式，`xmap` 是 Visual 模式，`tmap` 是终端模式；同一个键在不同模式下可以同时存在。

## 7. 快捷键查看和故障排查

### 7.1 Neovim

查看所有当前快捷键：

```vim
:Telescope keymaps
```

或者按：

```text
Space fk
```

查看某个快捷键由哪个文件设置：

```vim
:verbose nmap <Space>ff
:verbose nmap <C-h>
:verbose nmap <buffer> <Space>ll
```

查看当前文件类型：

```vim
:set ft?
```

### 7.2 tmux

查看当前 tmux 实际加载的所有按键：

```bash
tmux list-keys
```

查看当前配置文件：

```bash
tmux show-options -g
tmux show-window-options -g
```

重新加载配置：

```text
C-a r
```

如果重新加载后快捷键仍不生效，确认 TPM 已安装并检查：

```bash
ls ~/.tmux/plugins
```

## 8. Vim / Neovim 原生快捷键

下面是 Vim/Neovim 自带的核心操作，不依赖插件。除特别说明外，都是普通模式。

### 8.1 模式切换

| 按键 | 作用 |
| --- | --- |
| `Esc` | ⭐ 回到普通模式 |
| `i` / `I` | ⭐ 在光标前插入/行首插入 |
| `a` / `A` | ⭐ 在光标后插入/行尾插入 |
| `o` / `O` | ⭐ 下方/上方新开一行并插入 |
| `v` | ⭐ 字符可视模式 |
| `V` | ⭐ 行可视模式 |
| `C-v` | 块可视模式 |
| `R` | 替换模式 |
| `:` | ⭐ 打开 Ex 命令行 |
| `/` / `?` | ⭐ 向下/向上搜索 |
| `C-\\ C-n`（终端模式） | 从终端回到普通模式 |

### 8.2 光标移动

| 按键 | 作用 |
| --- | --- |
| `h` / `j` / `k` / `l` | ⭐ 左/下/上/右 |
| `w` / `W` | ⭐ 下一个单词/大 WORD |
| `b` / `B` | ⭐ 上一个单词/大 WORD |
| `e` / `E` | 单词末尾/大 WORD 末尾 |
| `0` | ⭐ 行首（绝对列 0） |
| `^` | ⭐ 行首第一个非空字符 |
| `$` | ⭐ 行尾 |
| `gg` / `G` | ⭐ 文件开头/文件末尾 |
| `{n}G` | 跳到第 n 行，例如 `20G` |
| `:{n}` | 跳到第 n 行，例如 `:20` |
| `C-d` / `C-u` | ⭐ 向下/向上半页 |
| `C-f` / `C-b` | ⭐ 向下/向上整页 |
| `C-e` / `C-y` | 向下/向上滚动一行 |
| `H` / `M` / `L` | 光标移到屏幕上/中/下部 |
| `f{char}` / `F{char}` | 向右/向左跳到本行字符 |
| `t{char}` / `T{char}` | 跳到字符前/后 |
| `;` / `,` | 重复/反向重复 `f`、`F`、`t`、`T` |
| `%` | 在括号、环境等匹配位置之间跳转 |

数字可以作为计数前缀，例如 `5j` 向下移动五行，`3dd` 删除三行，`2w` 跳过两个单词。

### 8.3 操作符和文本对象

Vim 的基本组合是：

```text
操作符 + motion/text-object
```

例如：`daw` 删除一个单词，`ciw` 修改当前单词，`yap` 复制当前段落。

常用操作符：

| 按键 | 作用 |
| --- | --- |
| `d` | ⭐ 删除 |
| `c` | ⭐ 删除并进入插入模式 |
| `y` | ⭐ 复制 |
| `>` / `<` | 增加/减少缩进 |
| <code>&#61;</code> | 自动缩进 |
| `gq` | 按文本宽度重新排版 |
| `gu` / `gU` | 转小写/转大写 |
| `g~` | 切换大小写 |

常用文本对象：

| 文本对象 | 作用 |
| --- | --- |
| `iw` / `aw` | ⭐ 单词内部/包含周围空格的单词 |
| `is` / `as` | 句子内部/完整句子 |
| `ip` / `ap` | 段落内部/完整段落 |
| `i"` / `a"` | 双引号内部/包含双引号 |
| `i'` / `a'` | 单引号内部/包含单引号 |
| `i(` / `a(` | 括号内部/包含括号 |
| `i[` / `a[` | 方括号内部/包含方括号 |
| `i{` / `a{` | 花括号内部/包含花括号 |
| `it` / `at` | HTML/XML 标签内部/包含标签 |
| `iB` / `aB` | 大括号块内部/包含大括号块 |

例子：

```text
ciw       修改当前单词
di"       删除双引号内部内容
da)       删除一对括号及其内容
yip       复制当前段落
>i}       增加花括号内部缩进
gg=G      自动格式化整个文件
```

### 8.4 删除、修改、复制和粘贴

| 按键 | 作用 |
| --- | --- |
| `x` / `X` | ⭐ 删除当前字符/光标前字符 |
| `dd` | ⭐ 删除整行 |
| `D` | ⭐ 删除到行尾 |
| `C` | ⭐ 修改到行尾 |
| `s` | 删除字符并进入插入模式 |
| `S` | 删除整行并进入插入模式 |
| `r{char}` | 替换一个字符 |
| `J` | 合并当前行和下一行 |
| `yy` | ⭐ 复制整行 |
| `y{motion}` | ⭐ 复制 motion 覆盖的内容 |
| `p` / `P` | ⭐ 在光标后/前粘贴 |
| `u` | ⭐ 撤销 |
| `C-r` | ⭐ 重做 |
| `.` | ⭐ 重复上一次修改 |
| `~` | 切换当前字符大小写 |
| `>>` / `<<` | 增加/减少当前行缩进 |

### 8.5 搜索和替换

| 按键/命令 | 作用 |
| --- | --- |
| `/pattern` | ⭐ 向下搜索 pattern |
| `?pattern` | ⭐ 向上搜索 pattern |
| `n` / `N` | ⭐ 下一个/上一个搜索结果 |
| `*` / `#` | 向下/向上搜索光标下的单词 |
| `g*` / `g#` | 搜索光标下单词，但不要求完整单词匹配 |
| `:noh` | 清除搜索高亮 |
| `:%s/old/new/g` | 全文件替换 |
| `:s/old/new/g` | 当前行替换 |
| `:'<,'>s/old/new/g` | Visual 选区替换 |
| `:vimgrep /pat/gj **/*` | 在文件中搜索并放入 quickfix |

替换命令中的常见标志：`g` 表示一行内全部替换，`c` 表示每次替换前询问，`i` 表示忽略大小写。例如：

```vim
:%s/foo/bar/gc
```

### 8.6 寄存器和系统剪贴板

| 按键/命令 | 作用 |
| --- | --- |
| `"ayy` | 将当前行复制到寄存器 `a` |
| `"ap` | 粘贴寄存器 `a` |
| `"+y` | 复制到系统剪贴板 |
| `"+p` | 从系统剪贴板粘贴 |
| `"_dd` | 删除但不写入寄存器 |
| `:registers` | 查看寄存器内容 |
| `"0p` | 粘贴最近一次复制的内容 |
| `"_d{motion}` | 删除到黑洞寄存器 |

你的配置把 `clipboard` 设置为 `unnamedplus`，所以普通的 `y` 和 `p` 通常也会与系统剪贴板同步。

### 8.7 宏、标记和跳转历史

| 按键/命令 | 作用 |
| --- | --- |
| `qa` | 开始录制宏到寄存器 `a` |
| `q` | 停止录制宏 |
| `@a` | 执行寄存器 `a` 中的宏 |
| `@@` | 重复执行上一次宏 |
| `5@a` | 执行宏 `a` 五次 |
| `ma` | 在当前位置设置标记 `a` |
| `` `a `` | 跳到标记 `a` 的精确位置 |
| `'a` | 跳到标记 `a` 所在行 |
| `''` | 回到上一次跳转前的行 |
| `C-o` / `C-i` | 跳转历史后退/前进 |
| `:marks` | 查看标记 |
| `:jumps` | 查看跳转历史 |

### 8.8 多窗口、buffer 和 Tab 的原生操作

你已经配置了 `Space s...` 和 `Space t...`，下面是对应的 Vim 原生方式：

| 按键/命令 | 作用 |
| --- | --- |
| `C-w h/j/k/l` | ⭐ 移到左/下/上/右侧窗口 |
| `C-w w` | ⭐ 循环切换窗口 |
| `C-w q` | ⭐ 关闭当前窗口 |
| `C-w o` | 只保留当前窗口 |
| `C-w` + <code>&#61;</code> | 平均窗口大小 |
| `C-w +/-` | 增大/减小高度 |
| `C-w >/<` | 增大/减小宽度 |
| `C-w T` | 将当前窗口移动到新 Tab |
| `:split` / `:vsplit` | ⭐ 水平/垂直分割 |
| `:enew` | ⭐ 新建空 buffer |
| `:edit {file}` | ⭐ 打开文件 |
| `:bnext` / `:bprevious` | 下一个/上一个 buffer |
| `:buffer {name}` | 切换到指定 buffer |
| `:bdelete` | 关闭当前 buffer |
| `gt` / `gT` | ⭐ 下一个/上一个 Tab |
| `:tabnew` | 新建 Tab |
| `:tabclose` | 关闭 Tab |
| `:tabmove {n}` | 移动当前 Tab |

### 8.9 折叠、缩进和显示

| 按键 | 作用 |
| --- | --- |
| `za` | 切换当前折叠 |
| `zo` / `zc` | 打开/关闭当前折叠 |
| `zR` / `zM` | 打开全部/关闭全部折叠 |
| `zf{motion}` | 手动创建折叠 |
| `zd` | 删除当前折叠 |
| `zE` | 删除当前窗口所有手动折叠 |
| <code>&#61;&#61;</code> | 自动缩进当前行 |
| <code>&#61;</code>{motion} | 自动缩进 motion 覆盖的内容 |
| `gg` + <code>&#61;</code> + `G` | 自动缩进整个文件 |
| `:set number?` | 查看行号设置 |
| `:set list?` | 查看不可见字符显示设置 |
| `:set wrap?` | 查看自动换行设置 |

你的配置对 Markdown 和 TeX 自动启用换行，对其他文件默认关闭换行。

### 8.10 文件和命令

| 命令 | 作用 |
| --- | --- |
| `:w` | ⭐ 保存 |
| `:wa` | ⭐ 保存全部 buffer |
| `:q` | ⭐ 退出当前窗口 |
| `:qa` | 退出全部窗口 |
| `:q!` | 放弃修改并退出 |
| `:wq` / `:x` | ⭐ 保存并退出 |
| `:waq` | 保存全部并退出 |
| `:source %` | 重新加载当前 Vim 配置文件 |
| `:set paste?` | 查看粘贴模式状态 |
| `:messages` | 查看消息日志 |
| `:checkhealth` | 检查 Neovim 环境 |
| `:Lazy` | 查看和管理 lazy.nvim 插件 |
| `:Mason` | 查看和管理 Mason 工具 |

### 8.11 Vim 帮助系统

Vim/Neovim 的帮助是最准确的内置参考：

```vim
:help normal-index
:help insert-index
:help visual-index
:help operator
:help motion.txt
:help text-objects
:help registers
:help recording
:help window
:help tabpage
```

查找某个快捷键的实际来源：

```vim
:verbose nmap <C-h>
:verbose imap <Tab>
:verbose xmap S
:verbose nmap <buffer> K
```

## 9. 配置文件位置

| 内容 | 文件 |
| --- | --- |
| tmux 主配置 | `~/.tmux.conf` |
| Neovim 总入口 | `~/.config/nvim/init.lua` |
| Neovim 基本快捷键 | `~/.config/nvim/lua/zhu/core/keymaps.lua` |
| LSP 快捷键 | `~/.config/nvim/lua/zhu/core/lsp.lua` |
| Telescope、Git、格式化、TODO | `~/.config/nvim/lua/zhu/plugins/editor.lua` |
| 文件树、which-key、session | `~/.config/nvim/lua/zhu/plugins/ui.lua` |
| Obsidian 快捷键 | `~/.config/nvim/lua/zhu/plugins/obsidian.lua` |
| Markdown 图片和 snippets | `~/.config/nvim/lua/zhu/markdown.lua` |
| LaTeX / VimTeX | `~/.config/nvim/lua/zhu/plugins/latex.lua` |
| Flash 跳转 | `~/.config/nvim/lua/zhu/plugins/flash.lua` |
