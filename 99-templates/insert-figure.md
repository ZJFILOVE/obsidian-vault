<%*
const rawImage = await tp.system.prompt("图片文件名或 Vault 路径（如 Fig3.png）");
if (!rawImage?.trim()) { new Notice("已取消插入图片"); return; }

const image = rawImage.trim().replace(/^!?\[\[/, "").replace(/\]\]$/, "");
const caption = await tp.system.prompt("图注（可留空）");

tR += `![[${image}]]`;
if (caption?.trim()) tR += `\n\n*${caption.trim()}*`;
%>
