---
type: area
homepage: true
icon: "🌐"
description: "CET · Translation · Vocabulary · Reading"
order: 30
---
					
# 🌐 English

[[Home|← 回到首页]]

> [!quote] 英语训练入口。Daily、Vocabulary 和 Translation 仍然保持为普通 Markdown，主页只负责汇总。

## 最近训练

```dataview
TABLE WITHOUT ID
  file.link AS 笔记,
  choice(component, component, "note") AS 类型,
  dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS 最近修改
FROM "50-courses/English"
WHERE file.path != this.file.path
SORT file.mtime DESC
LIMIT 12
```

## Daily

```dataview
LIST WITHOUT ID file.link
FROM "50-courses/English/Daily"
SORT file.name DESC
LIMIT 10
```

## Translation

```dataview
LIST WITHOUT ID file.link
FROM "50-courses/English/Translation"
SORT file.name DESC
LIMIT 10
```

## Vocabulary

```dataview
LIST WITHOUT ID file.link
FROM "50-courses/English/Vocabulary"
SORT file.name DESC
LIMIT 10
```
