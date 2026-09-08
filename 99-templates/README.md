# Templates

模板保持为普通 Markdown，Obsidian 和 Neovim 都可以直接编辑。

## 当前模板

- `daily.md`：日记；Obsidian 会自动放进 `60-daily/`
- `book.md`：书籍总页；包含自动章节目录与书评区
- `chapter.md`：基础章节模板；手工填写 `book` + `chapter` 后自动归入母书
- `chapter-auto.md`：Templater 版章节模板；创建时选择母书和章节号，自动建立双向关联并移动到对应章节目录
- `film.md`：电影总页 / 影评
- `area.md`：主页领域入口；用于 Research、Programming、Chemistry 等新板块
- `paper.md`：论文笔记
- `blog.md`：博客草稿

## 动态主页工作流

主页不再把 English、Research、Programming 等入口写死。每个领域只需要有一张 `type: area` 的入口笔记，例如：

```yaml
---
type: area
homepage: true
icon: "🧪"
description: "科研、文献与实验笔记"
order: 20
---
```

满足 `type: area` 且 `homepage: true` 的笔记会自动出现在 `Home.md` 的 Areas 卡片区。

- `icon`：主页卡片图标
- `description`：卡片简介
- `order`：数值越小越靠前
- `homepage: false`：保留领域入口页，但不显示在主页

建议把领域入口笔记放在它管理的目录根部，例如：

```text
20-research/Research.md
40-programming/Programming.md
50-courses/English/English.md
```

插入 `area.md` 后，其“最近笔记”查询会自动收集该入口文件所在目录下的内容。

## 图书馆工作流

书籍和章节的关系统一通过章节 frontmatter 中的 `book` 字段建立。推荐把它写成指向书籍总页的 WikiLink：

```yaml
---
type: chapter
book: "[[10-books/微观化学反应]]"
chapter: "1"
---
```

书籍总页会自动查询：

```dataview
WHERE type = "chapter"
  AND (book = this.file.link OR book = this.file.name)
```

因此章节文件放在 `10-books/` 下哪个子目录都可以，只要 `book` 指向正确母书，它就会自动出现在母书的章节目录中。

### 方式 A：不安装额外插件

1. 新建章节 Markdown。
2. 使用 `Templates: Insert template` 插入 `chapter.md`。
3. 把 `book` 填成 `[[10-books/微观化学反应]]` 这类母书链接。
4. 填写 `chapter` 序号。
5. 回到母书页面，Dataview 会自动显示该章节。

### 方式 B：全自动，推荐

安装社区插件 **Templater**，然后使用 `chapter-auto.md`。

运行 `Templater: Create new note from template` → 选择 `chapter-auto.md` 后，模板会：

1. 自动扫描所有 `type: book` 的书籍总页；
2. 弹出列表让你选择母书；
3. 询问章节编号；
4. 自动写入 `book: "[[母书]]"`；
5. 自动添加 `type: chapter` 和 `chapter-note` 样式；
6. 自动把文件移动到 `10-books/chapters/<书名>/`；
7. 母书的 Dataview 章节目录立即出现这篇笔记。

例如你选择《微观化学反应》、章节号 `1`，生成后的关键字段会类似：

```yaml
type: chapter
book: "[[10-books/微观化学反应]]"
chapter: "1"
```

这就是章节和母书的正式关联，不需要再维护手工目录链接。

在 Obsidian 中基础模板继续使用 `Templates: Insert template`。自动章节模板需要 Templater。用 Neovim 编辑时，这些文件仍然只是普通 Markdown。
