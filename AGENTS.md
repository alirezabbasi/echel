# Echel agent instructions

Echel is a progressive SDLC memory system, not a documentation generator.

- Keep the canonical model small: knowledge, work, runs, evidence, and findings.
- Never make generated views authoritative.
- Add structure only when a demonstrated workflow requires it.
- Keep the agent runtime behind `AgentRuntime`; do not import Hermes internals into the domain.
- Persistent product-memory changes must be explicit and reviewable.
- Prefer sparse, justified relationships over inferred graph density.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` before completing changes.
