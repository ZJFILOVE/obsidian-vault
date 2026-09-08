---
type: area
homepage: true
icon: "🧭"
description:
order: 100
cssclasses:
  - hub-page
---

# {{title}}

> [!hub-hero]
> **Area overview**
> 这个页面只负责聚合与导航；具体内容仍然保存在各自的普通 Markdown 笔记中。
>
> [[Home|Home]]

## Recently Active

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Note,
>   choice(type, type, "note") AS Type,
>   dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS Updated
> FROM ""
> WHERE startswith(file.folder, this.file.folder)
>   AND file.path != this.file.path
>   AND type != "area"
> SORT file.mtime DESC
> LIMIT 15
> ```
