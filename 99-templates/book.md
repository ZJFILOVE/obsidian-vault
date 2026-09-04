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

## 📖 章节目录

```dataview
TABLE WITHOUT ID
  chapter AS 章节,
  file.link AS 笔记
FROM "10-books"
WHERE type = "chapter" AND book = this.file.name
SORT chapter ASC
```

