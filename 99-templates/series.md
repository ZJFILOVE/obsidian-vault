<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("剧集名");
if (!rawTitle?.trim()) { new Notice("已取消创建剧集笔记"); return; }
const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "10-books/movies";
if (tp.file.title !== fileName) await tp.file.rename(fileName);
await tp.file.move(`${targetFolder}/${fileName}`);
const yamlTitle = title.replace(/"/g, '\\"');

tR += `---
title: "${yamlTitle}"
type: series
year:
status: watching
watched: false
cover:
image:
rating:
personalRating:
onlineRating:
genres:
seasons:
dataSource: local
url:
id:
douban_url:
douban_rating:
reviewed: false
tags:
  - series
---

# ${title}

${tp.file.cursor()}
`;
%>
