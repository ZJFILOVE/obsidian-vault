---
type: area
homepage: true
icon: "📚"
description: "书籍、电影、电视剧与章节笔记"
order: 10
cssclasses:
  - hub-page
  - hub-library
---

# Library

> [!hub-hero]
> **Books · Cinema · Series**
> 书籍、电影与剧集共用同一套现代编辑式视觉：深色底、克制的紫青强调、大留白与细边框；封面和海报作为主要视觉主体。
>
> [[Home|Home]] · [[#Recent Collection|Recent]] · [[#Books|Books]] · [[#Movies|Movies]] · [[#Series|Series]] · [[10-books/Media Library 使用说明|Import Guide]]

```dataviewjs
const items = dv.pages('"10-books"')
  .where(p => ["book", "movie", "film", "series"].includes(p.type))
  .array();
const metrics = [
  [items.filter(p => p.type === "book").length, "Books"],
  [items.filter(p => p.type === "movie" || p.type === "film").length, "Movies"],
  [items.filter(p => p.type === "series").length, "Series"],
  [items.filter(p => p.status === "reading" || p.status === "watching").length, "Active"]
];
const root = this.container.createDiv({ cls: "hub-metrics-js" });
for (const [value, label] of metrics) {
  const card = root.createDiv({ cls: "hub-metric" });
  card.createDiv({ cls: "hub-metric-value", text: String(value) });
  card.createDiv({ cls: "hub-metric-label", text: label });
}
```

## Recent Collection

```dataviewjs
function renderMedia(container, items) {
  function pathOf(raw) {
    if (!raw) return null;
    let path = raw.path ?? String(raw);
    return path.replace(/^!?\[\[/, "").replace(/\]\]$/, "").split("|")[0];
  }
  function textOf(v) {
    if (v == null) return "";
    if (Array.isArray(v)) return v.join(", ");
    try { if (typeof v !== "string" && v[Symbol.iterator]) return Array.from(v).join(", "); } catch (_) {}
    return String(v);
  }
  function addLink(parent, p) {
    const a = parent.createEl("a", { text: p.title || p.file.name, cls: "internal-link hub-media-title" });
    a.setAttr("data-href", p.file.path);
    a.setAttr("href", p.file.path);
  }
  if (!items.length) {
    container.createDiv({ cls: "hub-empty-state", text: "No entries yet." });
    return;
  }
  const grid = container.createDiv({ cls: "hub-media-grid" });
  for (const p of items) {
    const card = grid.createDiv({ cls: "hub-media-card" });
    const cover = card.createDiv({ cls: "hub-media-cover" });
    const path = pathOf(p.cover || p.image);
    const file = path ? app.vault.getAbstractFileByPath(path) : null;
    if (file) {
      const img = cover.createEl("img");
      img.src = app.vault.getResourcePath(file);
      img.alt = p.title || p.file.name;
    } else {
      cover.createDiv({ cls: "hub-media-cover-empty", text: p.type || "media" });
    }
    const body = card.createDiv({ cls: "hub-media-body" });
    addLink(body, p);
    const creator = p.type === "book" ? p.author : (p.director || p.genres);
    body.createDiv({ cls: "hub-media-meta", text: textOf(creator) || "—" });
    body.createDiv({ cls: "hub-media-meta", text: String(p.year || "") });
    const footer = body.createDiv({ cls: "hub-media-footer" });
    footer.createDiv({ cls: "hub-media-status", text: p.status || (p.watched ? "watched" : p.read ? "read" : p.type || "") });
    const rating = (p.personalRating && Number(p.personalRating) > 0) ? p.personalRating : (p.rating || p.onlineRating);
    footer.createDiv({ cls: "hub-media-rating", text: rating ? `★ ${rating}` : "" });
  }
}
const items = dv.pages('"10-books"')
  .where(p => ["book", "movie", "film", "series"].includes(p.type))
  .array()
  .sort((a, b) => (b.file.mtime?.ts ?? 0) - (a.file.mtime?.ts ?? 0))
  .slice(0, 8);
renderMedia(this.container, items);
```

## Continue

```dataviewjs
function pathOf(raw) {
  if (!raw) return null;
  let path = raw.path ?? String(raw);
  return path.replace(/^!?\[\[/, "").replace(/\]\]$/, "").split("|")[0];
}
function textOf(v) {
  if (v == null) return "";
  if (Array.isArray(v)) return v.join(", ");
  try { if (typeof v !== "string" && v[Symbol.iterator]) return Array.from(v).join(", "); } catch (_) {}
  return String(v);
}
const items = dv.pages('"10-books"')
  .where(p => ["book", "movie", "film", "series"].includes(p.type) && (p.status === "reading" || p.status === "watching"))
  .array()
  .sort((a, b) => (b.file.mtime?.ts ?? 0) - (a.file.mtime?.ts ?? 0));
if (!items.length) {
  this.container.createDiv({ cls: "hub-empty-state", text: "Nothing marked as reading or watching." });
} else {
  const grid = this.container.createDiv({ cls: "hub-feature-grid" });
  for (const p of items.slice(0, 6)) {
    const card = grid.createDiv({ cls: "hub-feature-card" });
    const cover = card.createDiv({ cls: "hub-feature-cover" });
    const path = pathOf(p.cover || p.image);
    const file = path ? app.vault.getAbstractFileByPath(path) : null;
    if (file) {
      const img = cover.createEl("img");
      img.src = app.vault.getResourcePath(file);
      img.alt = p.title || p.file.name;
    }
    const body = card.createDiv({ cls: "hub-feature-body" });
    const a = body.createEl("a", { text: p.title || p.file.name, cls: "internal-link hub-media-title" });
    a.setAttr("data-href", p.file.path);
    a.setAttr("href", p.file.path);
    const creator = p.type === "book" ? p.author : (p.director || p.genres);
    body.createDiv({ cls: "hub-media-meta", text: [textOf(creator), p.year].filter(Boolean).join(" · ") });
    body.createDiv({ cls: "hub-media-meta", text: p.status || "" });
  }
}
```

## Books

```dataviewjs
function mediaGrid(container, items) {
  const pathOf = raw => raw ? (raw.path ?? String(raw)).replace(/^!?\[\[/, "").replace(/\]\]$/, "").split("|")[0] : null;
  const textOf = v => Array.isArray(v) ? v.join(", ") : (v == null ? "" : String(v));
  if (!items.length) { container.createDiv({ cls: "hub-empty-state", text: "No books yet." }); return; }
  const grid = container.createDiv({ cls: "hub-media-grid" });
  for (const p of items) {
    const card = grid.createDiv({ cls: "hub-media-card" });
    const cover = card.createDiv({ cls: "hub-media-cover" });
    const path = pathOf(p.cover || p.image);
    const file = path ? app.vault.getAbstractFileByPath(path) : null;
    if (file) { const img = cover.createEl("img"); img.src = app.vault.getResourcePath(file); img.alt = p.title || p.file.name; }
    else cover.createDiv({ cls: "hub-media-cover-empty", text: "book" });
    const body = card.createDiv({ cls: "hub-media-body" });
    const a = body.createEl("a", { text: p.title || p.file.name, cls: "internal-link hub-media-title" });
    a.setAttr("data-href", p.file.path); a.setAttr("href", p.file.path);
    body.createDiv({ cls: "hub-media-meta", text: textOf(p.author) || "—" });
    body.createDiv({ cls: "hub-media-meta", text: String(p.year || "") });
    const f = body.createDiv({ cls: "hub-media-footer" });
    f.createDiv({ cls: "hub-media-status", text: p.status || (p.read ? "read" : "unread") });
    const rating = (p.personalRating && Number(p.personalRating) > 0) ? p.personalRating : (p.rating || p.onlineRating);
    f.createDiv({ cls: "hub-media-rating", text: rating ? `★ ${rating}` : "" });
  }
}
const items = dv.pages('"10-books"').where(p => p.type === "book").array().sort((a,b) => String(a.title || a.file.name).localeCompare(String(b.title || b.file.name)));
mediaGrid(this.container, items);
```

## Movies

```dataviewjs
function mediaGrid(container, items) {
  const pathOf = raw => raw ? (raw.path ?? String(raw)).replace(/^!?\[\[/, "").replace(/\]\]$/, "").split("|")[0] : null;
  const textOf = v => Array.isArray(v) ? v.join(", ") : (v == null ? "" : String(v));
  if (!items.length) { container.createDiv({ cls: "hub-empty-state", text: "No movies yet." }); return; }
  const grid = container.createDiv({ cls: "hub-media-grid" });
  for (const p of items) {
    const card = grid.createDiv({ cls: "hub-media-card" });
    const cover = card.createDiv({ cls: "hub-media-cover" });
    const path = pathOf(p.cover || p.image);
    const file = path ? app.vault.getAbstractFileByPath(path) : null;
    if (file) { const img = cover.createEl("img"); img.src = app.vault.getResourcePath(file); img.alt = p.title || p.file.name; }
    else cover.createDiv({ cls: "hub-media-cover-empty", text: "movie" });
    const body = card.createDiv({ cls: "hub-media-body" });
    const a = body.createEl("a", { text: p.title || p.file.name, cls: "internal-link hub-media-title" });
    a.setAttr("data-href", p.file.path); a.setAttr("href", p.file.path);
    body.createDiv({ cls: "hub-media-meta", text: textOf(p.director) || "—" });
    body.createDiv({ cls: "hub-media-meta", text: String(p.year || "") });
    const f = body.createDiv({ cls: "hub-media-footer" });
    f.createDiv({ cls: "hub-media-status", text: p.status || (p.watched ? "watched" : "unwatched") });
    const rating = (p.personalRating && Number(p.personalRating) > 0) ? p.personalRating : (p.rating || p.onlineRating);
    f.createDiv({ cls: "hub-media-rating", text: rating ? `★ ${rating}` : "" });
  }
}
const items = dv.pages('"10-books"').where(p => p.type === "movie" || p.type === "film").array().sort((a,b) => String(a.title || a.file.name).localeCompare(String(b.title || b.file.name)));
mediaGrid(this.container, items);
```

## Series

```dataviewjs
function mediaGrid(container, items) {
  const pathOf = raw => raw ? (raw.path ?? String(raw)).replace(/^!?\[\[/, "").replace(/\]\]$/, "").split("|")[0] : null;
  const textOf = v => Array.isArray(v) ? v.join(", ") : (v == null ? "" : String(v));
  if (!items.length) { container.createDiv({ cls: "hub-empty-state", text: "No series yet." }); return; }
  const grid = container.createDiv({ cls: "hub-media-grid" });
  for (const p of items) {
    const card = grid.createDiv({ cls: "hub-media-card" });
    const cover = card.createDiv({ cls: "hub-media-cover" });
    const path = pathOf(p.cover || p.image);
    const file = path ? app.vault.getAbstractFileByPath(path) : null;
    if (file) { const img = cover.createEl("img"); img.src = app.vault.getResourcePath(file); img.alt = p.title || p.file.name; }
    else cover.createDiv({ cls: "hub-media-cover-empty", text: "series" });
    const body = card.createDiv({ cls: "hub-media-body" });
    const a = body.createEl("a", { text: p.title || p.file.name, cls: "internal-link hub-media-title" });
    a.setAttr("data-href", p.file.path); a.setAttr("href", p.file.path);
    body.createDiv({ cls: "hub-media-meta", text: textOf(p.genres) || "—" });
    body.createDiv({ cls: "hub-media-meta", text: String(p.year || "") });
    const f = body.createDiv({ cls: "hub-media-footer" });
    f.createDiv({ cls: "hub-media-status", text: p.status || (p.watched ? "watched" : "unwatched") });
    const rating = (p.personalRating && Number(p.personalRating) > 0) ? p.personalRating : (p.rating || p.onlineRating);
    f.createDiv({ cls: "hub-media-rating", text: rating ? `★ ${rating}` : "" });
  }
}
const items = dv.pages('"10-books"').where(p => p.type === "series").array().sort((a,b) => String(a.title || a.file.name).localeCompare(String(b.title || b.file.name)));
mediaGrid(this.container, items);
```

## Recently Updated

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Work,
>   choice(type = "book", "Book", choice(type = "series", "Series", "Movie")) AS Type,
>   dataSource AS Source,
>   dateformat(file.mtime, "yyyy-MM-dd HH:mm") AS Updated
> FROM "10-books"
> WHERE type = "book" OR type = "movie" OR type = "film" OR type = "series"
> SORT file.mtime DESC
> LIMIT 10
> ```

> [!hub-hero]
> **Quick Add**
> `Ctrl+P` → `Media DB: Create entry (book/movie/series)`。TMDB 搜索时让 Obsidian 走 Clash TUN；手工 `cover` 与 Media DB `image` 都会被统一渲染。
