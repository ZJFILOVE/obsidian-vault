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
- insert-image.md: reference an image that already exists in the Vault. It searches indexed images, lets you choose one, then optionally adds a caption. It never renames or moves the underlying file.
- insert-claim.md: Claim / Evidence with cursor stops.
- insert-question.md: question callout with a cursor stop.

Image ownership policy:
- New screenshots / clipboard images are import-time assets: name them when pasted and choose their destination then. This is attachment management, not an insert-template job.
- Images living under an external/symlinked research directory are owned by that external directory. Rename and organize them outside Obsidian; Obsidian and Neovim only reference them.
- Obsidian Templater and Neovim LuaSnip share the same Markdown output conventions, but they do not need to execute the same template files.
