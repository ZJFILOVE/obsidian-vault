---
type: note
tags:
  - library
  - obsidian
  - media-db
---

# Media Library 使用说明

## 数据库检索

本 Vault 的图书、电影和电视剧统一放在 `10-books/` 下，并由 `10-books/Library.md` 汇总。

推荐安装 Obsidian 社区插件 **Media DB**（插件 ID：`obsidian-media-db-plugin`）。仓库已经预置它的 `data.json`：

- 图书 → `10-books/books`
- 电影 → `10-books/movies`
- 电视剧 / 季 → `10-books/series`
- 自动下载的封面 / 海报 → `10-books/assets/covers`

### Arch / Linux 一键安装

在 Vault 根目录执行：

```bash
bash scripts/install-obsidian-media-db.sh
```

脚本会安装并启用 Media DB 0.9.1。完成后重启 Obsidian。

也可以直接在 Obsidian → Settings → Community plugins → Browse 中搜索 `Media DB` 安装。

安装插件以后，使用命令面板：

- `Media DB: Create entry (book)`：按书名检索图书；Open Library 不需要 API key。
- `Media DB: Create entry (movie)`：检索电影。
- `Media DB: Create entry (series)`：检索电视剧。
- `Media DB: Create entry by id`：已知数据库 ID 时精确导入。
- `Media DB: Update metadata`：以后重新从数据库更新元数据。

也就是说，正常使用时不需要再手工建立 Markdown：**搜标题 → 选数据库结果 → 自动生成条目 → Library 自动出现卡片**。

## 电影 / 电视剧数据库

电影和电视剧建议使用 TMDB。Media DB 的 TMDB 接口需要你在插件设置里填写 **API Read Access Token**。不要把 token 写进 Git 仓库；只保存在 Obsidian 的本地 Secret Storage 中。

## 图书数据库

Media DB 当前直接支持 Open Library，而且不需要 API key。一般英文书检索效果很好；中文旧书可能没有条目，此时保留本地手工元数据即可。

## 豆瓣

目前不把豆瓣作为自动抓取源。豆瓣没有适合这个工作流的稳定公开 API，直接网页抓取也容易受反爬和页面变化影响。条目里可以保留：

```yaml
douban_url:
douban_rating:
```

需要时手工补豆瓣链接 / 评分，或者后续再单独做可维护的导入脚本。

## 字段约定

数据库导入和手工条目统一识别这些字段：

```yaml
type: book | movie | series
cover:             # 本地手工封面
image:             # Media DB 自动封面 / 海报
rating:            # 旧模板个人评分
personalRating:    # Media DB 个人评分
onlineRating:      # 数据库评分
status:            # reading / completed / watching / planned ...
dataSource:         # OpenLibraryAPI / TMDBMovieAPI / TMDBSeriesAPI / local
url:
id:
douban_url:
douban_rating:
```

`Library.md` 同时兼容旧的 `cover/rating` 和 Media DB 的 `image/personalRating/onlineRating` 字段。
