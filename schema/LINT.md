# LINT.md — Knowledge Quality Gates

## Critical gates
- Missing required wiki artifacts.
- Missing/invalid task structure.
- Missing frontmatter.
- Unresolved wiki links.
- Missing memory and execution control docs.

## Major gates
- Duplicate canonical titles.
- Orphan canonical pages.
- Missing contradiction records when declared.

## Outputs
- `wiki/reports/wiki-health-report.md`
- Non-zero exit code when critical issues exist.
