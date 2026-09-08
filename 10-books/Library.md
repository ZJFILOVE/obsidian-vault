---
type: area
homepage: true
icon: "📚"
description: "书籍、电影、电视剧与章节笔记"
order: 10
cssclasses:
  - hub-page
  - hub-library
---

# Library

> [!hub-hero]
> **Books · Cinema · Series**
> 不是单独套一层“Netflix 皮肤”，而是和整个 Vault 共用同一套现代编辑式视觉：深色底、克制的紫青强调、大留白、细边框，封面仍然是这里的视觉主体。
>
> [[Home|Home]] · [[#Recent Collection|Recent]] · [[#Books|Books]] · [[#Movies|Movies]] · [[#Series|Series]] · [[10-books/Media Library 使用说明|Import Guide]]

> [!hub-metrics]
> ```dataview
> TABLE WITHOUT ID
>   length(filter(rows, (r) => r.type = "book")) AS "Books",
>   length(filter(rows, (r) => r.type = "movie" OR r.type = "film")) AS "Movies",
>   length(filter(rows, (r) => r.type = "series")) AS "Series",
>   length(filter(rows, (r) => r.status = "reading" OR r.status = "watching")) AS "Active"
> FROM "10-books"
> WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
> GROUP BY true
> ```

## Recent Collection

> [!media-grid]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   choice(type = "book", author, choice(type = "movie" OR type = "film", director, genres)) AS "",
>   year AS "",
>   status AS "",
>   choice(personalRating, personalRating, choice(rating, rating, onlineRating)) AS ""
> FROM "10-books"
> WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
> SORT file.mtime DESC
> LIMIT 8
> ```

## Continue

> [!feature-row]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   choice(type = "book", author, choice(type = "movie" OR type = "film", director, genres)) AS "",
>   year AS "",
>   status AS ""
> FROM "10-books"
> WHERE (type = "book" OR type = "movie" OR type = "film" OR type = "series")
>   AND (status = "reading" OR status = "watching")
> SORT file.mtime DESC
> LIMIT 6
> ```

## Books

> [!media-grid]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   author AS "",
>   year AS "",
>   choice(status, status, choice(read, "read", "unread")) AS "",
>   choice(personalRating, personalRating, choice(rating, rating, onlineRating)) AS ""
> FROM "10-books"
> WHERE type = "book"
> SORT status ASC, file.name ASC
> ```

## Movies

> [!media-grid]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   director AS "",
>   year AS "",
>   choice(status, status, choice(watched, "watched", "unwatched")) AS "",
>   choice(personalRating, personalRating, choice(rating, rating, onlineRating)) AS ""
> FROM "10-books"
> WHERE type = "movie" OR type = "film"
> SORT status ASC, file.name ASC
> ```

## Series

> [!media-grid]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   genres AS "",
>   year AS "",
>   choice(status, status, choice(watched, "watched", "unwatched")) AS "",
>   choice(personalRating, personalRating, choice(rating, rating, onlineRating)) AS ""
> FROM "10-books"
> WHERE type = "series"
> SORT status ASC, file.name ASC
> ```

## Recently Updated

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Work,
>   choice(type = "book", "Book", choice(type = "series", "Series", "Movie")) AS Type,
>   dataSource AS Source,
>   dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS Updated
> FROM "10-books"
> WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
> SORT file.mtime DESC
> LIMIT 10
> ```

> [!hub-hero]
> **Quick Add**
> `Ctrl+P` → `Media DB: Create entry (book/movie/series)`。TMDB 搜索时让 Obsidian 走 Clash TUN；封面无论来自手工 `cover` 还是 Media DB 的 `image`，本页都会统一显示。
