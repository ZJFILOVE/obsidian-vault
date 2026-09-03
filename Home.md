---
cssclasses:
  - knowledge-home
---

# 🧠 Homepage

Welcome to your vault.

> [!quote] 随手写，慢慢整理；主页只放值得每天看到的东西。

> [!multi-column]
>
>> [!library] 📚 Library
>> *书评、影评与章节笔记*
>> - [[10-books/Library|进入个人图书馆]]
>> - [[Home#Library|主页看板]]
>
>> [!english] 🌐 English
>> *CET · Translation · Vocabulary*
>> - [[Home#English|最近英语训练]]
>> - [[Home#最近修改|最近修改]]
>
>> [!templates] ✍️ Templates
>> *快速开始一篇新笔记*
>> - [[99-templates/book|书籍模板]]
>> - [[99-templates/chapter|章节模板]]
>> - [[99-templates/film|电影模板]]
>
>> [!review] ✅ Review
>> *把最近改过的笔记重新看一遍*
>> - [[Home#Weekly Review|Weekly Review]]
>> - [[Home#最近修改|Recent Notes]]

---

## 📚 Library

> [!multi-column]
>
>> [!books] 📖 Books
>> ```dataview
>> LIST WITHOUT ID file.link
>> FROM "10-books"
>> WHERE type = "book"
>> SORT file.mtime DESC
>> LIMIT 8
>> ```
>> [[10-books/Library|打开完整图书馆 →]]
>
>> [!films] 🎬 Films
>> ```dataview
>> LIST WITHOUT ID file.link
>> FROM "10-books"
>> WHERE type = "film"
>> SORT file.mtime DESC
>> LIMIT 8
>> ```
>> [[10-books/Library#🎬 电影|打开影评区 →]]

> [!tip] 书籍导航方式
> 首页点击书名 → 进入书籍总页 → 在“章节目录”中点击具体章节笔记。章节目录由 Dataview 根据 `type: chapter`、`book:` 和 `chapter:` 自动生成。

## 🌐 English

```dataview
TABLE WITHOUT ID
  file.link AS 笔记,
  dateformat(file.mtime, "MM-dd HH:mm") AS 修改
FROM "50-courses/English"
WHERE file.extension = "md"
SORT file.mtime DESC
LIMIT 6
```

## 📝 Weekly Review

> [!weekly-review]+ 最近 7 天需要回看的笔记
> *给笔记设置 `reviewed: true/false` 后，这里会显示复习状态。*
>
> ```dataview
> TABLE WITHOUT ID
>   file.link AS 文件,
>   durationformat(date(now) - file.mtime, "d'd'") + " ago" AS Modified,
>   file.folder AS Path,
>   choice(reviewed = true, "✅", choice(reviewed = false, "⬜", "—")) AS Reviewed
> FROM ""
> WHERE file.mtime >= (date(today) - dur(7 days))
>   AND file.name != "Home"
>   AND !startswith(file.folder, "99-templates")
> SORT file.mtime DESC
> LIMIT 20
> ```

## 最近修改

```dataview
TABLE WITHOUT ID
  file.link AS 笔记,
  dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS 修改时间
FROM ""
WHERE file.name != "Home" AND !startswith(file.folder, "99-templates")
SORT file.mtime DESC
LIMIT 10
```
