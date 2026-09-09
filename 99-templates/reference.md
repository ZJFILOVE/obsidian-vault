<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("资料标题");
if (!rawTitle?.trim()) { new Notice("已取消创建资料笔记"); return; }

const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = "Resources/Reference";
const created = tp.date.now("YYYY-MM-DD");

if (!app.vault.getAbstractFileByPath("Resources")) await app.vault.createFolder("Resources");
if (!app.vault.getAbstractFileByPath(targetFolder)) await app.vault.createFolder(targetFolder);
if (tp.file.title !== fileName) await tp.file.rename(fileName);
if (tp.file.folder(true) !== targetFolder) await tp.file.move(`${targetFolder}/${fileName}`);

tR += `---\ntype: reference\ncreated: "${created}"\n---\n\n# ${title}\n\n`;
%><% tp.file.cursor() %>
