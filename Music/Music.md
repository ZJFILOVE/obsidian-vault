---
type: area
homepage: true
icon: "🎧"
description: "Daily 5 · 音乐赏析 · Apple Music"
order: 20
cssclasses:
  - music-hub
---

# 🎧 Music

[[Home|← 回到首页]]

> [!quote] 每日音乐推荐与赏析入口。Daily 继续按日期保存，这里只负责聚合与导航。

## 🎵 最新一期

```dataview
TABLE WITHOUT ID
  file.link AS 日刊,
  provider AS 平台,
  date AS 日期
FROM "Music/Daily"
WHERE type = "music-daily"
SORT date DESC
LIMIT 1
```

## 🗓️ 最近的 Daily 5

```dataview
TABLE WITHOUT ID
  file.link AS 日刊,
  date AS 日期,
  provider AS 平台
FROM "Music/Daily"
WHERE type = "music-daily"
SORT date DESC
LIMIT 14
```

## 🔎 全部音乐笔记

```dataview
LIST WITHOUT ID file.link
FROM "Music"
WHERE file.path != this.file.path
  AND endswith(file.name, ".md") = false
SORT file.mtime DESC
LIMIT 30
```

> [!tip] 使用方式
> 从 Home 的 **Areas** 点击整张 Music 卡片进入这里，再从这里进入每天的 `Daily 5`。以后新的每日推荐只要继续写入 `Music/Daily/`，这个看板会自动更新。
