Minimal template policy

Creation templates only automate what the machine must know: type, title, destination, and a small amount of metadata. They should not prescribe how to think or how to structure the body.

Canonical creation templates:
- paper.md: one paper = one Markdown file in Resources/Papers
- note.md: General note or Concept; Concept moves to 30-concepts
- writing.md: General writing or Blog; Blog preserves the publishing YAML
- chapter.md: choose a parent book, then create a minimal chapter note
- book.md: manual fallback when Media DB cannot create a useful book entry
- reference.md: manually created external reference
- daily.md: minimal daily note
- area.md: navigation/dashboard page

Normal book/movie/series creation should use Media DB. YouTube and Reddit notes are automated and do not need manual templates.

Insert policy:
- insert-image.md: reference an image that already exists in the Vault. It searches indexed images, shows the containing folder, inserts the full Vault-relative path, then optionally adds a caption. It never renames or moves the underlying file.
- insert-claim.md: Claim / Evidence with cursor stops.
- insert-question.md: question callout with a cursor stop.

Image ownership policy:
- Keep source-derived images where their source/project already owns them. A deep path such as library/books/<book>/<chapter>/figures_manual is valid and does not need to be flattened into one global images folder.
- New screenshots / clipboard images are import-time assets: name them when pasted and choose the owning project/source directory then.
- External/symlinked research images are renamed and organized outside Obsidian; Obsidian and Neovim only reference them.
- Store an image at the lowest shared scope that owns it: chapter-specific images beside that chapter, book-wide images at book scope, and project-wide images in that project directory.
- Do not symlink the whole ~/knowledge directory into the Vault when the Vault itself lives under ~/knowledge, because that creates a recursive path. Instead expose only external roots such as ~/knowledge/library under _external/library.
- _external is local-machine state and is ignored by Git.
- Obsidian Templater and Neovim LuaSnip share the same Markdown output conventions, but they do not need to execute the same template files.
