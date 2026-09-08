<%*
let rawTitle = tp.file.title;
if (/^(Untitled|未命名|新建笔记)/i.test(rawTitle)) rawTitle = await tp.system.prompt("博客标题");
if (!rawTitle?.trim()) { new Notice("已取消创建博客草稿"); return; }
const title = rawTitle.trim();
const fileName = title.replace(/[\\/:*?"<>|]/g, " - ").replace(/\s+/g, " ").trim();
if (tp.file.title !== fileName) await tp.file.rename(fileName);
const yamlTitle = title.replace(/"/g, '\\"');
const postDate = tp.date.now("YYYY-MM-DD HH:mm:ss ZZ");

tR += `---
layout: post
title: "${yamlTitle}"
subtitle:
date: "${postDate}"
author: "ZJF"
header-img: "img/webb-deep-field.jpg"
header-img-credit: "NASA / ESA / CSA / STScI"
header-img-credit-href: "https://images.nasa.gov/details-webb_first_deep_field"
catalog: true
tags:
  - 随笔
---

# ${title}

${tp.file.cursor()}
`;
%>
