<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("Area 名称");
if (!rawTitle?.trim()) { new Notice("已取消创建 Area"); return; }
const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const activeFile = app.workspace.getActiveFile();
const currentFolder = activeFile?.parent?.path ?? "";
const requestedFolder = await tp.system.prompt("目标文件夹（留空 = 保持当前位置）", currentFolder);
const targetFolder = (requestedFolder ?? currentFolder).trim().replace(/^\/+|\/+$/g, "");

async function ensureFolder(path) {
  let current = "";
  for (const part of path.split("/").filter(Boolean)) {
    current = current ? `${current}/${part}` : part;
    if (!app.vault.getAbstractFileByPath(current)) await app.vault.createFolder(current);
  }
}
if (targetFolder) await ensureFolder(targetFolder);
if (tp.file.title !== fileName) await tp.file.rename(fileName);
if (targetFolder && !(tp.file.path(true) ?? "").startsWith(`${targetFolder}/`)) {
  await tp.file.move(`${targetFolder}/${fileName}`);
}

const yamlTitle = title.replace(/"/g, '\\"');
tR += `---
title: "${yamlTitle}"
type: area
homepage: true
icon: "🧭"
description:
order: 100
cssclasses:
  - hub-page
---

# ${title}

> [!hub-hero]
> [[Home|Home]]

${tp.file.cursor()}

## Recently Active

> [!hub-table]
> \`\`\`dataview
> TABLE WITHOUT ID
>   file.link AS Note,
>   choice(type, type, "note") AS Type,
>   dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS Updated
> FROM ""
> WHERE startswith(file.folder, this.file.folder)
>   AND file.path != this.file.path
>   AND type != "area"
> SORT file.mtime DESC
> LIMIT 15
> \`\`\`
`;
%>
