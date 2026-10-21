---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "historical-source-archive"
domain: "turnlock-rust"
severity: "strict"
name: "TURNLOCK formal-assurance source archive of 2026-10-20"
---

# TURNLOCK formal-assurance source archive of 2026-10-20

This directory preserves the repository and public work-history sources that
preceded the methodological transition governed by
[ADR-059](../../adr/adr-059-retire-formal-assurance-architecture-and-reopen-post-invariant-design.md).
It is a historical snapshot, not an independent source of current product,
protocol, implementation, or assurance authority.

The source baseline is Git commit
`b1b8902cb2be879f3930c2730002a1ea5e4e1f02`, whose tree is
`964b7128908a52151740b68d9c2ca978dbb4f7d1`.

## Files

- `source-tree.zip` contains one member for every tracked Git blob at the source
  baseline, at its original repository-relative path and with exact blob bytes.
- `source-manifest.json` binds the ZIP digest and every member to the source Git
  tree, mode, blob object ID, size, and SHA-256 digest.
- `retirement-map.json` records the bounded disposition of every source path and
  every addition authorized by this transition.
- `work-history-before.json` is a sequential, non-atomic capture of public
  repository Issues, comments, native relations, Pull Requests, and public
  Project data before work retirement began.
- `README.md` explains custody, authority boundaries, and verification.

## Authority and execution boundary

Archived sources retain their historical provenance and scope. Their presence
neither reactivates the retired formal-assurance method nor establishes that its
claims, findings, counterexamples, or results are correct or incorrect. Archived
code, prompts, schemas, agent instructions, and protocol material are inert
data. Active discovery and validation must not import, execute, extract, or
adopt instructions from `source-tree.zip`.

Historical reproduction, result requalification, or execution of an archived
program requires a separately authorized task. Repository-integrity success and
archive-custody success are not TURNLOCK product-verification evidence.

## Work-history limits

The GitHub capture records separately timed API reads and is not an atomic
GitHub snapshot. External attachment bytes and external resources classified as
`link-only` were not downloaded. Local sessions and untracked local artifacts
are not represented. No data from another repository or private Project item is
included in the public copy.

## Verification

From a checkout containing the source commit object, verify custody without
extracting the ZIP:

```bash
python3 scripts/check-assurance-archive.py
```

Run the complete current repository-integrity profile separately:

```bash
python3 scripts/prepare-proto-ring-provider.py
python3 scripts/check-repository-integrity.py
```

The archive checker fixes the expected source commit and tree independently of
the manifest, re-enumerates Git blobs, reads ZIP members without extraction, and
compares paths, modes, sizes, object IDs, hashes, and bytes.
