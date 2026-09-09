<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("电影名");
if (!rawTitle?.trim()) { new Notice("已取消创建电影笔记"); return; }
const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "10-books/movies";
if (tp.file.title !== fileName) await tp.file.rename(fileName);
await tp.file.move(`${targetFolder}/${fileName}`);
const yamlTitle = title.replace(/"/g, '\\"');

tR += `---
title: "${yamlTitle}"
type: movie
director:
year:
status: planned
watched: false
cover:
image:
rating:
personalRating:
onlineRating:
dataSource: local
url:
id:
douban_url:
douban_rating:
reviewed: false
tags:
  - movie
---

# ${title}

`;
%><% tp.file.cursor() %>
