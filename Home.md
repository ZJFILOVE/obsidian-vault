---
cssclasses:
  - knowledge-home
---

# 首页

> [!quote] 随手写，慢慢整理。

## 入口

- [[10-books/Library|个人图书馆]]
- [[99-templates/README|写作模板]]

## 正在阅读

```dataview
TABLE WITHOUT ID
  file.link AS 书名,
  author AS 作者
FROM "10-books"
WHERE type = "book" AND status = "reading"
SORT file.name ASC
```

## 最近修改

```dataview
TABLE WITHOUT ID
  file.link AS 笔记,
  dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS 修改时间
FROM ""
WHERE file.name != "Home" AND !startswith(file.folder, "99-templates")
SORT file.mtime DESC
LIMIT 8
```
