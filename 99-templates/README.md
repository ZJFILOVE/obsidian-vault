# Templates

模板保持为普通 Markdown，Obsidian 和 Neovim 都可以直接编辑。

## 当前模板

- `daily.md`：日记；Obsidian 会自动放进 `60-daily/`
- `book.md`：书籍总页；包含自动章节目录与书评区
- `chapter.md`：书籍章节笔记；通过 `book` + `chapter` 属性归入母书
- `film.md`：电影总页 / 影评
- `paper.md`：论文笔记
- `blog.md`：博客草稿

## 图书馆工作流

1. 新建一本书并插入 `book.md`。
2. 每个章节单独新建 Markdown，插入 `chapter.md`。
3. 在章节 frontmatter 中将 `book` 填为书籍总页的文件名，将 `chapter` 填为章节序号。
4. 回到书籍总页，Dataview 会自动生成章节子菜单。
5. `Home.md` 与 `10-books/Library.md` 会自动收集 `type: book` 和 `type: film` 的作品。

在 Obsidian 中使用 `Templates: Insert template` 插入。用 Neovim 编辑时，这些文件仍然只是普通 Markdown，后续也可以绑定 snippets。
