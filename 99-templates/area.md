---
type: area
homepage: true
icon: "🧭"
description:
order: 100
---

# {{title}}

[[Home|← 回到首页]]

## 最近笔记

```dataview
TABLE WITHOUT ID
  file.link AS 笔记,
  dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS 最近修改
FROM ""
WHERE startswith(file.folder, this.file.folder)
  AND file.path != this.file.path
  AND type != "area"
SORT file.mtime DESC
LIMIT 15
```

