<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("论文标题");
if (!rawTitle?.trim()) { new Notice("已取消创建论文笔记"); return; }

const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "Resources/Papers";
const created = tp.date.now("YYYY-MM-DD");

async function ensureFolder(path) {
  let current = "";
  for (const part of path.split("/").filter(Boolean)) {
    current = current ? `${current}/${part}` : part;
    if (!app.vault.getAbstractFileByPath(current)) await app.vault.createFolder(current);
  }
}

await ensureFolder(targetFolder);
if (tp.file.title !== fileName) await tp.file.rename(fileName);
if (tp.file.folder(true) !== targetFolder) await tp.file.move(`${targetFolder}/${fileName}`);

tR += `---\ntype: paper\ncreated: "${created}"\n---\n\n# ${title}\n\n${tp.file.cursor()}\n`;
%>
