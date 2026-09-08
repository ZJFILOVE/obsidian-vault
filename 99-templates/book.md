---
title: "{{title}}"
type: book
author:
year:
publisher:
pages:
status: reading
read: false
cover:
image:
rating:
personalRating:
onlineRating:
isbn:
isbn13:
dataSource: local
url:
id:
douban_url:
douban_rating:
reviewed: false
tags:
  - book
---

# {{title}}

## 📖 章节目录

```dataview
TABLE WITHOUT ID
  chapter AS 章节,
  file.link AS 笔记
FROM "10-books"
WHERE type = "chapter" AND book = this.file.name
SORT chapter ASC
```

## 阅读笔记
