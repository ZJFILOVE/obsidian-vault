# Templates

这套模板采用一个原则：**自动化应该减少重复操作，而不是替你规定思考方式。**

因此模板分成两层：

- **自动化层可以很重**：负责命名、日期、frontmatter、目录、父子关系、移动文件。
- **写作层保持很轻**：真正开始写正文时，尽量只留下标题、必要导航和光标。

生成后的文件仍然是普通 Markdown，Obsidian 与 Neovim 都可以直接编辑；Templater 只负责“创建时”执行一次。

## 依赖

这些模板使用社区插件 **Templater**，核心语法是 `<%* ... %>`。

推荐入口：

`Command Palette → Templater: Create new note from template`

模板目录仍为：

```text
99-templates/
```

如果使用 Obsidian 核心 Daily Notes 创建日记，需要让 Templater 在新文件创建后执行模板；当前 Daily Notes 已经配置为：

```text
folder: 60-daily
template: 99-templates/daily
```

## 当前自动模板

| 模板 | 自动行为 | 最终位置 | 正文策略 |
| --- | --- | --- | --- |
| `book.md` | 获取书名、命名、生成书籍 metadata | `10-books/` | 只保留动态章节目录 |
| `chapter.md` | 扫描 `type: book`、选择母书、询问章节号、建立 WikiLink、自动建目录 | `10-books/chapters/<书名>/` | 只保留母书导航 + 空白正文 |
| `film.md` | 获取片名、命名、归档 | `10-books/movies/` | 空白正文 |
| `series.md` | 获取剧名、命名、归档 | `10-books/movies/` | 空白正文 |
| `concept.md` | 获取概念名、命名、日期 | `30-concepts/` | 空白正文 |
| `paper.md` | 获取论文标题、命名、日期、自动建目录 | `Resources/Papers/` | 空白正文 |
| `reference.md` | 获取资料标题、命名、日期、自动建目录 | `Resources/Reference/` | 空白正文 |
| `daily.md` | 使用当天日期、命名、归档 | `60-daily/` | 空白正文 |
| `area.md` | 获取 Area 名称和目标目录、生成主页 metadata 与最近活动查询 | 用户选择 | 保留导航功能，不规定内容结构 |
| `blog.md` | 获取标题、自动日期 | 保持创建位置 | 空白正文；原博客 YAML schema 不变 |

## 为什么不再使用复杂正文骨架

普通写作笔记不再默认生成：

```text
## 要点
## 正文
## 总结
## 问题
```

这类标题看似帮助写作，实际上会提前假定你的思考结构。数学章节、论文阅读、科研想法和随笔的自然结构并不相同，因此创建后直接把光标交给你。

需要结构时，在写作过程中自然创建标题即可。

## 导航型页面例外

`book.md` 和 `area.md` 不是普通正文笔记，而是 Hub，因此会保留功能性内容：

- Book 自动查询所属 Chapter。
- Area 自动查询同目录最近修改的笔记。

这些结构负责“找到内容”，而不是告诉你“怎样写内容”。

## Book → Chapter

`chapter.md` 已经包含原 `chapter-auto.md` 的全部自动逻辑，因此不再维护手动版和自动版两套 Chapter 模板。

创建 Chapter 时：

1. 自动扫描整个 Vault 中所有 `type: book` 的文件；
2. 选择母书；
3. 可填写章节编号；
4. 输入章节标题；
5. 自动移动到 `10-books/chapters/<书名>/`；
6. 自动写入：

```yaml
type: chapter
book: "[[10-books/母书]]"
chapter: "..."
```

书籍主页的 Dataview 会自动把它收进章节目录。

## Concepts

`30-concepts/` 现在有独立的 `concept.md` 自动模板。

Concept 不预设 Definition / Example / Feynman / Questions 等栏目。一个概念需要什么结构，由概念本身决定。

## Papers / References

论文与一般资料都归入现有的 `Resources/` 体系：

```text
Resources/
├── Papers/
├── Reference/
├── Reddit/
└── YouTube/
```

`Papers/` 和 `Reference/` 不存在时，模板首次使用会自动创建。

## Blog

博客模板继续使用原来的 Jekyll YAML 字段和默认配置：

- `layout: post`
- `author: "ZJF"`
- Webb Deep Field header image
- `catalog: true`
- `tags: 随笔`

自动化只负责把标题和日期填进去，不改变博客 metadata schema。

## Neovim

模板文件本身包含 JavaScript，但模板运行后生成的是普通 Markdown。因此日常编辑无需 Templater，也不会把 Obsidian 专用脚本散落到实际笔记中。

整体工作流是：

```text
Templater
   ↓
创建 / 命名 / 归档 / 建立关系
   ↓
普通 Markdown
   ↓
Obsidian 或 Neovim 自由写作
```

以后如果需要更快的入口，可以在这套模板之上增加 QuickAdd 或 Meta Bind；它们只应作为“启动按钮”，不需要改变模板和 Markdown 数据结构。
