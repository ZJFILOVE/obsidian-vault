---
type: area
homepage: true
icon: "📚"
description: "书籍、电影、电视剧与章节笔记"
order: 10
cssclasses:
  - library-hub
  - cards
  - cards-cover
  - cards-2-3
  - cards-cols-4
---

# 📚 个人媒体库

[[Home|← 回到首页]] · [[10-books/Media Library 使用说明|数据库检索与导入说明]]

> [!quote] 图书、电影和电视剧统一进入这里。既兼容手工条目，也兼容 Media DB 从 Open Library / TMDB 等数据库导入的元数据。

## 📖 书籍

```dataview
TABLE WITHOUT ID
  choice(cover, embed(cover), choice(image, embed(image), "")) AS 封面,
  file.link AS 书名,
  author AS 作者,
  year AS 年份,
  choice(status, status, choice(read, "已读", "未读")) AS 状态,
  choice(personalRating, personalRating, rating) AS 我的评分,
  onlineRating AS 数据库评分
FROM "10-books"
WHERE type = "book"
SORT status ASC, file.name ASC
```

## 🎬 电影

```dataview
TABLE WITHOUT ID
  choice(cover, embed(cover), choice(image, embed(image), "")) AS 海报,
  file.link AS 片名,
  director AS 导演,
  year AS 年份,
  choice(status, status, choice(watched, "已看", "未看")) AS 状态,
  choice(personalRating, personalRating, rating) AS 我的评分,
  onlineRating AS 数据库评分
FROM "10-books"
WHERE type = "movie" OR type = "film"
SORT status ASC, file.name ASC
```

## 📺 电视剧

```dataview
TABLE WITHOUT ID
  choice(cover, embed(cover), choice(image, embed(image), "")) AS 海报,
  file.link AS 剧名,
  year AS 年份,
  genres AS 类型,
  choice(status, status, choice(watched, "已看", "未看")) AS 状态,
  choice(personalRating, personalRating, rating) AS 我的评分,
  onlineRating AS 数据库评分
FROM "10-books"
WHERE type = "series"
SORT status ASC, file.name ASC
```

## 📚 正在阅读

```dataview
LIST WITHOUT ID file.link
FROM "10-books"
WHERE type = "book" AND status = "reading"
SORT file.name ASC
```

## ▶️ 正在观看

```dataview
LIST WITHOUT ID file.link
FROM "10-books"
WHERE (type = "movie" OR type = "film" OR type = "series") AND status = "watching"
SORT file.name ASC
```

## 🕘 最近更新

```dataview
TABLE WITHOUT ID
  file.link AS 作品,
  choice(type = "book", "📖 书", choice(type = "series", "📺 剧", "🎬 电影")) AS 类型,
  choice(personalRating, personalRating, rating) AS 我的评分,
  dataSource AS 数据源,
  dateformat(file.mtime, "yyyy-MM-dd") AS 最近修改
FROM "10-books"
WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
SORT file.mtime DESC
LIMIT 12
```

## 🔎 数据库检索

- 推荐安装社区插件 **Media DB**；仓库已预置目录设置。
- 图书默认从 **Open Library** 检索，不需要 API key。
- 电影 / 电视剧推荐用 **TMDB**；在 Media DB 设置中填入本机 Secret Storage 的 API Read Access Token。
- 豆瓣保留 `douban_url` / `douban_rating` 字段，但暂不自动抓取，避免依赖不稳定网页抓取。
- 详细步骤：[[10-books/Media Library 使用说明]]。

## 使用方式

- 手工新建一本书：插入 `99-templates/book.md`。
- 手工新建电影：插入 `99-templates/film.md`。
- 手工新建电视剧：插入 `99-templates/series.md`。
- 新建章节笔记：插入 `99-templates/chapter.md`，并把 `book` 属性填写为对应书籍总页的文件名。
- `cover` 用于手工指定本地封面；Media DB 导入时通常使用 `image`，本页会自动兼容两者。
