<%*
const imageExtensions = new Set(["png", "jpg", "jpeg", "webp", "gif", "svg", "bmp", "avif"]);

const images = app.vault.getFiles()
  .filter(file => imageExtensions.has(file.extension.toLowerCase()))
  .sort((a, b) => a.path.localeCompare(b.path, undefined, { numeric: true, sensitivity: "base" }));

if (!images.length) { new Notice("Vault 中没有可引用的图片"); return; }

const labels = images.map(file => `${file.name}  —  ${file.parent?.path ?? "/"}`);
const chosen = await tp.system.suggester(labels, images, false, "选择已有图片");
if (!chosen) return;

const caption = await tp.system.prompt("图注（可留空）");

tR += `![[${chosen.path}]]`;
if (caption?.trim()) tR += `\n\n*${caption.trim()}*`;
%>
