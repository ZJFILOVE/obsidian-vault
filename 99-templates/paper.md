<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("论文标题");
if (!rawTitle?.trim()) { new Notice("已取消创建论文笔记"); return; }
const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "Resources/Papers";
if (!app.vault.getAbstractFileByPath(targetFolder)) await app.vault.createFolder(targetFolder);
if (tp.file.title !== fileName) await tp.file.rename(fileName);
await tp.file.move(`${targetFolder}/${fileName}`);
const yamlTitle = title.replace(/"/g, '\\"');
const created = tp.date.now("YYYY-MM-DD");

tR += `---
title: "${yamlTitle}"
type: paper
authors:
year:
source:
created: "${created}"
tags:
  - paper
---

# ${title}

${tp.file.cursor()}
`;
%>
