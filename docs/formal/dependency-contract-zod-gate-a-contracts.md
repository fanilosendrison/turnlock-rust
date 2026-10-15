---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "dependency-contract"
workspace: "turnlock-rust"
date: "2026-10-15"
step_id: 2
id: DC-ZOD-GATE-A-CONTRACTS
version: "1.0.0"
dependency_version: "4.6.7"
scope: gate-a-campaign-runner/contracts/zod
status: active
consumers: [architect, coding-agent]
referenced_by: [NIB-M-GATE-A-CONTRACTS]
superseded_by: []
---

# Dependency Contract — Gate A M0 Zod Validation

Contract ID: `DC-ZOD-GATE-A-CONTRACTS`

Version: `1.0.0`

Status: `active`

## 0. Identity, status, authority, and scope

This Dependency Contract is implementation-construction dependency authority
for the M0 `contracts` module's use of Zod only.

It is consumed by:

```text
NIB-M-GATE-A-CONTRACTS 1.5.1
```

The contract selects exactly:

```text
package: zod
package version: 4.6.7
runtime floor: Node.js >= 22.19.0
consumer: M0 contracts
dependency role: strict runtime structural validation
```

Zod owns no TURNLOCK product meaning, hostile-review protocol meaning, semantic
identity, currentness, qualification, evidence, or repository authority. M0
owns the public validation result and every public issue classification.

This contract creates no production package manifest. The later authorized
implementation stage consumes this contract.

## 1. Exact package and version selection

The future production manifest must select exactly:

```json
{
  "dependencies": {
    "zod": "4.6.7"
  }
}
```

No range or alias is permitted. In particular, forbid:

```text
^4.6.7
~4.6.7
>=4.6.7
4.x
latest
*
```

Consume the package through its public root ESM export only:

```ts
import { z } from "zod";
```

Do not import package-internal files, `src/`, `v4/core`, or a private build
artifact. Do not substitute `zod/mini`, `zod/v3`, another Zod entry point, a
fork, or another validation library.

## 2. Package qualification and provenance

The exact npm registry distribution was inspected and executed in an isolated,
untracked qualification workspace.

```text
registry package: zod@4.6.7
registry tarball: https://registry.npmjs.org/zod/-/zod-4.6.7.tgz
packed size: 1,141,941 bytes
unpacked size: 6,148,944 bytes
file count: 840
SHA-1: e806cf64a7f4e37635ce9f2f52c04c3766f75e5b
SHA-512 hex:
83c5b60f6914e9af2e9ed734e777d7d6e5412b333bcaa0315bfdf3c24f37fba4
72176f9228eb95f9cd30043854c335753da19aa66647fab99c5333dffb7086c2
SRI:
sha512-g8W2D2kU6a8untc053fX1uVBKzM7yqAxW/3zwk83+6RyF2+SKOuV+c0wBDhUwzV1PaGapmZH+rmcUzPf+3CGwg==
```

The computed tarball SHA-1 and SHA-512 matched npm registry metadata exactly.
`npm audit signatures` under npm `10.9.3` verified the registry signature.

The registry SLSA provenance binds the package SHA-512 above to:

```text
upstream repository: https://github.com/colinhacks/zod
source commit: b500a2ee95134f81d74da7911d7378dd2853d042
release workflow: .github/workflows/release.yml
workflow invocation:
https://github.com/colinhacks/zod/actions/runs/38270975828/attempts/1
```

The upstream `v4.6.7` tag resolves to the same source commit.

The unpacked distribution declares:

```text
package type: module
root ESM import: ./index.js
root CommonJS entry: ./index.cjs
root TypeScript declarations: ./index.d.cts
package engines declaration: absent
```

The selected root ESM import executed successfully on Node.js `22.19.0`.
TypeScript `5.9.3` with strict checking, `module = NodeNext`, and
`moduleResolution = NodeNext` accepted the selected public declarations and
API. TypeScript `5.9.3` is qualification tooling only; this contract does not
select the future production TypeScript toolchain.

