# Obsidian writing workflow

原则：**Obsidian 负责创建和组织，Templater 负责文件创建逻辑，Neovim 负责主要正文写作。**

## 创建笔记

按 `Alt+N` 打开 QuickAdd。QuickAdd 只做启动菜单，当前提供：

```text
Paper
Note
Chapter
Writing
```

四个入口都调用 Templater 的 Create command，因此命名、frontmatter、移动路径和书籍关系仍只维护在 `99-templates/` 中。

- `paper.md` → `Resources/Papers/`
- `note.md` → `concept / idea / method / note`；`concept` 与 `method` → `30-concepts/`
- `chapter.md` → `10-books/chapters/<book>/`
- `writing.md` → `draft / essay / article`

论文默认一篇论文一个 Markdown 文件，不强制拆成 concept note。

## 插入小结构

Obsidian 中按 `Alt+E` 打开 Templater Insert template modal。

- `insert-figure.md`：询问图片文件名或 Vault 路径；图注可留空；不会自动创建 `### Figure` 标题
- `insert-claim.md`：Claim / Evidence，使用 Templater cursor locations
- `insert-question.md`：question callout

Templater 已开启 automatic jump to cursor。以后 Neovim 的 LuaSnip 使用相同的输出结构，但交互由 LuaSnip 的 tabstop 完成；不复制文件创建逻辑。

## 文件格式

模板运行结束后都是普通 Markdown。例如论文：

```markdown
---
type: paper
created: "YYYY-MM-DD"
---

# Paper title
```

正文不预设 Summary / Methods / Results / Questions 等固定栏目。

## 其他

Daily Note 仍使用 `60-daily/`。`book.md`、`area.md`、`film.md`、`series.md`、`blog.md` 等保留为专用模板。

当前继续使用 `Resources/`，暂不改名，以免先打断现有 YouTube / Reddit 自动推送路径；若以后统一为编号目录，需要连同自动任务一起迁移。
