---
type: area
homepage: true
icon: "📚"
description: "书籍、电影、电视剧与章节笔记"
order: 10
cssclasses:
  - library-hub
  - library-media-dashboard
---

# Media Library

> [!library-hero]
> **你的私人书影音库**  ·  Books · Movies · Series
>
> [[Home|← 首页]] · [[#继续阅读 / 观看|继续]] · [[#📚 Books|书籍]] · [[#🎬 Movies|电影]] · [[#📺 Series|电视剧]] · [[10-books/Media Library 使用说明|数据库导入]]

> [!library-stats]
> ```dataview
> TABLE WITHOUT ID
>   length(filter(rows, (r) => r.type = "book")) AS "📚 书籍",
>   length(filter(rows, (r) => r.type = "movie" OR r.type = "film")) AS "🎬 电影",
>   length(filter(rows, (r) => r.type = "series")) AS "📺 剧集",
>   length(filter(rows, (r) => r.status = "reading" OR r.status = "watching")) AS "▶ 进行中"
> FROM "10-books"
> WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
> GROUP BY true
> ```

## 继续阅读 / 观看

> [!library-continue]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   choice(type = "book", "📖 Book", choice(type = "series", "📺 Series", "🎬 Movie")) AS "",
>   choice(status, status, choice(read, "已读", choice(watched, "已看", "未标记"))) AS "",
>   choice(personalRating, "★ " + personalRating, choice(rating, "★ " + rating, choice(onlineRating, "★ " + onlineRating, ""))) AS ""
> FROM "10-books"
> WHERE (type = "book" OR type = "movie" OR type = "film" OR type = "series")
>   AND (status = "reading" OR status = "watching")
> SORT file.mtime DESC
> LIMIT 6
> ```

## 📚 Books

> [!media-shelf]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   author AS "",
>   year AS "",
>   choice(status, status, choice(read, "已读", "未读")) AS "",
>   choice(personalRating, "★ " + personalRating, choice(rating, "★ " + rating, choice(onlineRating, "★ " + onlineRating, ""))) AS ""
> FROM "10-books"
> WHERE type = "book"
> SORT status ASC, file.name ASC
> ```

## 🎬 Movies

> [!media-shelf]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   director AS "",
>   year AS "",
>   choice(status, status, choice(watched, "已看", "未看")) AS "",
>   choice(personalRating, "★ " + personalRating, choice(rating, "★ " + rating, choice(onlineRating, "★ " + onlineRating, ""))) AS ""
> FROM "10-books"
> WHERE type = "movie" OR type = "film"
> SORT status ASC, file.name ASC
> ```

## 📺 Series

> [!media-shelf]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   genres AS "",
>   year AS "",
>   choice(status, status, choice(watched, "已看", "未看")) AS "",
>   choice(personalRating, "★ " + personalRating, choice(rating, "★ " + rating, choice(onlineRating, "★ " + onlineRating, ""))) AS ""
> FROM "10-books"
> WHERE type = "series"
> SORT status ASC, file.name ASC
> ```

## Recently Updated

> [!library-recent]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS "",
>   choice(type = "book", "📖 书", choice(type = "series", "📺 剧", "🎬 电影")) AS "",
>   dataSource AS "",
>   dateformat(file.mtime, "MM-dd") AS ""
> FROM "10-books"
> WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
> SORT file.mtime DESC
> LIMIT 8
> ```

## Quick Add

> [!library-tools]
> **添加新条目：** 按 `Ctrl+P` 打开命令面板，然后运行 Media DB 的创建命令。
>
> - 书籍：`Media DB: Create entry (book)` → Open Library
> - 电影：`Media DB: Create entry (movie)` → TMDB
> - 电视剧：`Media DB: Create entry (series)` → TMDB
>
> TMDB 在当前网络环境下需要让 Obsidian 走代理；你现在使用 Clash TUN 即可。手工封面使用 `cover`，Media DB 自动下载的封面 / 海报使用 `image`，本看板会自动兼容两者。
