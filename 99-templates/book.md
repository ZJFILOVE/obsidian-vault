<%*
const rawTitle = /^(Untitled|未命名|新建笔记)/i.test(tp.file.title)
  ? await tp.system.prompt("书名")
  : tp.file.title;
if (!rawTitle?.trim()) { new Notice("已取消创建书籍笔记"); return; }

const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "10-books/books";
const yamlTitle = title.replace(/"/g, '\\"');
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

tR += `---\ntitle: "${yamlTitle}"\ntype: book\nauthor:\nyear:\npublisher:\npages:\nstatus: reading\ncover:\nrating:\ndataSource: local\nurl:\ndouban_url:\ndouban_rating:\ncreated: "${created}"\n---\n\n# ${title}\n\n## Chapters\n\n\`\`\`dataview\nTABLE WITHOUT ID\n  chapter AS 章节,\n  file.link AS 笔记,\n  dateformat(file.mtime, "MM-dd") AS 更新\nFROM "10-books"\nWHERE type = "chapter"\n  AND (book = this.file.link OR book = this.file.name)\nSORT chapter ASC\n\`\`\`\n\n`;
%><% tp.file.cursor() %>
