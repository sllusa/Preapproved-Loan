# Pre-Approved Loan Journey (Ruralvía) — Spec Kit Bundle

## What this is
A GitHub Spec Kit (Spec-Driven Development) artifact bundle for the **digital contracting journey
of a pre-approved consumer loan** in **Ruralvía** (RSI / Grupo Caja Rural). It contains the
`/constitution`, `/specify`, `/plan`, and `/tasks` artifacts — produced directly from the RSI /
Ruralvía functional specification with no Spec Kit CLI dependency.

**Scope:** a **Single UC Happy Path** at **MVP** tier covering the end-to-end origination thread —
offer discovery → simulation → summary/account → precontractual → verification → SCA → idempotent
disbursement → confirmation — realized as synthesized agents (AGT-01–AGT-07) orchestrated over the
loan lifecycle, with all external systems mocked and a React front end over a Python agent/orchestration back end.

**Non-negotiable trait carried through every artifact:** the journey is *built once and
parameterized per entity* ("build once, deploy to many") so it can be rolled out across the ~30
credit unions of Grupo Caja Rural on the common Ruralvía channel and the common IRIS core — brand,
product catalog (amounts, terms, TIN, fees, relationship bonus), legal text templates, and locale
enter through per-entity configuration, never through forked code.

## Bundle contents & where the files go
Drop these onto a Spec Kit repo layout:
```text
memory/constitution.md
specs/001-prestamo-preconcedido/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── tasks.md
└── contracts/interfaces.md
```
In this working folder the files are kept **flat** (no `memory/` or `specs/…` nesting) and
`interfaces.md` sits at the top level; the tree above is the destination layout when you drop them
onto a Spec Kit repo. If you run `specify init`, copy these over the generated skeleton.

Supporting context documents (the source material the artifacts were derived from — **not** Spec
Kit artifacts) also live in this folder:
- `Funcional_Prestamos_Preconcedidos_Ruralvia.md` — the functional specification (the blueprint).
- `Contexto_Idiosincrasia_Ruralvia_Multientidad.md` — the multi-entity / IRIS platform reality.
- `Proceso_Actual_Preconcedidos_Ruralvia_AsIs.md` — best-effort as-is reconstruction.
- `Marco_Legal_Lending_UE_Espana.md` — the EU/Spain lending legal framework.
- `Ruralvia-*-Schema.jsonld`, `CTTI-Command-Center-Schema.jsonld` — ontology / context schemas.

## What's next
This bundle stops before `/implement` by design — writing code and file layout is the coding
agent's job. `tasks.md` is already generated (an ID-based, capability-level backlog referencing
work by `AGT-XX` / `MCP-TXX` / `BR-NN` / `FV-NN`, never file paths), so you can hand the bundle to
any coding agent (Claude Code, Cursor, IBM Bob, Cline) and continue straight to **`/implement`**.
Start with the P1 user story (Phase 3) for the MVP slice.

## Open decisions to revisit (see `research.md` and `spec.md` Assumptions)
- **Offer expiry/revocation mid-flow** — defaulted to *stop at the current step and mark the offer
  terminal* (no grace window); confirm the grace policy with RSI.
- **Multiple live offers per customer** — defaulted to *use the single most recent live offer* (no
  picker); confirm the prioritization rule with RSI.
- **Product parameters and per-entity configuration** (amounts, terms, TIN/TAE, fees, relationship
  bonus, legal texts, locales) are reference values to be confirmed against the real RSI / Grupo
  Caja Rural catalog per entity.
- **Legal baseline** — Ley 16/2011 today, with **CCD2 (Directive (UE) 2023/2225)** applying from
  **20-Nov-2026**; confirm the Spanish transposition timeline with RSI (see `Marco_Legal_Lending_UE_Espana.md`).

## Attribution
The artifact shapes and lifecycle are derived from [GitHub Spec Kit](https://github.com/github/spec-kit),
MIT-licensed. Vendored template shapes (spec, plan, tasks) are used under the MIT License, © GitHub.
This bundle adapts them for the RSI / Ruralvía blueprint (Technical Context provenance,
tier-conditional reliability, ID-based tasks with no file paths).
