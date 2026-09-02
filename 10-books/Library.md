---
cssclasses:
  - cards
  - cards-cover
  - cards-2-3
  - cards-cols-4
---

# 个人图书馆

回到 [[Home|首页]]。

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

书籍笔记中的 `cover` 可以填写 Vault 内部图片链接，例如：

`cover: "[[90-assets/covers/book.jpg]]"`
