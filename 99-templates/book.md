<%*
const rawTitle = /^(Untitled|未命名|新建笔记)/i.test(tp.file.title)
  ? await tp.system.prompt("书名")
  : tp.file.title;
if (!rawTitle?.trim()) { new Notice("已取消创建书籍笔记"); return; }

const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "10-books";
if (tp.file.title !== fileName) await tp.file.rename(fileName);
if (tp.file.folder(true) !== targetFolder) await tp.file.move(`${targetFolder}/${fileName}`);

const yamlTitle = title.replace(/"/g, '\\"');
const created = tp.date.now("YYYY-MM-DD");

tR += `---
title: "${yamlTitle}"
type: book
author:
year:
publisher:
pages:
status: reading
read: false
cover:
image:
rating:
personalRating:
onlineRating:
isbn:
isbn13:
dataSource: local
url:
id:
douban_url:
douban_rating:
reviewed: false
created: "${created}"
cssclasses:
  - wide-note
  - book-detail
tags:
  - book
---

# ${title}

## Chapters

\`\`\`dataview
TABLE WITHOUT ID
  chapter AS 章节,
  file.link AS 笔记,
  dateformat(file.mtime, "MM-dd") AS 更新
FROM "10-books"
WHERE type = "chapter"
  AND (book = this.file.link OR book = this.file.name)
SORT chapter ASC
\`\`\`

${tp.file.cursor()}
`;
%>
