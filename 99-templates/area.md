---
type: area
homepage: true
icon: "🧭"
description:
order: 100
---

# {{title}}

[[Home|← 回到首页]]

> [!info] 主页领域入口
> 这个文件只要保留 `type: area` 和 `homepage: true`，就会自动出现在 `Home.md` 的 Areas 区域。用 `order` 控制排序；设为 `homepage: false` 即可从主页隐藏。

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
