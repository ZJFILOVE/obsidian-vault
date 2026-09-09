<%*
const labels = ["General", "Blog"];
const kind = await tp.system.suggester(labels, labels, false, "写作类型");
if (!kind) return;

let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt(kind === "Blog" ? "博客标题" : "标题");
if (!rawTitle?.trim()) { new Notice("已取消创建写作笔记"); return; }

const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
const targetFolder = kind === "Blog" ? "40-writing/blog" : "40-writing";
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

if (kind === "Blog") {
  const yamlTitle = title.replace(/"/g, '\\"');
  const postDate = tp.date.now("YYYY-MM-DD HH:mm:ss ZZ");
  tR += `---\nlayout: post\ntitle: "${yamlTitle}"\nsubtitle:\ndate: "${postDate}"\nauthor: "ZJF"\nheader-img: "img/webb-deep-field.jpg"\nheader-img-credit: "NASA / ESA / CSA / STScI"\nheader-img-credit-href: "https://images.nasa.gov/details-webb_first_deep_field"\ncatalog: true\ntags:\n  - 随笔\n---\n\n# ${title}\n\n`;
} else {
  tR += `---\ntype: writing\ncreated: "${created}"\n---\n\n# ${title}\n\n`;
}
%><% tp.file.cursor() %>
