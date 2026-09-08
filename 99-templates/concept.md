<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("概念名称");
if (!rawTitle?.trim()) { new Notice("已取消创建概念笔记"); return; }
const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "30-concepts";
if (tp.file.title !== fileName) await tp.file.rename(fileName);
await tp.file.move(`${targetFolder}/${fileName}`);
const yamlTitle = title.replace(/"/g, '\\"');
const created = tp.date.now("YYYY-MM-DD");

tR += `---
title: "${yamlTitle}"
type: concept
created: "${created}"
aliases: []
tags:
  - concept
---

# ${title}

${tp.file.cursor()}
`;
%>
