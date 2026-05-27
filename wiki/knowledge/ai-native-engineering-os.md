---
type: system
status: active
---
# AI-Native Engineering OS

A platform model where persistent project intelligence lets domain experts and AI agents build software together across long-running, context-limited development sessions.

## Purpose

Echel is not only an AI-maintained wiki or a task runner. It is an orchestration layer for AI-native software development:

- domain experts guide requirements, intent, constraints, and product direction
- AI agents perform structured execution and implementation work
- Echel preserves project memory, relationships, decisions, and execution state
- quality gates and evidence keep accumulated knowledge trustworthy

## Core Problem

AI coding agents are constrained by token and context windows. Without durable memory, important decisions, architectural relationships, product intent, and lessons learned disappear between sessions.

Echel addresses this by continuously organizing development knowledge into a persistent project memory that can be reloaded, queried, linked, and evolved.

## Operating Boundary

- `wiki/` owns durable project intelligence and relationship modeling.
- `docs/development/` owns SDLC procedure, execution controls, gates, and operational snapshots.
- automation connects the two layers and keeps them synchronized.

The system should avoid repeating the same procedural concepts in both layers. Durable meaning belongs in the wiki; repeatable operating instructions belong in development docs.
