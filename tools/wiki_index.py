#!/usr/bin/env python3
from pathlib import Path
from echel_paths import configured_root

wiki = configured_root("WIKI_ROOT", "wiki")
sections: dict[str, list[tuple[str, str]]] = {}

for p in sorted(wiki.rglob("*.md")):
    if p.name == "index.md":
        continue
    rel = p.relative_to(wiki)
    folder = rel.parts[0] if len(rel.parts) > 1 else "root"
    title = p.stem.replace("-", " ").title()
    sections.setdefault(folder, []).append((rel.as_posix(), title))

out = ["---", "type: index", "status: active", "---", "", "# Index", ""]
for folder in sorted(sections):
    out += [f"## {folder.title()}", ""]
    out += [f"- [[{rel[:-3]}|{title}]]" for rel, title in sections[folder]]
    out += [""]

(wiki / "index.md").write_text("\n".join(out), encoding="utf-8")
print("Updated wiki/index.md")
