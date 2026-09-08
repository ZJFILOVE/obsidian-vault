---
cssclasses:
  - hub-page
  - hub-home
---

# Knowledge Base

> [!hub-hero]
> **A quiet front door to the vault.**
> Research、学习、书影音与每日信息流都从这里进入。保留 Dracula 的深色底与紫青强调，但让层级、间距与卡片更克制。
>
> [[10-books/Library|Library]] · [[Music/Music|Music]] · [[50-courses/English/English|English]] · [[News/News|News]]

```dataviewjs
const pages = dv.pages("").array().filter(p => !p.file.path.startsWith("99-templates/"));
const media = pages.filter(p => ["book", "movie", "film", "series"].includes(p.type));
const areas = pages.filter(p => p.type === "area");
const recent = pages.filter(p => (p.file.mtime?.ts ?? 0) >= Date.now() - 7 * 86400000);
const metrics = [
  [pages.length, "Notes"],
  [areas.length, "Areas"],
  [media.length, "Media"],
  [recent.length, "7 Days"]
];
const root = this.container.createDiv({ cls: "hub-metrics-js" });
for (const [value, label] of metrics) {
  const card = root.createDiv({ cls: "hub-metric" });
  card.createDiv({ cls: "hub-metric-value", text: String(value) });
  card.createDiv({ cls: "hub-metric-label", text: label });
}
```

## Areas

```dataviewjs
function internalLink(parent, path, text) {
  const a = parent.createEl("a", { text, cls: "internal-link" });
  a.setAttr("data-href", path);
  a.setAttr("href", path);
  return a;
}
const areas = dv.pages("")
  .where(p => p.type === "area" && p.homepage === true)
  .array()
  .sort((a, b) => (a.order ?? 999) - (b.order ?? 999));
const grid = this.container.createDiv({ cls: "hub-area-grid" });
for (const p of areas) {
  const card = grid.createDiv({ cls: "hub-area-card" });
  card.createDiv({ cls: "hub-area-icon", text: p.icon || "◇" });
  internalLink(card, p.file.path, p.file.name);
  card.createDiv({ cls: "hub-area-description", text: p.description || "" });
}
```

## Recently Active

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Note,
>   choice(type, type, "note") AS Type,
>   file.folder AS Location,
>   dateformat(file.mtime, "MM-dd HH:mm") AS Updated
> FROM ""
> WHERE file.name != "Home"
>   AND type != "area"
>   AND !startswith(file.folder, "99-templates")
> SORT file.mtime DESC
> LIMIT 12
> ```

## From the Collection

```dataviewjs
function link(parent, path, text) {
  const a = parent.createEl("a", { text, cls: "internal-link hub-media-title" });
  a.setAttr("data-href", path);
  a.setAttr("href", path);
}
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
function cover(parent, p) {
  const box = parent.createDiv({ cls: "hub-feature-cover" });
  const path = pathOf(p.cover || p.image);
  const file = path ? app.vault.getAbstractFileByPath(path) : null;
  if (file) {
    const img = box.createEl("img");
    img.src = app.vault.getResourcePath(file);
    img.alt = p.title || p.file.name;
  }
}
const items = dv.pages('"10-books"')
  .where(p => ["book", "movie", "film", "series"].includes(p.type))
  .array()
  .sort((a, b) => (b.file.mtime?.ts ?? 0) - (a.file.mtime?.ts ?? 0))
  .slice(0, 4);
if (!items.length) {
  this.container.createDiv({ cls: "hub-empty-state", text: "No media entries yet." });
} else {
  const grid = this.container.createDiv({ cls: "hub-feature-grid" });
  for (const p of items) {
    const card = grid.createDiv({ cls: "hub-feature-card" });
    cover(card, p);
    const body = card.createDiv({ cls: "hub-feature-body" });
    link(body, p.file.path, p.title || p.file.name);
    const who = p.type === "book" ? p.author : (p.director || p.genres);
    body.createDiv({ cls: "hub-media-meta", text: [textOf(who), p.year].filter(Boolean).join(" · ") });
    body.createDiv({ cls: "hub-media-meta", text: p.status || p.type || "" });
  }
}
```

## Weekly Review

> [!hub-table]
> ```dataview
> TABLE WITHOUT ID
>   file.link AS Note,
>   durationformat(date(now) - file.mtime, "d'd'") + " ago" AS Modified,
>   file.folder AS Location,
>   choice(reviewed = true, "✓", choice(reviewed = false, "○", "—")) AS Reviewed
> FROM ""
> WHERE file.mtime >= (date(today) - dur(7 days))
>   AND file.name != "Home"
>   AND type != "area"
>   AND !startswith(file.folder, "99-templates")
> SORT file.mtime DESC
> LIMIT 16
> ```
