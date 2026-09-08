---
cssclasses:
  - hub-page
  - hub-home
---

# Knowledge Base

> [!hub-hero]
> **A quiet front door to the vault.**
> Research、学习、书影音与每日信息流都从这里进入；保留 Dracula 的深色底与紫青强调，但把界面收敛成更耐看的现代编辑式布局。
>
> [[10-books/Library|Library]] · [[Music/Music|Music]] · [[50-courses/English/English|English]] · [[News/News|News]]

> [!hub-metrics]
> ```dataview
> TABLE WITHOUT ID
>   length(rows) AS "Notes",
>   length(filter(rows, (r) => r.type = "area")) AS "Areas",
>   length(filter(rows, (r) => r.type = "book" OR r.type = "movie" OR r.type = "film" OR r.type = "series")) AS "Media",
>   length(filter(rows, (r) => r.file.mtime >= (date(today) - dur(7 days)))) AS "7 Days"
> FROM ""
> WHERE !startswith(file.folder, "99-templates")
> GROUP BY true
> ```

## Areas

> [!hub-grid]
> ```dataview
> TABLE WITHOUT ID
>   icon AS "",
>   file.link AS "",
>   description AS ""
> FROM ""
> WHERE type = "area" AND homepage = true
> SORT order ASC, file.name ASC
> ```

## Recently Active

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Note,
>   choice(type, type, "note") AS Type,
>   file.folder AS Location,
>   dateformat(file.mtime, "MM-dd HH:mm") AS Updated
> FROM ""
> WHERE file.name != "Home"
>   AND type != "area"
>   AND !startswith(file.folder, "99-templates")
> SORT file.mtime DESC
> LIMIT 12
> ```

## From the Collection

> [!feature-row]
> ```dataview
> TABLE WITHOUT ID
>   choice(cover, embed(cover), choice(image, embed(image), "")) AS "",
>   file.link AS "",
>   choice(type = "book", author, choice(type = "movie" OR type = "film", director, genres)) AS "",
>   year AS "",
>   status AS ""
> FROM "10-books"
> WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
> SORT file.mtime DESC
> LIMIT 4
> ```

## Weekly Review

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Note,
>   durationformat(date(now) - file.mtime, "d'd'") + " ago" AS Modified,
>   file.folder AS Location,
>   choice(reviewed = true, "✓", choice(reviewed = false, "○", "—")) AS Reviewed
> FROM ""
> WHERE file.mtime >= (date(today) - dur(7 days))
>   AND file.name != "Home"
>   AND type != "area"
>   AND !startswith(file.folder, "99-templates")
> SORT file.mtime DESC
> LIMIT 16
> ```