Relevant inspected distribution declarations and implementation artifacts were:

```text
package.json
index.js
index.d.cts
v4/classic/schemas.d.ts
v4/classic/parse.d.ts
v4/core/errors.d.ts
v4/core/parse.js
v4/core/schemas.js
```

## 3. Exact public dependency API consumed

The M0 adapter may consume only this public root-export surface:

```text
z.strictObject
z.string
z.number
z.boolean
z.null
z.literal
z.enum
z.array
z.tuple
z.union
z.discriminatedUnion
z.record
z.lazy
schema.optional
schema.nullable
stringSchema.regex
stringSchema.min
stringSchema.max
numberSchema.int
numberSchema.min
numberSchema.max
arraySchema.min
arraySchema.max
schema.safeParse
safeParse failure.error.issues
```

Use an optional or nullable schema only when the owning M0 representation
explicitly defines that field as optional or nullable. Use bounds, literals,
enums, regular expressions, unions, recursion, and collection shapes only to
encode an already-owned representation constraint.

The adapter may inspect these issue fields where the issue's discriminated code
provides them:

```text
code
path
keys
expected
values
format
minimum
maximum
errors
discriminator
options
```

Human-readable `message` and `note` are not consumed behavior.

Do not consume:

```text
parse or parseAsync
safeParseAsync
encode or decode APIs
Zod global configuration
private/internal schema definitions
private parser state
private issue constructors
```

The M0-specific `DUPLICATE`, `ORDER`, and `CROSS-FIELD` checks execute as
M0-owned pure checks after successful structural parsing. They do not require a
Zod refinement, transform, or custom issue.

## 4. Safe-parse interface

For a schema whose inferred output is `T`, the consumed dependency interface is
conceptually:

```ts
schema.safeParse(value: unknown):
  | {
      readonly success: true;
      readonly data: T;
    }
  | {
      readonly success: false;
      readonly error: {
        readonly issues: readonly ZodIssue[];
      };
    };
```

The exact dependency declarations name the result
`ZodSafeParseResult<output<this>>`. The type names above remain internal to the
adapter and never cross M0's public boundary.

For ordinary supported data representations, a structural mismatch returns
`success: false`; it does not require exception-based control flow.

A successful parse may return newly allocated objects and arrays. Object
identity preservation is not contracted. The adapter must preserve the accepted
representation's fields, primitive values, Unicode contents, nested values, and
semantic array ordering.

## 5. Exact validation pipeline

Implement exactly:

```text
unknown supported representation input
→ exact strict Zod structural validation
→ M0-owned representation constraints
→ M0-owned issue normalization
→ ContractValidationResult<T>
```

For valid input, return exactly:

```ts
{
  kind: "valid",
  value: exactValidatedRepresentation
}
```

For invalid input, return exactly:

```ts
{
  kind: "invalid",
  issues: normalizedIssues
}
```

Do not mutate the input. Do not repair output. Do not normalize Unicode, path
text, identifier spelling, semantic values, or semantic array order.

If structural validation fails, normalize every applicable structural failure
reported by the exact schema. Run an M0-owned post-structural constraint only
after the structure required by that constraint has validated successfully.
Do not fabricate a cross-field, duplicate, or ordering issue when malformed
structure prevents that check from being evaluated.

## 6. Strict-object and non-transforming behavior

Construct every closed M0 contract object with exactly:

```ts
z.strictObject({
  // exact owning M0 fields
})
```

The qualified release reports unknown keys from `z.strictObject` with native
code `unrecognized_keys`. A single native issue may contain multiple exact
unknown keys and identifies the containing object through its native path.

Do not use `z.object(...)` for a closed contract object. In the qualified
release, ordinary `z.object(...)` accepts an unknown property and strips it from
the returned value. That behavior violates M0.

Forbid behavior equivalent to:

```text
z.coerce.*
.default(...)
.catch(...)
.transform(...)
object passthrough
loose object validation
unknown-property stripping
implicit repair
```

