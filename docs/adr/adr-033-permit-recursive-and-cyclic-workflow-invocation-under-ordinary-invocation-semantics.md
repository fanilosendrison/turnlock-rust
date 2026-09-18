---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Permit recursive and cyclic workflow invocation under ordinary invocation semantics"
id: "ADR-033"
status: "accepted"
date: "2026-09-18"
decision_body_sha256: "bb58adf056f7509177bf607f39d646fa785c9e439f8204afe87c598461fb92db"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-008"
    - "ADR-022"
    - "ADR-023"
    - "ADR-027"
    - "ADR-028"
    - "ADR-029"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Permission for direct recursive and cyclic workflow invocation"
  - "Ordinary per-occurrence invocation semantics under recursive and cyclic composition"
  - "Per-occurrence governing-definition binding across recursive and cyclic invocation"
---

# ADR-033: Permit recursive and cyclic workflow invocation under ordinary invocation semantics

## Context

TURNLOCK already supports structured nested workflow invocation through both
main-agent-selected and workflow-declared invocation paths.

ADR-008 establishes nested invocation from a main-agent region and return to the
same main-agent caller. ADR-022 establishes workflow-declared invocation with
structured call/return semantics. ADR-023 distinguishes the immediate caller
context from its preserved return-bearing continuation.

Those decisions deliberately did not decide whether the workflow-definition
call graph may contain direct recursion or cycles.

ADR-027 subsequently established that every accepted invocation, including a
nested invocation, independently binds one governing workflow definition no
later than its own acceptance and keeps that definition stable for its lifetime.
A caller's governing definition does not transitively freeze definitions of
future callees.

The remaining product question is therefore whether an otherwise authorized and
admissible workflow invocation may target a workflow already represented among
its invocation ancestors.

Representative structures are:

```text
direct recursion:

A1
↓
invoke A
↓
A2
````

and:

```text
indirect recursion:

A1
↓
B1
↓
A2
```

and more generally:

```text
A1
↓
B1
↓
C1
↓
A2
```

GitHub Issue #23 records the explicit product-owner decision resolving that
question.

## Discovery classification

### B — recursive and cyclic workflow invocation is permitted

Existing authority deliberately left recursion and cyclic call graphs
unresolved.

The product decision is:

```text
TURNLOCK permits recursive workflow invocation
and cyclic workflow call graphs.
```

Direct recursion, mutual recursion, and longer cyclic call graphs are therefore
not prohibited merely because a workflow definition occurs more than once in the
ancestry of an invocation occurrence.

### A — each recursive or cyclic occurrence remains an ordinary distinct invocation

Once recursive/cyclic composition is permitted, existing invocation semantics
require every accepted occurrence to remain distinct.

Therefore:

```text
workflow identity may repeat
but
invocation identity does not collapse
```

For example:

```text
A1 != A2
```

even when `A1` and `A2` resolve to definitions associated with the same workflow
artifact.

### A — structured caller/continuation semantics remain unchanged

Recursive/cyclic composition creates no alternate return semantics.

Each accepted recursive/cyclic callee has an immediate caller, and normal
completion returns to that immediate caller according to the ordinary structured
invocation rules.

### A — governing-definition binding remains per invocation occurrence

ADR-027 already requires each accepted nested invocation to establish its own
governing definition at its own acceptance boundary.

Recursive/cyclic permission does not change that rule.

### A — recursion creates no authority or admissibility escape

Permission for recursive/cyclic topology is independent from authority to invoke
a workflow and independent from whether a particular invocation is admissible in
its current context.

A recursive edge does not create new authority, reset restrictions, or widen the
caller context.

## Decision

TURNLOCK permits direct recursive workflow invocation and cyclic workflow call
graphs.

Permission applies to otherwise ordinary TURNLOCK workflow invocation.

No separate recursive invocation primitive or recursive execution form is
introduced.

### Direct recursion

A workflow MAY invoke the same workflow again through an invocation path that is
otherwise authorized and admissible.

For example:

```text
invocation A1
↓
invoke A
↓
invocation A2
```

is permitted.

`A2` is a new invocation occurrence.

It is not a continuation, mutation, restart, replacement, or rebinding of
`A1`.

### Indirect recursion and cyclic call graphs

A workflow invocation chain MAY revisit a workflow already represented among its
ancestors.

For example:

```text
A1
↓
B1
↓
A2
```

and:

```text
A1
↓
B1
↓
C1
↓
A2
```

are permitted invocation structures.

The repeated workflow in the call graph does not collapse the corresponding
invocation occurrences into one invocation.

### A cycle in the call graph does not imply infinite concrete execution

A cyclic workflow-definition call graph is distinct from an infinite execution.

For example:

```text
implementation
↓
review
↓
if correction_required:
    invoke implementation
