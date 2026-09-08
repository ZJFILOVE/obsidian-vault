<%*
const books = app.vault.getMarkdownFiles()
  .map(file => ({ file, fm: app.metadataCache.getFileCache(file)?.frontmatter }))
  .filter(x => x.fm?.type === "book")
  .sort((a, b) => String(a.fm?.title ?? a.file.basename).localeCompare(String(b.fm?.title ?? b.file.basename)));

if (!books.length) {
  new Notice("没有找到 type: book 的书籍总页");
  return;
}

const chosen = await tp.system.suggester(
  books.map(x => `${x.fm?.title ?? x.file.basename}  —  ${x.file.path}`),
  books
);
if (!chosen) return;

const chapterNo = await tp.system.prompt("章节编号（如 1、2、3.1）");
const bookTitle = chosen.fm?.title ?? chosen.file.basename;
const bookPath = chosen.file.path.replace(/\.md$/, "");
let chapterTitle = tp.file.title;

if (/^(Untitled|未命名)/i.test(chapterTitle)) {
  const entered = await tp.system.prompt("章节笔记标题");
  if (entered) {
    chapterTitle = entered;
    await tp.file.rename(chapterTitle);
  }
}

const targetFolder = `10-books/chapters/${chosen.file.basename}`;
if (!app.vault.getAbstractFileByPath(targetFolder)) {
  await app.vault.createFolder(targetFolder);
}
await tp.file.move(`${targetFolder}/${chapterTitle}`);

const safeTitle = chapterTitle.replace(/"/g, '\\"');
const created = tp.date.now("YYYY-MM-DD");

tR += `---
title: "${safeTitle}"
type: chapter
book: "[[${bookPath}]]"
chapter: "${chapterNo ?? ""}"
reviewed: false
created: "${created}"
cssclasses:
  - chapter-note
tags:
  - book/chapter
---

# ${chapterTitle}

> [!chapter-nav]
> **所属书籍：** [[${bookPath}|${bookTitle}]]  ·  **章节：** ${chapterNo || "—"}
>
> [[10-books/Library|Library]]

## 要点

## 正文笔记

## 问题与回顾
`;
%>
