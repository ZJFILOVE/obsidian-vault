<%*
const fileDate = /^\d{4}-\d{2}-\d{2}$/.test(tp.file.title) ? tp.file.title : tp.date.now("YYYY-MM-DD");
if (!app.vault.getAbstractFileByPath("60-daily")) await app.vault.createFolder("60-daily");
if (tp.file.title !== fileDate) await tp.file.rename(fileDate);
const currentPath = tp.file.path(true);
if (!currentPath.startsWith("60-daily/")) await tp.file.move(`60-daily/${fileDate}`);

tR += `---
date: "${fileDate}"
type: daily
tags:
  - daily
---

# ${fileDate}

`;
%><% tp.file.cursor() %>