else:
    complete
```

contains a cyclic workflow relationship but a concrete execution may terminate
after any finite number of invocation occurrences.

Therefore:

```text
cyclic workflow call graph
!=
infinite execution
```

and:

```text
recursion permitted
!=
termination guaranteed
```

TURNLOCK neither requires recursive execution to continue indefinitely nor
guarantees that every recursive execution terminates.

### Every occurrence uses ordinary invocation semantics

Each accepted recursive or cyclic invocation occurrence has its own:

```text
immediate caller
preserved return-bearing continuation
acceptance boundary
governing workflow definition
invocation lifetime
```

The ordinary structured lifecycle applies:

```text
caller
↓
callee occurrence
↓
normal completion
↓
same immediate caller
```

A recursive/cyclic callee MUST NOT skip outward over its immediate caller merely
because the same workflow definition appears elsewhere in the ancestry.

For example:

```text
A1
↓
B1
↓
A2
```

returns, on normal completion, as:

```text
A2
↓
B1
↓
A1
```

according to the applicable caller-continuation semantics.

It does not return directly from `A2` to `A1`.

### Recursive invocation does not mutate an ancestor invocation

Accepting a recursive/cyclic invocation MUST NOT replace, rewrite, capture,
replan, or rebind any active ancestor invocation.

The relationship is composition:

```text
active caller
↓
new invocation occurrence
```

not mutation:

```text
active caller
→ different governing invocation
```

### Governing-definition binding remains per occurrence

ADR-027 applies independently to every recursive/cyclic invocation occurrence.

For example:

```text
artifact A = D1

accept A1
→ governingDefinition(A1) = D1

artifact A later changes:
D1 → D2

A1 later reaches an invocation of A
that is already authorized by A1's governing orchestration

accept A2
→ resolve A2 under the applicable workflow-resolution semantics
→ governingDefinition(A2) may be D2

A2 completes
→ return to A1

