---
type: area
homepage: true
icon: "🌐"
description: "CET · Translation · Vocabulary · Reading"
order: 30
cssclasses:
  - hub-page
  - hub-english
---

# English

> [!hub-hero]
> **CET · Translation · Vocabulary · Reading**
> Daily、Vocabulary、Translation 和 Weekly 继续保持普通 Markdown；主页只负责把训练材料组织成一个清晰、稳定的入口。
>
> [[Home|Home]] · [[#Recent Training|Recent]] · [[#Daily|Daily]] · [[#Translation|Translation]] · [[#Vocabulary|Vocabulary]]

> [!hub-metrics]
> ```dataview
> TABLE WITHOUT ID
>   length(filter(rows, (r) => contains(r.file.folder, "Daily"))) AS "Daily",
>   length(filter(rows, (r) => contains(r.file.folder, "Translation"))) AS "Translation",
>   length(filter(rows, (r) => contains(r.file.folder, "Vocabulary"))) AS "Vocabulary",
>   length(filter(rows, (r) => r.file.mtime >= (date(today) - dur(7 days)))) AS "7 Days"
> FROM "50-courses/English"
> WHERE file.path != this.file.path AND file.extension = "md"
> GROUP BY true
> ```

## Recent Training

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Note,
>   choice(component, component, choice(contains(file.folder, "Translation"), "translation", choice(contains(file.folder, "Vocabulary"), "vocabulary", "daily"))) AS Type,
>   dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS Updated
> FROM "50-courses/English"
> WHERE file.path != this.file.path
> SORT file.mtime DESC
> LIMIT 12
> ```

## Daily

```dataview
LIST WITHOUT ID file.link
FROM "50-courses/English/Daily"
SORT file.name DESC
LIMIT 12
```

## Translation

```dataview
LIST WITHOUT ID file.link
FROM "50-courses/English/Translation"
SORT file.name DESC
LIMIT 12
```

## Vocabulary

```dataview
LIST WITHOUT ID file.link
FROM "50-courses/English/Vocabulary"
SORT file.name DESC
LIMIT 12
```

## Weekly

```dataview
LIST WITHOUT ID file.link
FROM "50-courses/English/Weekly"
SORT file.name DESC
LIMIT 8
```
