---
cssclasses:
  - library-hub
  - cards
  - cards-cover
  - cards-2-3
  - cards-cols-4
---

# 📚 个人图书馆

[[Home|← 回到首页]]

> [!quote] 这里既放书，也放电影。每一本书/每一部电影都是自己的入口页。

## 📖 书籍

```dataview
TABLE WITHOUT ID
  choice(cover, embed(cover), "") AS 封面,
  file.link AS 书名,
  author AS 作者,
  status AS 状态,
  rating AS 评分
FROM "10-books"
WHERE type = "book"
SORT status ASC, file.name ASC
```

## 🎬 电影

```dataview
TABLE WITHOUT ID
  choice(cover, embed(cover), "") AS 海报,
  file.link AS 片名,
  director AS 导演,
  status AS 状态,
  rating AS 评分
FROM "10-books"
WHERE type = "film"
SORT status ASC, file.name ASC
```

## 📚 正在阅读

```dataview
LIST WITHOUT ID file.link
FROM "10-books"
WHERE type = "book" AND status = "reading"
SORT file.name ASC
```

## 🎞️ 最近写过的书评 / 影评

```dataview
TABLE WITHOUT ID
  file.link AS 作品,
  choice(type = "book", "📖 书", "🎬 电影") AS 类型,
  rating AS 评分,
  dateformat(file.mtime, "yyyy-MM-dd") AS 最近修改
FROM "10-books"
WHERE type = "book" OR type = "film"
SORT file.mtime DESC
LIMIT 12
```

## 使用方式

- 新建一本书：插入 `99-templates/book.md`。
- 新建章节笔记：插入 `99-templates/chapter.md`，并把 `book` 属性填写为对应书籍总页的文件名。
- 新建电影笔记：插入 `99-templates/film.md`。
- 书籍总页的“章节目录”会自动收集属于这本书的章节笔记，因此从首页点击书名后，可以继续进入章节子菜单。
- `cover` 可填写 Vault 内部图片链接，例如 `"[[90-assets/covers/book.jpg]]"`。