A1 continues under D1
```

The semantic distinction is:

```text
A2 binds D2
!=
A1 rebinds from D1 to D2
```

A new recursive invocation boundary may therefore observe a definition different
from an active ancestor when the applicable resolution semantics select that
definition.

This ADR does not define workflow-version syntax, unqualified-name resolution,
or "latest version" semantics.

### Recursive/cyclic permission creates no invocation authority

The fact that recursive/cyclic composition is permitted does not authorize an
actor or execution resource to invoke workflows.

The rule is:

```text
recursive/cyclic structure permitted
+
invocation path independently authorized
+
invocation independently admissible
→ invocation may be accepted
```

It is not:

```text
recursion permitted
→ all execution resources may invoke workflows
```

Existing invocation-decision-owner rules remain independently authoritative.

In particular, this ADR does not grant independent-agent regions a
workflow-invocation capability.

### Recursive/cyclic composition creates no admissibility escape

Crossing a recursive or cyclic edge MUST NOT itself reset, erase, widen, or
bypass restrictions that apply to the invocation context.

Conceptually:

```text
restriction R
↓
A
↓
B
↓
A
↓
C
```

does not imply:

```text
C without R
```

Issue #6 owns the general transitive composition-admissibility contract.

This ADR establishes only that recursive/cyclic composition is a permitted
topological form to which the ordinary authority and admissibility rules apply.

### Root acceptance does not require infinite expansion

Permitting recursion does not require TURNLOCK to infinitely expand, pre-resolve,
or prove the complete possible future recursive invocation tree when accepting a
root invocation.

Later invocation occurrences retain their own boundaries:

```text
caller reaches invocation X
↓
X resolves under the applicable semantics
↓
applicable authority/admissibility rules are evaluated
↓
X is accepted or rejected
```

This ADR does not define the complete admissibility algorithm.

Issue #6 owns that broader contract.

### No termination or resource guarantee

Permission for recursive/cyclic invocation introduces no guarantee or
requirement concerning:

```text
eventual termination
maximum recursion depth
minimum recursion depth
unbounded nesting capacity
memory availability
compute availability
token availability
wall-clock availability
absence of stack/resource exhaustion
automatic cycle breaking
retry
timeout
cancellation
failure propagation
crash recovery
```

A future implementation, harness, profile, or environment may have explicit
resource constraints.

This ADR does not select such constraints or make any concrete limit part of the
TURNLOCK product semantics.

## Invariant consequence

The invariant-admission test creates no new stable invariant identity.

No `TL-INV-040` is introduced.

The accepted recursion/cycle semantics are carried by existing invariant
responsibilities:

```text
TL-INV-017
→ nested invocation may revisit an ancestor workflow and nesting is not
  semantically limited to an acyclic definition graph

TL-INV-018
→ normal completion returns to the immediate caller at every recursive depth

TL-INV-019
→ recursive/cyclic nesting does not rewrite enclosing orchestration

TL-INV-031
→ required composition capability includes recursive/cyclic composition through
  ordinary nested invocation

TL-INV-035
→ workflow-declared invocation may target an ancestor workflow and participate
  in cyclic call graphs

TL-INV-037
→ each recursive occurrence independently binds and preserves its own governing
  workflow definition
```

`TL-INV-030` continues to prohibit execution resources or runtime results from
creating undeclared global continuations; recursion creates no exception to that
existing rule.

The recursion decision does not require a second invocation mechanism and does
not justify broadening an unrelated invariant identity.

## Formal applicability

Recursive/cyclic invocation is relevant to the future core state-machine model,
but the product decision does not require the first executable TLA+ model to
represent unbounded recursion.

The normative distinction is:

```text
product semantics:
recursive/cyclic invocation is permitted

