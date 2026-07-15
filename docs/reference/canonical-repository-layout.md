# Canonical repository layout

Echel stores product truth under `.echel/` at the root of the containing Git
repository. Discovery starts from any nested file or directory, resolves the Git
root, and checks only that root. It never walks above the repository looking for
unrelated Echel state.

```text
.echel/
  records/
    artifacts/ claims/ decisions/ relationships/ findings/ work/
    tasks/ runs/ evidence/ releases/ learnings/
  cache/
  backups/       # created only by an applied migration
  migrations/    # present only while migration recovery is required
```

Each canonical record collection contains one JSON record per file. `cache/` is
reserved for disposable, reconstructable state and is never canonical. Authored
artifacts, migration journals, project records, and policy records are introduced
only by the tasks that define their behavior; initialization does not create
placeholder content for future lifecycle stages.

Migration backup and journal directories are created lazily. They are operational
recovery state, not canonical records, and can never authorize knowledge.

`CanonicalRepository.create(path)` requires the actual Git root and constructs
the layout through a temporary sibling directory so a failed operation does not
leave a partial `.echel/`. `CanonicalRepository.discover(path)` supports normal
repositories and Git worktrees (`.git` may be a directory or file). Missing,
malformed, duplicate, and path-escape conditions return structured errors.

The repository layout defines location and discovery. [Canonical record writes](canonical-record-writes.md)
provide schema-validated preview and atomic single-record replacement; direct
filesystem writes are not an authorized alternative.
