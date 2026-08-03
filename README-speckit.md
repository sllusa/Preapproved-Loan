# Supplier Selection & Contracts — Spec Kit Bundle

## What this is
A GitHub Spec Kit (Spec-Driven Development) artifact bundle generated from an EAEF Layer 2 blueprint for **Supplier Selection & Contracts** (APQC PCF 4.2.3). It contains the `/constitution`, `/specify`, `/plan`, and `/tasks` artifacts — produced directly from the blueprint with no Spec Kit CLI dependency. Scope: a **Single UC Happy Path** at **MVP** tier covering the sourcing-to-award thread (agents AGN1–AGN5), with all external systems mocked and a CLI + file-based review queue.

## Where the files go
Drop these onto a Spec Kit repo layout:
```text
memory/constitution.md
specs/001-supplier-selection-contracts/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── tasks.md
└── contracts/interfaces.md
```
If you run `specify init`, copy these over the generated skeleton. `memory/` and `specs/001-supplier-selection-contracts/` map straight onto the Spec Kit layout.

## What's next
This bundle stops before `/implement` by design — writing code and file layout is the coding agent's job. `tasks.md` is already generated (an ID-based, capability-level backlog), so you can hand the bundle to any coding agent (Claude Code, Cursor, IBM Bob, Cline) and continue straight to **`/implement`**. Start with the P1 user story (Phase 3) for the MVP slice.

One open decision to revisit: the `[NEEDS CLARIFICATION]` marker in `spec.md` on the negotiation-strategy downstream consumer (defaulted to an advisory `strategy_ready` terminal state — see `research.md`).

## Attribution
The artifact shapes and lifecycle are derived from [GitHub Spec Kit](https://github.com/github/spec-kit), MIT-licensed. Vendored template shapes (spec, plan, tasks) are used under the MIT License, © GitHub. This bundle adapts them for EAEF blueprints (Technical Context provenance, tier-conditional reliability, ID-based tasks with no file paths).
