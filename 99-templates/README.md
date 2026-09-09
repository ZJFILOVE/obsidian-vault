# Templates

这套模板采用一个原则：**Obsidian 负责创建和组织，Neovim 负责高频写作；Templater 始终是文件创建引擎。**

自动化只处理机械动作：命名、日期、最少 frontmatter、必要的目录移动和父子关系。模板执行结束后得到普通 Markdown，之后可以完全在 Neovim 中继续写。

## 核心工作流

不强迫把每篇论文拆成大量 concept note。默认采用最直观的方式：

```text
论文 A → Resources/Papers/论文 A.md
论文 B → Resources/Papers/论文 B.md
论文 C → Resources/Papers/论文 C.md
```

每篇论文就是一个独立 Markdown 文件。什么时候需要建立 `[[WikiLink]]`、拆出 concept、写额外总结，由实际写作需要决定，而不是模板强制决定。

## Obsidian 端的日常入口

QuickAdd 推荐只暴露 4 个高频创建入口：

- `paper.md` — 一篇论文一个文件，自动放入 `Resources/Papers/`
- `note.md` — 普通知识笔记；可选择 `concept / idea / method / note`
- `chapter.md` — 书籍章节；选择母书、章节号并自动归档
- `writing.md` — 长文草稿；选择 `draft / essay / article`

`source.md` 继续保留给 `reference / video / web` 等一般来源；如果创建论文，日常优先直接使用 `paper.md`，少一次类型选择。

Daily Note 继续由 Obsidian Daily Notes / Calendar 创建，不经过 QuickAdd。

### `paper.md`

创建时只问论文标题，然后自动：

1. 清理文件名；
2. 创建 `Resources/Papers/`（如果不存在）；
3. 重命名并移动文件；
4. 写入最少 metadata；
5. 把光标交给正文。

最终文件只保留：

```yaml
---
type: paper
created: "YYYY-MM-DD"
---

# Paper title
```

不默认生成 Summary / Methods / Results / Questions，也不强制填写 authors / DOI / status 等字段。

### `note.md`

创建时选择：

```text
concept
idea
method
note
```

然后输入标题。`concept` 与 `method` 自动归入 `30-concepts/`；`idea` 与普通 `note` 保留在创建位置。

### `chapter.md`

章节是少数需要较重 Templater 自动化的模板：扫描 `type: book` 的书籍总页、选择母书、填写章节号、建立 WikiLink，并移动到：

```text
10-books/chapters/<书名>/
```

### `writing.md`

只创建 `draft / essay / article` 的最少 metadata 与标题，不预设 Introduction、Conclusion 或固定大纲。

## Daily

`daily.md` 保持极简，只负责日期、归档到 `60-daily/` 和正文入口。

## Insert templates = shared snippets

`insert-*` 不再包含 Templater 专属的 cursor 代码，而是纯 Markdown：

- `insert-figure.md`
- `insert-claim.md`
- `insert-question.md`

这样它们有两个用途：

```text
Obsidian
Templater: Insert template
        ↓
纯 Markdown snippet
        ↑
Neovim
:read 99-templates/insert-*.md
```

也就是说，这三份文件是两边共享的“结构定义”。以后 Neovim 的 LuaSnip 可以再做一层完全同构的快捷 snippet，为同一结构提供 tabstop；LuaSnip 只是编辑体验层，不应重新定义另一套 Markdown 结构。

例如 `insert-claim.md` 的真实内容就是：

```markdown
**Claim**

**Evidence**
```

因此即使不加载任何 Obsidian 插件，这个 snippet 仍然是合法 Markdown。

## QuickAdd 与 Templater 的分工

```text
QuickAdd
  ↓
选择“我要创建哪种文件”
  ↓
Templater
  ↓
命名 / metadata / 移动 / 建立关系
  ↓
普通 Markdown
  ↓
Neovim 为主进行正文写作
```

QuickAdd 只是启动菜单，不负责核心逻辑。真正的文件规则继续全部放在 `99-templates/` 的 Templater 模板里，因此不会出现 QuickAdd 和 Neovim 各维护一套创建规则的问题。

推荐菜单：

```text
New
├── Paper
├── Note
├── Chapter
└── Writing
```

如果偶尔需要一般来源，再额外保留：

```text
Source
```

Insert 不必加入高频 QuickAdd 菜单；在 Obsidian 中可直接使用 `Templater: Insert template`。主要写作迁移到 Neovim 后，这些结构会由 LuaSnip 提供更快的输入方式。

## Specialized templates

现有 `book.md`、`area.md`、`film.md`、`series.md`、`blog.md` 等继续保留。它们承担书籍 Hub、Area Hub、媒体数据库或 Jekyll 发布等特定功能，不属于日常核心入口。

## 最终职责边界

```text
Obsidian
├── QuickAdd：选择创建什么
├── Templater：真正创建文件
├── Calendar / Daily Notes：创建 Daily
├── Dataview / Backlinks：浏览与组织
└── Templater Insert：偶尔在 GUI 内插 snippet

Neovim
├── 打开已有 Markdown
├── 正文写作
├── 搜索与跳转
└── LuaSnip：高频 snippet

Git
└── 同步同一套普通 Markdown
```

因此 Neovim 不需要复制 Templater 的“创建文件”职责，Obsidian 也不需要承担主要正文编辑。两边只在 snippet 层共享同一套 Markdown 结构。
