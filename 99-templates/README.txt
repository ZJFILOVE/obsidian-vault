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

Insert templates are intentionally kept separate from creation templates. Their design should be shared with the Neovim snippet layer by output format, not by forcing both editors to execute the same template file.
