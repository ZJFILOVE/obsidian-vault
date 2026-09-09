<%*
const types = ["draft", "essay", "article"];
const type = await tp.system.suggester(types, types, false, "写作类型");
if (!type) return;

let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("标题");
if (!rawTitle?.trim()) { new Notice("已取消创建写作笔记"); return; }

const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const created = tp.date.now("YYYY-MM-DD");

if (tp.file.title !== fileName) await tp.file.rename(fileName);

tR += `---\ntype: ${type}\ncreated: "${created}"\n---\n\n# ${title}\n\n${tp.file.cursor()}\n`;
%>
