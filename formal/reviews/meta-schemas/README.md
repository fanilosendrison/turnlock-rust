# Immutable hostile-review meta-schemas

This directory contains immutable content-addressed schemas used to interpret
hostile-review protocol and evidence artifacts.

The Python traceability checker is the finite selector and mechanical root of
trust: it selects the meta-schema appropriate to a protocol-bundle schema
version. No schema registry, registry schema, meta-meta-schema, or recursive
schema-of-schema chain exists.

Published files in this directory are append-only. Once published, a
meta-schema is never edited, never replaced at its path, and never deleted.

`review-evidence-v5.schema.json` is the immutable initial review-evidence
meta-schema. It is a byte-for-byte snapshot of the schema-5.0 review-evidence
contract frozen at the same time as the unversioned legacy alias one directory
above.

`review-protocol-bundle-v1-v3.schema.json` preserves the historical validation
semantics for protocol-bundle schema versions 1, 2, and 3.

`review-protocol-bundle-v4.schema.json` defines protocol-bundle schema version
4, which requires an exact top-level `meta_schemas` object binding the exact
protocol-bundle meta-schema and the exact review-evidence meta-schema.

Future schema changes create new files at new paths and require a new protocol
identity. A future review-evidence schema change creates a new immutable
review-evidence meta-schema path plus a protocol bundle that binds that exact
artifact. `review-evidence-v5.schema.json` is never overwritten.

The unversioned files one directory above remain in the repository as frozen
historical aliases for historical links. They are not the active validation
authority, and the checker never consults them as mutable meta-schemas.