formal-model scope:
may use a finite abstraction or bounded invocation universe
when that bound is explicitly a modeling choice
```

A finite model bound, bounded caller stack, restricted explored depth, or focused
configuration MUST NOT be presented as a TURNLOCK product recursion limit.

The future model must not encode acyclicity of workflow definitions as a product
requirement.

The future model must preserve distinct invocation occurrences, structured
caller/continuation semantics, per-occurrence governing definitions, and
ordinary admission boundaries when recursive/cyclic traces are represented.

No TLA+ variable, recursion encoding, stack representation, configuration bound,
or model-checking algorithm is selected by this ADR.

No successful TLA+/TLC verification is claimed.

## Rationale

Ordinary workflow composition is more expressive when an invocation target may
be a workflow already present in the ancestry.

Patterns such as:

```text
implementation
→ review
→ implementation
```

can naturally represent iterative processes without requiring the workflow
author to manufacture distinct semantic workflow definitions solely to avoid a
cycle in the call graph.

The semantic safety does not come from forbidding cycles.

It comes from retaining the ordinary invocation boundaries at every occurrence:

```text
distinct invocation occurrence
+
stable governing definition
+
preserved immediate caller
+
preserved continuation
+
ordinary authority
+
ordinary admissibility
```

This also preserves the distinction between source evolution and active
invocation mutation.

A later recursive occurrence may bind a newer definition while its active
ancestor continues under its existing stable definition.

## Alternatives considered

### Require workflow call graphs to be acyclic

Rejected. It would prohibit ordinary recursive composition without a semantic
need.

### Permit direct recursion but forbid mutual recursion

Rejected. The distinction would be arbitrary at the product-semantics level;
ordinary invocation semantics apply equally to both.

### Require proof of termination before accepting recursion

Rejected. TURNLOCK does not guarantee termination for ordinary execution, and
the presence of a call-graph cycle does not imply infinite execution.

### Freeze the complete recursive dependency tree at root acceptance

Rejected. ADR-027 establishes per-invocation governing-definition binding rather
than a root-wide transitive snapshot.

### Treat recursive invocation as active rebinding

Rejected. A recursive call creates a new invocation occurrence; it does not
change the governing definition of the active caller.

### Add a dedicated recursive-call primitive

Rejected. Recursion is ordinary invocation in a topology where the callee may
equal or reach an ancestor workflow.

### Select a recursion depth limit

Rejected. Resource and depth limits are not determined by this semantic
decision.

### Select a cycle detector or termination-analysis algorithm

Rejected. Those are implementation, modeling, or conformance mechanisms rather
than product semantics.

## Consequences

* Direct workflow recursion is permitted.
* Indirect recursion and cyclic workflow call graphs are permitted.
* Repeated workflow identity never collapses distinct invocation occurrences.
* Each recursive/cyclic occurrence retains ordinary immediate-caller and
  continuation semantics.
* Normal completion returns one caller boundary at a time.
* Each occurrence independently binds its governing workflow definition.
* A later recursive occurrence may bind a different definition from an active
  ancestor without rebinding that ancestor.
* Recursive/cyclic permission creates no invocation authority.
* Recursive/cyclic composition creates no admissibility escape.
* Root acceptance need not expand or resolve an infinite future call tree.
* A cyclic call graph does not imply infinite concrete execution.
* No termination, depth, compute, memory, token, timing, retry, timeout,
  cancellation, failure, or crash-recovery guarantee is introduced.
* No new stable invariant identity is admitted.
* Issue #6 remains responsible for the general transitive
  composition-admissibility contract.

## Verification obligation

A conforming realization must be capable of demonstrating, subject to otherwise
applicable authority and admissibility rules:

1. direct recursive invocation `A1 → A2`;
2. indirect recursion `A1 → B1 → A2`;
3. structured normal return `A2 → B1 → A1`;
4. distinct invocation identity for every recursive occurrence;
5. stable governing-definition binding independently for ancestor and recursive
   descendant occurrences;
6. an ancestor remaining under its original definition while a later recursive
   occurrence binds another applicable definition;
7. no automatic invocation authority created by recursion;
8. no restriction reset merely because a recursive/cyclic edge is crossed; and
9. a cyclic workflow-definition graph whose concrete execution can terminate.

The demonstration MUST NOT require a product-level recursion depth, cycle
detector, termination prover, stack representation, scheduler, Rust structure,
DSL construct, TLA+ recursion encoding, TLC bound, or other implementation
mechanism selected by this ADR.

## References

* `docs/specification/turnlock-spec.md`
* `docs/adr/adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md`
* `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
* `docs/adr/adr-022-allow-workflow-declared-invocation-with-structured-call-return-semantics.md`
* `docs/adr/adr-023-clarify-caller-context-and-continuation-semantics-across-nested-workflow-invocations.md`
* `docs/adr/adr-027-bind-each-accepted-invocation-to-a-stable-governing-workflow-definition.md`
* `docs/adr/adr-028-clarify-that-tl-inv-037-forbids-governing-definition-changes-under-current-semantics.md`
* `docs/adr/adr-029-separate-local-execution-capabilities-from-immutable-invocation-orchestration.md`
* `formal/verification.yaml`
* GitHub Issue #23
