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
const bookTitle = chosen.fm?.title ?? chosen.file.basename;
const bookPath = chosen.file.path.replace(/\.md$/, "");
const targetFolder = `10-books/chapters/${chosen.file.basename}`;

async function ensureFolder(path) {
  let current = "";
  for (const part of path.split("/").filter(Boolean)) {
    current = current ? `${current}/${part}` : part;
    if (!app.vault.getAbstractFileByPath(current)) await app.vault.createFolder(current);
  }
}
await ensureFolder(targetFolder);
if (tp.file.title !== fileName) await tp.file.rename(fileName);
await tp.file.move(`${targetFolder}/${fileName}`);

const yamlTitle = title.replace(/"/g, '\\"');
const created = tp.date.now("YYYY-MM-DD");

tR += `---
title: "${yamlTitle}"
type: chapter
book: "[[${bookPath}]]"
chapter: "${(chapterNo ?? "").replace(/"/g, '\\"')}"
reviewed: false
created: "${created}"
cssclasses:
  - chapter-note
tags:
  - book/chapter
---

# ${title}

> [!chapter-nav]
> [[${bookPath}|${bookTitle}]]${chapterNo ? ` · Chapter ${chapterNo}` : ""} · [[10-books/Library|Library]]

`;
%><% tp.file.cursor() %>
