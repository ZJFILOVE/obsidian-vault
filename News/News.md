---
type: area
homepage: true
icon: "📰"
description: "长期影响新闻：只保留值得未来数月到数年继续关注的事件"
order: 70
cssclasses:
  - hub-page
  - hub-news
---

# News

> [!hub-hero]
> **Long-horizon signal, not a breaking-news feed.**
> 每天只保留少量具有结构性、长期性、可持续跟踪价值的事件；宁缺毋滥。视觉上与其他主页保持同一套编辑式层级，但用暖色强调资讯与判断。
>
> [[Home|Home]] · [[#Latest|Latest]] · [[#Daily Archive|Archive]] · [[#Coverage|Coverage]]

> [!hub-metrics]
> ```dataview
> TABLE WITHOUT ID
>   length(rows) AS "Daily Notes",
>   length(filter(rows, (r) => r.importance)) AS "Rated",
>   length(filter(rows, (r) => r.file.mtime >= (date(today) - dur(7 days)))) AS "7 Days",
>   length(filter(rows, (r) => r.file.mtime >= (date(today) - dur(30 days)))) AS "30 Days"
> FROM "News/Daily"
> WHERE type = "daily-news"
> GROUP BY true
> ```

## Latest

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Date,
>   importance AS Importance,
>   topics AS Topics,
>   dateformat(file.mtime, "MM-dd HH:mm") AS Updated
> FROM "News/Daily"
> WHERE type = "daily-news"
> SORT date DESC
> LIMIT 14
> ```

## Daily Archive

```dataview
LIST WITHOUT ID file.link
FROM "News/Daily"
WHERE type = "daily-news"
SORT date DESC
```

## Coverage

> [!hub-grid]
> ```dataview
> TABLE WITHOUT ID
>   "◆" AS "",
>   topic AS "",
>   scope AS ""
> FROM "News"
> WHERE false
> ```

- **Geopolitics & institutions** — 地缘政治、制度变化与关键政策
- **Macro & industry** — 宏观经济、金融与产业结构
- **AI & compute** — AI、半导体、计算基础设施
- **Science & health** — 科学、生命科学、医药与重大技术突破
- **Energy & climate** — 能源、气候与资源
- **China & global policy** — 中国及全球关键政策变化

> [!hub-hero]
> **Editorial rule**
> 每日笔记中的自动生成部分由 ChatGPT 更新；自动区之外可以自由加入自己的判断、链接和后续追踪，不会被后续推送覆盖。
