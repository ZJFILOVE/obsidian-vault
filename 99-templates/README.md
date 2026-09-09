# Templates

这套模板采用一个原则：**自动化负责机械动作，写作本身保持极简。**

Templater 只在创建瞬间负责：命名、日期、最少 frontmatter、必要的目录移动和父子关系。模板执行结束后，得到的仍然是普通 Markdown，Obsidian 与 Neovim 都可以直接编辑。

## 日常核心入口

QuickAdd 日常只需要暴露 4 个创建入口：

- `note.md` — 通用知识笔记；选择 `concept / idea / method / note`
- `source.md` — 来源笔记；选择 `paper / reference / video / web`
- `chapter.md` — 书籍章节；选择母书、章节号并自动归档
- `writing.md` — 长文草稿；选择 `draft / essay / article`

Daily Note 继续由 Obsidian Daily Notes / Calendar 创建，不经过 QuickAdd。

### `note.md`

创建时只问类型和标题。生成结果只有：

```yaml
---
type: concept
created: "YYYY-MM-DD"
---
```

然后是标题和正文光标。`concept` 与 `method` 自动归入 `30-concepts/`；`idea` 和普通 `note` 保留在创建位置。

### `source.md`

只问来源类型和标题，并自动归档：

```text
paper      → Resources/Papers/
reference  → Resources/Reference/
video      → Resources/YouTube/
web        → Resources/Reference/
```

不会预生成 Summary / Methods / Results / Questions 等写作栏目。

### `chapter.md`

章节是少数需要较重创建自动化的模板。它会扫描 `type: book` 的书籍总页，让你选择母书、填写章节编号，然后移动到：

```text
10-books/chapters/<书名>/
```

并建立 `book` WikiLink。

### `writing.md`

只创建 `draft / essay / article` 的最少 metadata 与标题，不预设 Introduction、Conclusion 或固定大纲。

## Daily

`daily.md` 保持极简，只负责日期、归档到 `60-daily/` 和正文入口。

## Insert templates

写作结构不放进每篇笔记，而是在真正需要时插入：

- `insert-figure.md` — Figure 标题 + 图片位置
- `insert-claim.md` — Claim / Evidence
- `insert-question.md` — 一个 question callout

这样普通笔记保持空白，需要结构时再按需增加。

## Specialized templates

现有 `book.md`、`area.md`、`film.md`、`series.md`、`blog.md` 等继续保留。它们承担书籍 Hub、Area Hub、媒体数据库或 Jekyll 发布等特定功能，不属于日常 QuickAdd 核心入口。

现有 `concept.md`、`paper.md`、`reference.md` 也暂时保留作兼容入口；日常使用可以逐渐切换到 `note.md` 与 `source.md`，确认工作流稳定后再决定是否删除旧入口。

## QuickAdd 与 Templater 的分工

```text
QuickAdd
  ↓
选择“我要创建什么”
  ↓
Templater
  ↓
命名 / metadata / 移动 / 建立关系
  ↓
普通 Markdown
  ↓
Obsidian / Neovim 自由写作
```

QuickAdd 不负责维护复杂数据结构，它只作为统一启动菜单；真正的模板逻辑仍放在 `99-templates/` 中。

## 推荐 QuickAdd 菜单

```text
New
├── Note
├── Source
├── Chapter
└── Writing

Insert
├── Figure
├── Claim
└── Question
```

Daily Note 继续使用 Calendar / Daily Notes，因此不需要再增加一个 QuickAdd 入口。

## Neovim

模板源码包含 Templater JavaScript，但运行后生成的是普通 Markdown。因此日常编辑不依赖 Templater，也不会把模板脚本带进实际笔记。
