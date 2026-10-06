---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "research-index"
domain: "turnlock-competitive-watch"
severity: "guideline"
name: "Competitive Guarantee Watch"
---

# Competitive Guarantee Watch

The Competitive Guarantee Watch is TURNLOCK's dated, evidence-based research
archive for comparing technical responsibilities and guarantees relevant to
[TURNLOCK and the possible Turnlock Cloud product](../../product/positioning.md).
It supports public positioning with cumulative observations while keeping
research separate from product authority.

No competitor assessment is established merely by installing this directory.
The initial watchlist contains discovery seeds, not verified competitor ratings.
Grouped seed labels do not establish legal ownership, affiliation, or technical
identity; those relationships require verification in a real report.

## Authority boundary

This directory defines operational rules for competitive research. Those rules
are authoritative only for how the watch is conducted and reported. They do not
create TURNLOCK Product Intent, TURNLOCK or Turnlock Cloud requirements, product
architecture, or premises for specification derivation. Competitive evidence
may motivate a question, but it cannot silently alter governed product meaning.

Product positioning explains the intended distinctions without naming or rating
alternatives. Named observations belong only in immutable, dated reports whose
scope and evidence are explicit.

## Contents

- [Methodology](methodology.md) defines research questions, permanent radar
  membership, discovery, implementation analysis, ratings, evidence, and
  historical interpretation.
- [Execution](execution.md) defines cadence expectations, coverage operations,
  GitHub publication, additive chat delivery, and failure handling without
  creating a scheduler.
- [Watchlist](watchlist.json) initializes discovery seeds and membership policy;
  it is not the complete historical roster and contains no current scores.
- [Report schema](report.schema.json) defines the structural JSON contract for
  new reports.
- [Report template](report-template.md) defines the French-readable Markdown
  projection of the same report data.

## Archive structure

Every future report occupies a new directory:

```text
docs/research/competitive-watch/reports/YYYY/
  TCW-YYYYMMDDTHHMMSSZ/
    report.json
    report.md
```

Published report directories are immutable and append-only. Corrections are new
reports that reference the reports and findings they correct. No rolling report
is overwritten, and weekly reports do not replace daily reports.

`report.json` is the source representation of one report. `report.md` is a
human-readable projection of the same content; it must not add ratings,
judgments, or evidence absent from the JSON. A future index may be generated
from report history, but no report or index exists merely because this framework
has been installed.

## Four comparison dimensions

The watch evaluates four dimensions independently:

1. **TURNLOCK Core guarantees** — the extent to which the examined scope
   preserves the accepted workflow-control, execution-form, composition,
   binding, inspectability, provenance, and composability guarantees.
2. **Managed execution** — the extent to which it supplies compatible
   isolation, workspace materialization, environment lifecycle, effects, and
   elastic execution resources.
3. **Run signal / reproducibility** — the extent to which it captures durable
   execution truth and supports explicitly scoped reproducibility or
   property-relative comparison claims while preserving unknowns.
4. **Evaluation / optimization downstream** — the extent to which available
   capabilities support valid regression judgment, variance treatment,
   refinement, promotion, routing, benchmarks, learning, assurance, or analysis.

There is no mandatory aggregate score. A component can be strong in one
dimension, depend on another provider in a second, and remain indeterminate in a
third or fourth.

## Permanent radar and discovery

The effective radar is cumulative and permanent. Once an identifiable actor,
product, or component has been evaluated, it remains represented for as long as
the watch operates unless an explicit user instruction stops active monitoring.
Stopping monitoring does not erase identity or history. Dormant, discontinued,
acquired, renamed, uncertain, complementary, and low-threat actors remain part
of the historical radar.

Every execution performs both accumulated-radar monitoring and open discovery
for new entrants. Discovery searches by problems and guarantees rather than
only by known names. Incomplete monitoring or discovery is reported as such; it
is never converted into a claim that nothing changed or no entrant exists.

## Technical depth

Public claims and documentation are starting evidence, not an automatic basis
for a guarantee conclusion. When a relevant conclusion depends on implementation
behavior and source is accessible, the watch follows the production path into
workflow and session control, binding and admission, persistence and capture,
error and unknown handling, execution and result attribution, comparison and
evaluation, and optimizer or promotion behavior where applicable. Code read,
tests read, tests executed, and verified proof remain separate evidence classes.

Closed, inaccessible, or incomplete code creates an evidence limitation, not a
negative capability finding. The actor remains on the radar and unfinished
technical questions remain persistent investigations.

## Human-readable delivery

Each execution is intended to deliver its complete readable report as a new
ordinary French-language chat message. The GitHub JSON/Markdown archive
complements that delivery and does not replace it. Corrections are also new
messages. A link-only notification, edited rolling canvas, or weekly summary
cannot substitute for the daily report.

The external scheduler and chat interface control execution, routing, display,
and retention. Repository files cannot activate or verify that scheduler,
force a message into a particular conversation, recover a deleted chat, or
impose platform retention policy.

This repository is configured with an archival contract. That is distinct from
having successfully tested recurring automatic archival. A future execution may
claim `ARCHIVED` only after the newly published files and their real reference
have been read back. Until such evidence exists, recurring repository
publication remains an untested operational dependency.