Qualification confirmed that coercion, default, catch, and transform APIs can
produce successful altered values. Their existence in the package does not
permit M0 to consume them.

## 7. Zod 4.6.7 issue behavior observed

The exact release produced these raw issue forms during executed qualification:

```text
absent required property
→ code = invalid_type
→ path = exact property path
→ expected = expected primitive/container

present property with value undefined
→ the same raw invalid_type form as absence

wrong primitive or container type
→ code = invalid_type
→ path = exact failing path

fractional number under numberSchema.int
→ code = invalid_type
→ expected = int
→ format = safeint

NaN or infinite number
→ code = invalid_type
→ expected = number
→ received identifies the non-finite representation

strict-object unknown properties
→ code = unrecognized_keys
→ path = containing object path
→ keys = exact unknown property names

regex failure
→ code = invalid_format
→ format = regex

literal or enum mismatch
→ code = invalid_value
→ values = accepted literal values

numeric lower bound
→ code = too_small
→ minimum = selected lower bound

numeric upper bound
→ code = too_big
→ maximum = selected upper bound

nested array failure
→ path contains canonical numeric array indices

general union failure
→ code = invalid_union
→ errors contains per-branch issue arrays

discriminated-union discriminator mismatch
→ code = invalid_union
→ path identifies the discriminator
→ discriminator and options identify the structural discriminator contract
```

These are dependency observations, not public M0 classifications. Native issue
ordering, native issue grouping, native human-readable messages, and native
codes are not M0 authority.

## 8. M0 public result boundary

M0 owns exactly:

```ts
interface ContractValidationIssueV1 {
  readonly path: string;
  readonly code:
    | "TYPE"
    | "REQUIRED"
    | "UNEXPECTED-PROPERTY"
    | "FORMAT"
    | "ENUM"
    | "RANGE"
    | "DUPLICATE"
    | "ORDER"
    | "CROSS-FIELD"
    | "UNSUPPORTED-VERSION";
}

type ContractValidationResult<T> =
  | {
      readonly kind: "valid";
      readonly value: T;
    }
  | {
      readonly kind: "invalid";
      readonly issues: readonly ContractValidationIssueV1[];
    };
```

Never expose through that boundary:

```text
ZodError
ZodIssue
Zod schema
Zod safe-parse result
Zod-native code
Zod-native path
Zod human-readable message
Zod exception
```

A Zod result establishes only representation validity for the exact runner-owned
shape being checked.

## 9. Deterministic issue normalization

Normalize failures through an M0-owned adapter. Do not return a dependency issue
directly.

For every invalid result:

1. Map each applicable violation from the owning M0 representation contract.
2. Expand each `unrecognized_keys` member into one public issue at the exact
   unknown-property pointer.
3. Convert paths to RFC 6901.
4. Suppress duplicate `(path, code)` pairs.
5. Sort by unsigned UTF-8 bytes of `path`, ascending.
6. Break equal-path ties by ASCII bytes of `code`, ascending.
7. Require at least one public issue.

Do not rely on JavaScript UTF-16 lexical ordering, object enumeration ordering,
Zod issue ordering, or the order of `unrecognized_keys.keys`.

Use exact byte comparison for final sorting. No locale-aware comparison is
permitted.

## 10. Public error classification

Apply exactly:

```text
missing required own property
→ REQUIRED

required own property present with wrong primitive/container type
→ TYPE

unknown closed-object property
→ UNEXPECTED-PROPERTY

lexical, regex, or exact representation failure
→ FORMAT

invalid closed enum or literal
→ ENUM

invalid supported-version discriminator
→ UNSUPPORTED-VERSION

numeric bound violation
→ RANGE

duplicate member where the owning contract requires uniqueness
→ DUPLICATE

canonical ordering violation fixed by the owning contract
→ ORDER

exact multi-field consistency violation fixed by the owning contract
→ CROSS-FIELD
```

Map from the violated M0 contract, not from the native code alone. In
particular:

```text
invalid_type
→ REQUIRED when the required own property is absent
→ TYPE when the supplied primitive or container kind is wrong
→ FORMAT when the supplied numeric primitive violates an exact finite/integer
  representation contract

invalid_value
→ ENUM or UNSUPPORTED-VERSION according to the exact field contract

too_small / too_big
→ RANGE when the exact M0 violation is a selected numeric value or safe-integer
  bound
→ FORMAT when the exact M0 violation is a string, array, or tuple
  representation-cardinality constraint

invalid_union
→ recursively inspect branch issues where present, then classify through the
  exact M0 union/discriminator contract
```

Never classify by regex-matching `message` or `note`.

A Zod issue code not covered by the exact statically constructed M0 schema and
this adapter is an implementation/dependency-contract failure. Do not guess a
public code.

### 10.1 Missing versus present `undefined`

Zod `4.6.7` reports absent required fields and explicitly present `undefined`
with the same raw `invalid_type` issue. Zod alone cannot implement the required
public distinction.

M0 must examine own-property presence in the original ordinary data
representation:

```text
required own property absent
→ REQUIRED

required own property present with value undefined
→ TYPE
```

This does not add a default. Serialized M0 representations do not admit
`undefined` as a valid field value. Do not infer absence from `value ===
undefined`.

If a parent container is absent, report the applicable missing parent property.
If the parent is present with the wrong container type, report `TYPE` at that
parent. Do not fabricate inaccessible child-property issues.

## 11. Nested paths and RFC 6901

Render the root path as:

```text
""
```

For every token:

```text
~ → ~0
/ → ~1
```

Render an array index as canonical non-negative decimal with no sign, leading
zero, decimal point, or exponent.

Examples:

```text
native path ["members", 0, "value"]
→ /members/0/value

unknown root key "~/"
→ /~0~1
```

For `unrecognized_keys` at native containing path `P` with keys `K1..Kn`, emit
one public issue for every exact `P + Ki`. Never emit only the containing-object
pointer.

The selected statically constructed M0 schemas produce only string object-key
and non-negative numeric array-index path tokens. Do not invent handling for a
symbol path token.

## 12. Conditional, union, and cross-field boundaries

Use Zod unions or discriminated unions only for exact structural alternatives
already declared by M0. A matching structural branch creates no semantic truth.

For an invalid discriminator, use the statically known M0 discriminator field
and accepted literals to classify the violated field. Do not derive the
classification from the human message.

Run these constraints only as M0-owned post-structural checks:

```text
duplicate freedom
canonical ordering
exact cross-field equality or consistency
unsupported-version classification where the field contract distinguishes it
```

Emit `DUPLICATE`, `ORDER`, `CROSS-FIELD`, or `UNSUPPORTED-VERSION` only when the
active NIB-S/NIB-M authority already defines that exact constraint. Do not add a
constraint to make the public issue taxonomy exhaustive.

A post-structural check must preserve all accepted values and ordering. It may
only add public issues; it may not rewrite the validated value.

## 13. Runtime integration and lifecycle

Construct each schema statically inside M0. Do not read schema definitions from
the filesystem or generate them from protocol artifacts at runtime.

Use synchronous `safeParse` only. Select no asynchronous refinement or
validation branch.

The adapter performs no:

```text
I/O
repository access
Python invocation
state mutation
provider invocation
time access
randomness
logging of raw untrusted values
```

No Zod global configuration or locale-specific message behavior may influence
the public result. Human-readable dependency messages are ignored.

The qualified package declares no `engines` field. Executed qualification at
the selected Node.js floor `22.19.0`, successful ESM loading, and successful
safe parsing establish compatibility for the selected runtime boundary. The
absence of a package engine declaration does not lower TURNLOCK's runtime floor.

Any Zod version change requires a new accepted Dependency Contract version and
requalification before implementation adoption.

## 14. Error handling and prohibited dependency leakage

A normal structural mismatch is data, not an exception:

```text
safeParse success = false
→ normalize issues
→ ContractValidationResult invalid
```

For the supported ordinary serialized-representation domain, malformed values
must not require exception-based control flow.

