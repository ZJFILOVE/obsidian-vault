<%*
const books = app.vault.getMarkdownFiles()
  .map(file => ({ file, fm: app.metadataCache.getFileCache(file)?.frontmatter }))
  .filter(x => x.fm?.type === "book")
  .sort((a, b) => String(a.fm?.title ?? a.file.basename).localeCompare(String(b.fm?.title ?? b.file.basename)));

if (!books.length) { new Notice("没有找到 type: book 的书籍总页"); return; }

const chosen = await tp.system.suggester(
  books.map(x => `${x.fm?.title ?? x.file.basename}  —  ${x.file.path}`),
  books,
  false,
  "选择所属书籍"
);
if (!chosen) return;

const chapterNo = await tp.system.prompt("章节编号（可留空，如 1、2、3.1）");
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("章节标题");
if (!rawTitle?.trim()) { new Notice("已取消创建章节笔记"); return; }

const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const bookPath = chosen.file.path.replace(/\.md$/, "");
const targetFolder = `10-books/chapters/${chosen.file.basename}`;
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

tR += `---\ntype: chapter\nbook: "[[${bookPath}]]"\nchapter: "${(chapterNo ?? "").replace(/"/g, '\\"')}"\ncreated: "${created}"\n---\n\n# ${title}\n\n`;
%><% tp.file.cursor() %>
