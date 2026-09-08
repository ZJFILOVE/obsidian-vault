---
type: area
homepage: true
icon: "🎧"
description: "Daily 5 · 音乐赏析 · Apple Music"
order: 20
cssclasses:
  - hub-page
  - hub-music
---

# Music

> [!hub-hero]
> **Daily listening, kept as an archive rather than a feed.**
> 每日推荐仍按日期保存；这里负责给 Daily 5、赏析和 Apple Music 入口提供统一的总览。
>
> [[Home|Home]] · [[#Latest|Latest]] · [[#Daily Archive|Archive]]

> [!hub-metrics]
> ```dataview
> TABLE WITHOUT ID
>   length(rows) AS "Daily Notes",
>   length(filter(rows, (r) => r.provider)) AS "With Provider",
>   length(filter(rows, (r) => r.file.mtime >= (date(today) - dur(7 days)))) AS "7 Days",
>   length(filter(rows, (r) => r.file.mtime >= (date(today) - dur(30 days)))) AS "30 Days"
> FROM "Music/Daily"
> WHERE file.extension = "md"
> GROUP BY true
> ```

## Latest

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Edition,
>   provider AS Provider,
>   date AS Date,
>   dateformat(file.mtime, "MM-dd HH:mm") AS Updated
> FROM "Music/Daily"
> WHERE type = "music-daily"
> SORT date DESC
> LIMIT 5
> ```

## Daily Archive

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Edition,
>   date AS Date,
>   provider AS Provider
> FROM "Music/Daily"
> WHERE type = "music-daily"
> SORT date DESC
> LIMIT 20
> ```

## Recently Edited

```dataview
LIST WITHOUT ID file.link
FROM "Music"
WHERE file.path != this.file.path AND file.extension = "md"
SORT file.mtime DESC
LIMIT 20
```

> [!hub-hero]
> **Workflow**
> 新的 Daily 继续写进 `Music/Daily/` 即可；这个主页不保存重复信息，只自动聚合已有内容。
