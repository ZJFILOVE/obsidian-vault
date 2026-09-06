---
type: area
homepage: true
icon: "📰"
description: "每日长期影响新闻：只保留值得未来数月到数年继续关注的事件。"
order: 70
---

# 📰 News

> [!info] 筛选原则
> 这里不是热搜或资讯流。每天只记录少量具有**结构性、长期性、可持续跟踪价值**的新闻；宁缺毋滥。

## Latest

```dataview
TABLE WITHOUT ID
  file.link AS 日期,
  importance AS "最高重要度",
  topics AS "主题"
FROM "News/Daily"
WHERE type = "daily-news"
SORT date DESC
LIMIT 14
```

## Daily Archive

```dataview
LIST WITHOUT ID file.link
FROM "News/Daily"
WHERE type = "daily-news"
SORT date DESC
```

## 关注维度

- 地缘政治与制度变化
- 宏观经济、金融与产业结构
- AI、半导体、计算基础设施
- 科学、生命科学、医药与重大技术突破
- 能源、气候与资源
- 中国及全球关键政策变化
- 其他可能改变未来数月到数年格局的事件

> 每日笔记中的自动生成部分由 ChatGPT 更新。你可以在自动区之外自由添加自己的判断、链接和后续追踪，不会被后续推送覆盖。
