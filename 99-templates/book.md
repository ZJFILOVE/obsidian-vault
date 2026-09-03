---
title: "{{title}}"
type: book
author:
year:
status: reading
cover:
rating:
reviewed: false
created: "{{date}}"
tags:
  - book
---

# {{title}}

> [!info]
> **作者：** `author`  
> **状态：** `status`  
> **评分：** `rating`

## 📖 章节目录

```dataview
TABLE WITHOUT ID
  chapter AS 章节,
  file.link AS 笔记
FROM "10-books"
WHERE type = "chapter" AND book = this.file.name
SORT chapter ASC
```

> [!tip] 新建章节笔记时插入 `99-templates/chapter.md`，并把它的 `book` 属性填写为本文件名。之后这里会自动出现该章节。

## 摘录


## 阅读笔记


## 我的想法


## ✍️ 书评


## 延伸链接