An unexpected dependency exception is not a contract-invalid data result. It is
an M0 implementation/process failure under the existing M0 failure taxonomy.
It must not be exposed as `ZodError`, converted to a guessed public issue, or
used to authorize retry, blocker materialization, semantic fallback, or data
repair.

Never log or persist a Zod error object as authoritative evidence. Never include
raw untrusted values merely to reproduce a dependency message.

## 15. Behavioral conformance matrix

The qualification harness executed the exact release under Node.js `22.19.0`.
The temporary harness established dependency behavior and adapter feasibility;
it is not production implementation and does not replace future NIB-T.

| Case | Raw Zod 4.6.7 observation | M0 adapter result exercised | Qualification |
| ---- | ------------------------- | --------------------------- | ------------- |
| Missing required property | `invalid_type` at property path | `REQUIRED` after own-property check | PASS |
| Present `undefined` | same raw issue as absence | `TYPE` after own-property check | PASS |
| Incorrect primitive type | `invalid_type` | `TYPE` | PASS |
| Incorrect container type | `invalid_type` | `TYPE` | PASS |
| Multiple unknown properties | one grouped `unrecognized_keys` issue | one issue per exact property | PASS |
| Nested unknown property | containing nested path plus exact key | full unknown-property pointer | PASS |
| Invalid string format | `invalid_format`, format `regex` | `FORMAT` | PASS |
| Invalid enum/literal | `invalid_value` | `ENUM` from field contract | PASS |
| Invalid version discriminator | `invalid_value` | `UNSUPPORTED-VERSION` from field contract | PASS |
| Numeric lower bound | `too_small` | `RANGE` | PASS |
| Numeric upper bound | `too_big` | `RANGE` | PASS |
| Fractional number | `invalid_type`, expected `int` | `FORMAT` from representation contract | PASS |
| NaN or infinity | `invalid_type`, expected `number` | `FORMAT` from representation contract | PASS |
| Nested array path | native string/number path tokens | canonical RFC 6901 pointer | PASS |
| JSON Pointer escaping | unknown key `~/` retained | `/~0~1` | PASS |
| Duplicate constrained member | structurally valid | M0 `DUPLICATE` check | PASS |
| Invalid canonical ordering | structurally valid | M0 `ORDER` check | PASS |
| Cross-field violation | structurally valid | M0 `CROSS-FIELD` check | PASS |
| Duplicate normalized issues | not dependency-owned | exact pair deduplication | PASS |
| Deterministic sorting | native order ignored | UTF-8 path then ASCII code | PASS |
| Valid strict object | successful deep-equal output | values, Unicode, and arrays preserved | PASS |
| Unknown-key stripping control | ordinary `z.object` stripped the key | selected `z.strictObject` rejected it | PASS |
| Coercion/repair controls | prohibited APIs altered successful output | APIs excluded from consumer surface | PASS |

The valid parse returned different object and array identities while preserving
all tested values and ordering. The contract therefore makes no object-identity
claim.

## 16. Security and input-domain limitations

The non-throwing qualification covers ordinary runner-owned serialized data
representations:

```text
null
booleans
strings
numbers
arrays of supported data values
ordinary accessor-free objects whose traversed properties are data values
```

This is the M0 serialized-representation boundary. It is not a universal safety
claim for every ECMAScript metaobject.

Executed negative qualification established:

```text
throwing accessor
→ Zod property traversal propagated the accessor exception

Proxy with throwing ownKeys trap
→ Zod reflection propagated the Proxy exception
```

Therefore:

```text
safeParse is not universally non-throwing for arbitrary accessors or Proxies
```

Do not claim otherwise. Accessors, hostile Proxies, and host objects with
throwing reflection are outside the qualified serialized-representation input
domain. A future boundary that intentionally accepts such values requires a new
construction decision and dependency qualification; it must not silently widen
this contract.

Zod does not establish resource-exhaustion safety for adversarial depth, width,
or regular-expression workload. This contract introduces no size limit that is
absent from M0. Future NIB-T must exercise accepted practical bounds without
inventing a product limit.

