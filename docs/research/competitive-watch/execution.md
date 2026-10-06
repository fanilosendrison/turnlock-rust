---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "research-operations"
domain: "turnlock-competitive-watch"
severity: "strict"
name: "Competitive Guarantee Watch Execution"
---

# Competitive Guarantee Watch Execution

This document defines watch operations and their limits. It does not create,
activate, modify, or verify a scheduler.

## Agreed cadence

The intended external cadence is:

- a daily run in the morning, around 08:00 Europe/Paris;
- a weekly synthesis on Monday, using the same report format; and
- a monthly trajectories section in the weekly report produced on the first
  Monday of each month.

There is no claim of instantaneous monitoring. The external scheduling task is
named **“Veille Turnlock et Turnlock Cloud”**. Its actual calendar, execution,
retries, and availability belong to the external scheduler. This mandate neither
creates nor changes that task, and the presence of this file does not show that
the schedule has run.

## No-forgetting and coverage operations

Every run must:

1. reconstruct the complete effective radar from the seed list, all prior
   report admissions, explicit user additions, and recoverable pending entries;
2. read cursors actually preserved by successful archives;
3. perform both accumulated-radar monitoring and open discovery;
4. deepen relevant changes and persistent investigations; and
5. produce a new report even when no significant change is found.

Coverage targets are:

- refresh sources for every active or not-yet-classified actor at least every
  7 days; and
- check lifecycle, successors, forks, and transferred technology for every
  confirmed dormant or discontinued actor at least every 30 days.

These are coverage targets, never expiration periods. Overdue work is processed
without allowing a low-threat actor to be deferred indefinitely in favor of
more visible actors.

A scan that did not occur remains `not_checked` or `overdue`. Its observation
date, last successful cursor, and existing due date must not advance. A source
cursor may be a commit SHA, date, or opaque provider reference; `reason`
explains its meaning when it is not self-evident. Capacity limits are reported
and do not justify removing any actor from the radar.

## GitHub publication

Before publication:

1. validate `report.json` structurally;
2. verify references, dates, semantic constraints, and radar continuity;
3. render `report.md` from the same data;
4. apply the repository's actual private-worktree, review, validation, and
   publication workflow; and
5. prove that no previous report changed.

Publication is exclusively into a new report directory:

```text
docs/research/competitive-watch/reports/YYYY/
  TCW-YYYYMMDDTHHMMSSZ/
    report.json
    report.md
```

An ordinary watch run must never edit TURNLOCK Product Intent, accepted ADRs,
either product rationale, product positioning, future-consideration vision
documents, or the competitive-watch methodology.

Announce `ARCHIVED` only after reading the real published files back from their
published reference. If archival fails:

- preserve produced material;
- announce `ARCHIVE_PENDING`;
- identify the intended destination and exact blocker; and
- do not advance a cursor as though archival succeeded.

A report cannot know in advance the commit SHA that will publish it. The
publication receipt remains outside the immutable report. Never amend a report
after publication merely to insert its own commit identifier.

Repository configuration and successful automated archival are different
claims. Recurring publication remains untested until a real execution produces,
publishes, and reads back a report through the external operating chain.

## Additive chat delivery

Every execution delivers a **new ordinary message** containing the complete
readable French report. Its title is:

```text
Veille Turnlock / Turnlock Cloud — Rapport du <date et heure Europe/Paris>
```

The message then provides `report_id`, observation window, report kind, report
content, sources, and coverage.

Never:

- replace a previous message;
- maintain one editable canvas or block as the sole result;
- deliver only a link, notification, or “report updated” statement; or
- replace daily reports with the weekly synthesis.

A correction is a new message that identifies the corrected report. Archived
JSON and Markdown complement chat readability; they do not replace it. An
archival failure does not cancel delivery of the readable report.

When a platform length limit prevents full display, the new message preserves
essential conclusions and evidence, identifies exactly what was omitted, and
attaches the complete report only if that file was actually produced. It must
not claim that omitted content was displayed.

Reference prior messages by links only when real links are available. Otherwise
use their dates and `report_id` values without inventing a chat URL.

The scheduler and chat interface control message routing and retention. The
repository cannot guarantee display in a particular thread, recover a deleted
chat, or impose a retention policy on the platform.

## First report and unavailable history

The first real report independently verifies a baseline from primary sources.
Its coverage may be partial but must be described precisely. It must not archive
old chat analyses as though their evidence had been reproduced and verified.

If expected historical roster information cannot be recovered, the report must:

- declare `ROSTER_HISTORY_INCOMPLETE`;
- preserve every actor that can be recovered;
- expose the limits; and
- avoid claiming verified continuity.

No empty report, invented assessment, or pre-populated score is created to make
the framework appear operational.