## 17. Consumer constraints and authority exclusions

M0 must not use Zod to establish:

```text
hostile-review protocol validity
protocol bundle validity
review evidence validity
current semantic subject S
current protocol P
SemanticAdmission existence or consumability
SemanticFact truth
QLEK reconstruction
FactId reconstruction
qualification truth
CandidateView truth
repository authority
formal-assurance readiness
```

Published protocol schemas, the Python checker, M2, M5, and M6 retain their
existing responsibilities.

Do not translate a published protocol schema into Zod and then treat Zod success
as equivalent authority. A runner-side structural mirror remains a mirror.

Zod success never authorizes mutation, dispatch, retry, repair, publication,
blocker creation, Decision Request creation, or protocol activation.

## 18. NIB-S and NIB-M interaction

NIB-S `13.0.1` selects Zod as M0's construction support dependency.
NIB-M-GATE-A-CONTRACTS `1.5.1` owns:

```text
public result types
all runner-owned representation contracts
schema meaning
canonical runner JSON
identity derivation
public issue classification
normalization and ordering
M0 failure taxonomy
authority exclusions
```

This Dependency Contract owns only the exact external package interface and
observed behavior consumed to realize those requirements.

P6 remains current. P7 remains permanently inactive. P8 remains inactive until
C15. This contract does not activate a protocol or change a protocol bundle,
schema, review record, formal result, ADR, specification, or formal-assurance
manifest.

## 19. Required future NIB-T obligations

C10/NIB-T has not begun. The future NIB-T must require executable tests for at
least:

```text
exact package version and selected public import
missing required own property
present required property with undefined
incorrect primitive type
incorrect container type
single and multiple unknown properties
nested unknown property
invalid string format
invalid enum/literal
invalid version discriminator
numeric lower and upper bounds
fractional, NaN, infinite, and unsafe-integer representations
string/array/tuple representation-cardinality classification
nested array pointer
RFC 6901 root, tilde, solidus, and array-index rendering
one issue per unknown property
duplicate constrained member
canonical ordering violation
cross-field violation
duplicate normalized issue suppression
unsigned UTF-8 path ordering
ASCII code tie ordering
non-empty invalid issue list
valid object value/field/Unicode/array-order preservation
no coercion, default, catch, transform, passthrough, or stripping
no input mutation
no Zod-native public leakage
ordinary malformed supported input remains non-throwing
throwing accessor and Proxy limitation remains explicit and does not become a
  false universal safeParse guarantee
protocol/Python/M2/M5/M6 authority remains unchanged
```

These are future test obligations, not tests claimed to exist in this stage.
The qualification harness does not satisfy RED or production conformance.

## 20. Acceptance criteria and qualification verdict

The contract acceptance assessment is:

```text
exact zod@4.6.7 package available: PASS
registry artifact integrity: PASS
registry signature: PASS
SLSA source provenance: PASS
public root ESM API: PASS
strict TypeScript declarations: PASS
Node.js 22.19.0 execution: PASS
safeParse on supported representation data: PASS
strict closed-object behavior: PASS
raw issue representation: PASS
M0 normalization feasibility: PASS
public dependency leakage prohibition: PASS
authority preservation: PASS
universal arbitrary-JavaScript non-throwing claim: NOT CLAIMED
```

Exact qualification verdict:

```text
DEPENDENCY_QUALIFICATION=PASS
CONTRACT_COMPLETENESS=PASS
SUPPORTED_INPUT_DOMAIN=ORDINARY-SERIALIZED-DATA-REPRESENTATIONS
EXOTIC_ACCESSOR_PROXY_UNIVERSAL_SAFETY=NOT-QUALIFIED
```

The explicit exotic-input limitation does not weaken M0's accepted serialized
representation contract and creates no normative product impact. If a future
consumer requires arbitrary accessor or Proxy acceptance, this contract no
longer qualifies that widened boundary and implementation must stop pending a
new accepted construction decision.
