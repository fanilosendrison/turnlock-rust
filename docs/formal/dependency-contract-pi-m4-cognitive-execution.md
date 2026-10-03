# Dependency Contract — Gate A Pi M4 Cognitive Execution

Contract ID: `DC-PI-M4-GATE-A-COGNITIVE-EXECUTION`

Version: `1.0.0`

Status: `active`

## 1. Status, authority, and purpose

This is implementation-construction dependency authority for M4-A only.

It consumes:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 9.0.1
NIB-M-GATE-A-COGNITIVE-EXECUTION-CAPTURE 1.0.4
```

It creates no TURNLOCK product semantics.
It creates no hostile-review protocol semantics.
It creates no reviewer-acquisition semantics.
It creates no model-version resolution semantics.

Qualification basis:

```text
Issue #41 final classification:
QUALIFIED-WITH-REQUIRED-ADAPTER

Durable evidence:
#42
#43
#44
#45
#46 superseding re-adjudication
```

The five accepted adapter responsibilities are exactly:

1. Fresh public pi-ai Context + direct Models.streamSimple; no AgentSession or
   coding loop.

2. Explicit transport/maxRetries/tools/deferred/AbortSignal.

3. Provider evidence through fetch/onPayload/onResponse/onProviderStreamEvent
   without semantic-request rewriting.

4. Provider response/effective-model evidence from provider-owned events,
   never requested AssistantMessage.model or unpopulated responseModel.

5. Exact provider-semantic textual completion and M4 journal/recovery evidence
   preserved before interpretation; never manufacture provider truth from Pi
   normalization or absence.

## 2. Immutable dependency identity

```text
package =
@earendil-works/pi-ai

package version =
0.99.2

Pi source commit =
005af57d88ee23b33778f343a9595b32e67ff788

runtime floor =
Node.js >= 22.19.0

public cognitive execution surface =
Models.streamSimple(...)

provider factory =
openaiCodexProvider()

provider =
openai-codex

provider API =
openai-codex-responses

provider endpoint =
https://chatgpt.com/backend-api/codex/responses
```

There is no version range and no floating Pi commit.

## 3. Exact v1 support scope

The active contract supports exactly:

```text
provider =
openai-codex

requestModel =
gpt-6.1-sol

provider API =
openai-codex-responses
```

This does NOT:

```text
admit a reviewer profile
assert gpt-6.1-sol is immutable
assert gpt-6.1-sol is a resolved model_version
resolve Issue #47
qualify another Pi provider
qualify another request model
```

Any exact M4 operation asking for another provider or requestModel is:

```text
unsupported by DC version 1.0.0
→ DEPENDENCY-CONTRACT-VIOLATION
→ no fallback
→ no substitution
→ no provider call
```

A future provider/model requires explicit requalification and a new accepted DC
version.

## 4. Allowed public Pi imports

Permit exactly the conceptual public imports:

```ts
from "@earendil-works/pi-ai":

createModels
hasApi
InMemoryCredentialStore
Context
OAuthCredential
relevant public option/evidence types

from "@earendil-works/pi-ai/providers/openai-codex":

openaiCodexProvider
```

Do not import:

```text
Pi coding-agent
AgentSession
subagent APIs
Codex CLI
Codex App Server
private/internal Pi modules
internal openai-codex response implementation modules
```

Source inspection may justify the contract, but GREEN consumes public surfaces
only.

## 5. Identity hierarchy

Preserve exactly:

```text
WorkItemId
= logical cognitive execution
= receipt.execution_id

ExecutionId
= protocol attempt
= receipt.attempt_id

CognitiveCallId
= exact M4 adapter call
= receipt.call_id

PiProviderAttemptId
= one dependency transport attempt

ProviderResponseId
= provider-owned response identity
```

Define:

```text
callId =
deriveId(
  "m4-cognitive-call.v1",
  execution.executionId
)
```

Define selected-v1 provider attempt:

```text
providerAttemptOrdinal = 1

providerAttemptId =
deriveId(
  "m4-provider-attempt.v1",
  callId,
  "1"
)
```

`providerAttemptId` is M4 operational evidence only.

It is not written into schema-v3 receipts.

Require:

```text
callId != providerResponseId
```

as identity namespaces even if string values accidentally resemble each other.

## 6. Dependency execution plan

Define exactly:

```ts
interface PiM4DependencyExecutionPlanV1 {
  readonly schema:
    "gate-a-pi-m4-dependency-execution-plan.v1";

  readonly contractId:
    "DC-PI-M4-GATE-A-COGNITIVE-EXECUTION";

  readonly contractVersion:
    "1.0.0";

  readonly callId:
    CognitiveCallId;

  readonly reviewerProfileId:
    string;

  readonly provider:
    "openai-codex";

  readonly requestModel:
    "gpt-6.1-sol";

  readonly providerApi:
    "openai-codex-responses";

  readonly dependency: {
    readonly package:
      "@earendil-works/pi-ai";

    readonly version:
      "0.99.2";

    readonly sourceCommit:
      "005af57d88ee23b33778f343a9595b32e67ff788";
  };

  readonly runtimeFloor: {
    readonly name: "node";
    readonly minimumVersion: "22.19.0";
  };

  readonly invocation: {
    readonly surface: "Models.streamSimple";
    readonly transport: "sse";
    readonly maxRetries: 0;
    readonly timeoutMs: 0;
    readonly toolsEnabled: false;
    readonly toolChoice: "none";
    readonly deferred: false;
    readonly cacheRetention: "none";
  };

  readonly credentialRequirementId:
    "pi-openai-codex-oauth-min-validity-10m.v1";
}
```

The plan is credential-free.

It contains no:

```text
access token
refresh token
Authorization
Cookie
credential source
environment value
timestamp
StateRevision
session/process identity
```

## 7. Credential-free plan construction

Plan construction happens during M4 `prepare()`.

It causes zero network effects.

Algorithm exactly:

```text
1. Require exact provider == "openai-codex".

2. Require exact requestModel == "gpt-6.1-sol".

3. Construct openaiCodexProvider().

4. Require provider.id == "openai-codex".

5. Inspect its synchronous pinned static model catalog only.

6. Require exactly one model with:
       id == "gpt-6.1-sol"

7. Require:
       hasApi(model, "openai-codex-responses") == true

8. Do NOT call:
       refresh()
       getAvailable()
       login()
       provider network
       credential network

9. Construct the exact plan above.

10. Seal it using ordinary M4 runner canonical JSON.
```

No model fallback.

## 8. Credential requirement and secret boundary

Define:

```text
credentialRequirementId =
pi-openai-codex-oauth-min-validity-10m.v1
```

The transient runtime credential must satisfy the public Pi `OAuthCredential`
shape:

```text
type == "oauth"

access:
non-empty string

refresh:
non-empty string

expires:
finite numeric Unix-millisecond timestamp
```

At every M4 credential-availability observation require:

```text
expires - current wall clock >= 600000 ms
```

The ten-minute requirement is an implementation safety margin over Pi's pinned
five-minute automatic OAuth-refresh threshold.

Absence or insufficient remaining validity means:

```text
required-provider-credential-unavailable
```

under existing M4 operational-blocker semantics.

A credential object returned by the credential boundary that is malformed,
throws, violates type shape, or cannot satisfy the declared contract is:

```text
CREDENTIAL-BOUNDARY-FAILURE
```

not an operational blocker.

Credential source/resolution is outside this DC.

The DC defines only the required transient object and injection behavior.

At invocation time:

```text
1. create one fresh InMemoryCredentialStore

2. insert the exact transient OAuthCredential only under:
   "openai-codex"

3. create one fresh Models instance using exactly that credential store

4. retain neither Models nor credential store after this M4 call
```

Do not use:

```text
ambient environment auth
ambient Pi auth storage
repository credential files
global persistent Pi credential store
options.apiKey
```

Secrets exist only in transient memory.

Do not persist or log any credential field.

## 9. Fresh isolated Context

Read exact prompt and packet artifacts through `CampaignArtifactStore`.

Decode both as strict UTF-8.

Require:

```text
UTF8(DecodedPrompt) == exact original prompt bytes

UTF8(DecodedPacket) == exact original packet bytes
```

Any failed UTF-8 round trip is an input/artifact failure.

Construct exactly one fresh Context:

```ts
{
  systemPrompt: exactPromptText,

  messages: [
    {
      role: "user",
      content: exactPacketText,
      timestamp: 0,
    },
  ],

  tools: [],
}
```

The `timestamp = 0` value is mechanical only.

The pinned Pi request converter does not send this timestamp to the provider.

Never use `Date.now()` for Context messages.

The Context contains no:

```text
prior assistant message
prior reviewer output
sibling reviewer state
AGENTS.md
workspace context
coding-agent instructions
session history
tool result
tool declaration
steering
follow-up
compaction summary
```

## 10. Models/provider/model construction

For every M4 invocation:

```text
one fresh credential store
→ one fresh Models instance
→ one openaiCodexProvider instance
→ models.setProvider(provider)
→ models.getModel("openai-codex", "gpt-6.1-sol")
```

Require:

```text
model exists

model.provider == "openai-codex"

model.id == "gpt-6.1-sol"

hasApi(model, "openai-codex-responses") == true
```

Do not call `models.refresh()`.

Do not select a model from defaults.

Do not enumerate and choose another model.

## 11. Exact Models.streamSimple options

Invoke public:

```text
Models.streamSimple(...)
```

exactly once per M4 call.

Use exactly:

```text
transport = "sse"

maxRetries = 0

timeoutMs = 0

toolChoice = "none"

deferred = false

cacheRetention = "none"

textVerbosity = "low"

signal = exact execution-owned AbortSignal
```

Also supply exactly:

```text
instrumented fetch
onPayload
onResponse
onProviderStreamEvent
```

Explicitly omit:

```text
sessionId
apiKey
custom headers
custom environment auth
temperature
maxTokens
serviceTier
caller-selected reasoning level
```

Reasoning configuration therefore remains the exact pinned provider/model
default for `gpt-6.1-sol`; GREEN may not choose a reasoning level.

No provider API default may re-enable tools because:

```text
Context.tools == []
AND
toolChoice == "none"
```

If any tool-call content nevertheless appears:

```text
DEPENDENCY-CONTRACT-VIOLATION
```

## 12. Direct invocation and stream consumption

Exact sequence:

```text
stream =
models.streamSimple(
  exact model,
  exact fresh Context,
  exact options
)
```

Call this public surface exactly once.

Then immediately consume that exact stream to its final `AssistantMessage`
through the public stream result mechanism.

Do not:

```text
call completeSimple
call streamSimple again
recreate the stream
call provider.streamSimple directly
follow up
resume a deferred response
```

The final Pi `AssistantMessage` is observation material only.

It is never by itself sufficient provider truth.

## 13. Transport attempt instrumentation

The custom fetch wrapper is transparent.

It must not modify:

```text
URL
method
headers
body
signal
request semantics
```

Maintain:

```text
transportAttemptCount initially 0
```

Immediately before first delegated `globalThis.fetch`:

```text
transportAttemptCount = 1
providerAttemptId =
deriveId("m4-provider-attempt.v1", callId, "1")
```

If the wrapper is invoked a second time for the same M4 call:

```text
DO NOT invoke globalThis.fetch again
→ DEPENDENCY-CONTRACT-VIOLATION
```

Selected v1 therefore has:

```text
transportAttemptCount ∈ {0,1}
```

Every receipt-admissible terminal outcome has:

```text
transportAttemptCount == 1
```

## 14. Request observation

`onPayload` is observational only.

It MUST always return:

```text
undefined
```

It may never replace the payload.

Require exactly one `onPayload` observation whenever transport is reached.

Inside the callback capture:

```text
payloadJsonBytes =
UTF8(JSON.stringify(exact observed payload object))
```

Do not mutate the object before or after observation.

The pinned provider later serializes the same unchanged body with
`JSON.stringify`.

Seal those exact observed pre-compression JSON bytes:

```text
mediaType = application/json
```

Define:

```ts
interface PiM4DependencyRequestEvidenceV1 {
  readonly schema:
    "gate-a-pi-m4-dependency-request-evidence.v1";

  readonly callId:
    CognitiveCallId;

  readonly providerAttemptId:
    string;

  readonly reviewerProfileId:
    string;

  readonly provider:
    "openai-codex";

  readonly requestModel:
    "gpt-6.1-sol";

  readonly providerApi:
    "openai-codex-responses";

  readonly prompt:
    ArtifactRef;

  readonly packet:
    ArtifactRef;

  readonly providerPayload:
    ArtifactRef;

  readonly transport:
    "sse";
}
```

The observed payload must mechanically preserve:

```text
model == "gpt-6.1-sol"

store == false

stream == true

instructions == exact prompt text

input ==
exact one user message derived from exact packet text

tool_choice == "none"

tools absent

text.verbosity == "low"

prompt_cache_key absent from JSON wire form
```

Provider-owned pinned non-semantic execution fields such as
`include = ["reasoning.encrypted_content"]` are permitted exactly as emitted by
the pinned provider implementation.

## 15. HTTP response observation

`onResponse` is observational.

Record only:

```text
HTTP status integer
```

Do NOT persist response headers.

In particular never persist:

```text
set-cookie
cookie
authorization
secret-bearing provider headers
```

For one transport attempt, more than one distinct HTTP Response observation is:

```text
DEPENDENCY-CONTRACT-VIOLATION
```

## 16. Raw provider-event trace

`onProviderStreamEvent` receives the exact parsed provider event before Pi's
normalization.

For each callback:

```text
deep-copy the JSON value
append it in exact callback order
do not mutate it
```

At terminal/returned classification, seal exactly:

```ts
interface PiM4ProviderEventTraceV1 {
  readonly schema:
    "gate-a-pi-m4-provider-event-trace.v1";

  readonly callId:
    CognitiveCallId;

  readonly providerAttemptId:
    string;

  readonly events:
    readonly JsonValue[];
}
```

Use runner canonical JSON for the trace artifact.

This trace is operational/provider evidence.

It is not hostile-review evidence by itself.

## 17. Provider response identity extraction

Inspect only provider-owned raw events.

Identity-bearing event families are:

```text
response.created
response.completed
response.incomplete
response.done
response.failed
```

For every non-empty:

```text
event.response.id
```

collect exact string.

Require all observed non-empty response IDs for the call are identical.

If two distinct provider-owned IDs appear:

```text
DEPENDENCY-CONTRACT-VIOLATION
```

Then:

```text
providerResponseId =
unique observed provider response ID
or null when none exists
```

Perform the same rule for:

```text
event.response.model
```

Then:

```text
providerModel =
unique provider-owned response.model
or null
```

A difference between:

```text
requestModel
and
providerModel
```

is NOT rewritten and is NOT automatically a contract failure.

Preserve both.

Never derive `providerModel` from:

```text
AssistantMessage.model
AssistantMessage.responseModel
requestModel
profile metadata
```

Pi `responseModel` is known to be unpopulated on the selected path.

## 18. Provider terminal-event classification

Exactly one accepted provider terminal event may exist for one terminal call.

Classify raw provider events exactly:

```text
response.completed
→ semantic terminal response
provided response.status is absent or "completed"

response.incomplete
→ semantic terminal response
provided response.status is absent or "incomplete"

response.done
with response.status == "completed"
→ semantic terminal response

response.done
with response.status == "incomplete"
→ semantic terminal response

response.done
with response.status == "failed"
→ terminal no-completed-response failure

response.done
with response.status == "cancelled"
→ terminal no-completed-response failure

response.failed
→ terminal no-completed-response failure

error
→ terminal provider error / no-completed-response failure
```

For `response.done` with:

```text
status absent
queued
in_progress
unknown value
```

return:

```text
DEPENDENCY-CONTRACT-VIOLATION
```

For `response.completed` with an explicit non-`completed` status, or
`response.incomplete` with an explicit non-`incomplete` status:

```text
DEPENDENCY-CONTRACT-VIOLATION
```

More than one accepted provider terminal event:

```text
DEPENDENCY-CONTRACT-VIOLATION
```

Do NOT use Pi's normalized internal `response.completed` event type as the
provider-terminal discriminator.

## 19. Exact provider-semantic textual completion

From raw provider events concatenate, in exact callback order, only exact string
deltas from:

```text
response.output_text.delta
response.refusal.delta
```

Define:

```text
providerDeltaText =
exact concatenation
with no separator
```

From the final Pi AssistantMessage concatenate in exact content-array order only:

```text
content entries where type == "text"
```

Define:

```text
piTerminalText
```

Do not include reasoning blocks.

Tool-call blocks are forbidden.

For a semantic terminal response require:

```text
UTF8(providerDeltaText)
==
UTF8(piTerminalText)
```

If they differ:

```text
DEPENDENCY-CONTRACT-VIOLATION
```

Then the exact provider-semantic textual completion is:

```text
rawContent =
providerDeltaText
```

M4 seals exactly:

```text
UTF8(rawContent)
```

with:

```text
mediaType = text/plain; charset=utf-8
```

No:

```text
trim
newline insertion/removal
Unicode normalization
JSON parse/reserialization
repair
pretty printing
refusal interpretation
schema validation
semantic classification
```

Empty text is valid.

Refusal text is valid captured text.

Malformed JSON is valid captured text.

## 20. Exact termination string

For a semantic terminal response:

```text
response.completed
→ "completed"

response.incomplete
without non-empty incomplete_details.reason
→ "incomplete"

response.incomplete
with reason R
→ "incomplete." + R

response.done status completed
→ "completed"

response.done status incomplete with no reason
→ "incomplete"

response.done status incomplete with reason R
→ "incomplete." + R
```

For technical terminal failure:

```text
HTTP non-OK status N
→ "http." + decimal N

response.failed
→ "failed"

response.done status failed
→ "failed"

response.done status cancelled
→ "cancelled"

provider raw error event
→ "provider.error"
```

Never use free-form exception text as `termination`.

## 21. Positive technical-failure facts

A `technical-failure` is valid only when:

```text
transportAttemptCount == 1

AND

no semantic terminal response was established

AND

one exact positive terminal fact exists
```

Accepted positive terminal facts are exactly:

```text
A. one HTTP Response with response.ok == false

B. raw provider response.failed

C. raw provider error event

D. raw response.done with status failed

E. raw response.done with status cancelled
```

Partial textual deltas before a provider failure do NOT become a completed
response.

Preserve them only as provider runtime evidence.

Define exact failure-source enum:

```text
"http-non-ok"
"provider-response-failed"
"provider-error-event"
"provider-terminal-failed"
"provider-terminal-cancelled"
```

Define:

```ts
interface PiM4TechnicalFailureEvidenceV1 {
  readonly schema:
    "gate-a-pi-m4-technical-failure-evidence.v1";

  readonly callId:
    CognitiveCallId;

  readonly providerAttemptId:
    string;

  readonly source:
    | "http-non-ok"
    | "provider-response-failed"
    | "provider-error-event"
    | "provider-terminal-failed"
    | "provider-terminal-cancelled";

  readonly httpStatus:
    number | null;

  readonly providerEventIndex:
    number | null;

  readonly termination:
    string;
}
```

No technical-failure branch may have:

```text
transportAttemptCount == 0
```

This closes the schema-v3 receipt minimum.

## 22. Ambiguous execution facts

The following are NOT technical failure by themselves:

```text
AbortError

signal cancellation

network exception before any HTTP Response

HTTP 2xx with missing body

SSE parse/protocol failure without accepted provider terminal event

stream interruption

EOF without accepted provider terminal event

Pi final stopReason == error by itself

Pi final stopReason == aborted by itself

missing provider response ID

missing provider model

elapsed time

process interruption
```

Map these to:

```text
ambiguous
```

unless another exact accepted positive terminal fact exists.

Define ambiguity reasons:

```text
"aborted"
"network-exception"
"missing-response-body"
"provider-stream-protocol-error"
"stream-interruption"
"stream-ended-without-provider-terminal"
"pi-error-without-provider-terminal"
```

Define:

```ts
interface PiM4AmbiguityEvidenceV1 {
  readonly schema:
    "gate-a-pi-m4-ambiguity-evidence.v1";

  readonly callId:
    CognitiveCallId;

  readonly providerAttemptId:
    string | null;

  readonly transportAttemptCount:
    0 | 1;

  readonly reason:
    | "aborted"
    | "network-exception"
    | "missing-response-body"
    | "provider-stream-protocol-error"
    | "stream-interruption"
    | "stream-ended-without-provider-terminal"
    | "pi-error-without-provider-terminal";

  readonly httpStatus:
    number | null;

  readonly providerResponseId:
    string | null;

  readonly providerModel:
    string | null;
}
```

M4 maps direct ambiguity to existing:

```text
kind = uncertain
```

It never fabricates terminal truth.

## 23. Runtime/provider evidence

Define:

```ts
interface PiM4DependencyRuntimeEvidenceV1 {
  readonly schema:
    "gate-a-pi-m4-dependency-runtime-evidence.v1";

  readonly callId:
    CognitiveCallId;

  readonly providerAttemptId:
    string;

  readonly dependency: {
    readonly package:
      "@earendil-works/pi-ai";

    readonly version:
      "0.99.2";

    readonly sourceCommit:
      "005af57d88ee23b33778f343a9595b32e67ff788";
  };

  readonly node: {
    readonly name: "node";
    readonly version: string;
  };

  readonly provider:
    "openai-codex";

  readonly requestModel:
    "gpt-6.1-sol";

  readonly providerApi:
    "openai-codex-responses";

  readonly transport:
    "sse";

  readonly transportAttemptCount:
    1;

  readonly httpStatus:
    number | null;

  readonly providerResponseId:
    string | null;

  readonly providerModel:
    string | null;

  readonly providerEventTrace:
    ArtifactRef;

  readonly termination:
    string;
}
```

Require actual:

```text
process.release.name == "node"
process.versions.node semver >= 22.19.0
```

M4 terminal evidence projects:

```ts
runtime = {
  name: "@earendil-works/pi-ai",
  version: "0.99.2",
}
```

Node exact version stays in dependency runtime evidence.

## 24. Evidence ordering into M4-A

For completed response:

```text
dependencyRequestEvidence =
exact PiM4DependencyRequestEvidenceV1 ArtifactRef

dependencyRuntimeEvidence =
[
  exact PiM4ProviderEventTraceV1 ArtifactRef,
  exact PiM4DependencyRuntimeEvidenceV1 ArtifactRef
]
```

For technical failure:

```text
dependencyRequestEvidence =
exact PiM4DependencyRequestEvidenceV1 ArtifactRef

dependencyRuntimeEvidence =
[
  exact PiM4ProviderEventTraceV1 ArtifactRef,
  exact PiM4DependencyRuntimeEvidenceV1 ArtifactRef
]

failureEvidence =
[
  exact PiM4TechnicalFailureEvidenceV1 ArtifactRef
]
```

For direct ambiguity, after arm-time evidence append only available same-call
evidence in this order:

```text
dependency request evidence, if payload was observed
provider event trace, if sealed
ambiguity evidence
```

Do not label ambiguity evidence as terminal evidence.

## 25. Abort, cancellation, revocation, and recovery

The adapter receives the exact execution-owned AbortSignal.

Use the same exact signal for:

```text
credential-store operation
Models.streamSimple options
SSE request
```

If already aborted before transport:

```text
transportAttemptCount = 0
no provider attempt
```

When MAYBE-SENT is already durable, this still maps to M4 `uncertain`, not
positive nonexecution.

After transport begins, abort does not prove provider cancellation.

No later provider attempt may begin.

There is no retry.

Selected backend recovery capability is exactly:

```text
provider-side post-crash response lookup:
UNKNOWN / unavailable for accepted construction use

provider response ID sufficient for safe recovery:
NOT ESTABLISHED

safe read-only provider pending observation:
NOT ESTABLISHED

pending:
FORBIDDEN

provider-call replay:
FORBIDDEN
```

Recovery relies only on M4 local durable journal/evidence:

```text
PREPARED without MAYBE-SENT
→ positive local nonexecution proof

MAYBE-SENT without TERMINAL-DURABLE
→ unknown / indeterminate

TERMINAL-DURABLE
→ reconstruct exact terminal outcome locally
→ zero provider replay
```

Do not import generic OpenAI `/responses/{id}` assumptions into the ChatGPT
Codex backend.

## 26. Forbidden behavior, limitations, invariants, and discovery routing

Explicitly forbid:

```text
AgentSession
coding-agent loop
Pi subagent loop
Codex CLI
Codex App Server

WebSocket transport
transport = auto

automatic provider retry
M4 retry

dependency timeout

tools
tool continuation

deferred execution

session continuation
prompt-cache/session identity

ambient semantic context

request rewriting through onPayload

model fallback

provider fallback

reviewerProfileId lookup from environment/config

providerModel = AssistantMessage.model

providerModel = AssistantMessage.responseModel

providerResponseId = callId

Pi normalized terminal event used as provider terminal truth

rawContent from JSON reserialization

provider-call replay after uncertainty

provider pending without positive observational recovery
```

Provider-normalization limitations:

```text
Pi collapses raw response.done / response.completed / response.incomplete into
an internal response.completed processing path.

Therefore raw onProviderStreamEvent evidence is authoritative for provider event
identity.

Pi high-level AssistantMessage.model reflects requested model identity.

Pi responseModel is not populated on the selected path.

Therefore neither may substitute provider-owned response.model evidence.
```

Issue #47 boundary exactly:

```text
The DC may preserve providerModel.

It may NOT decide whether that identifier is:
resolved immutable model_version
or
mutable/unresolved alias.

That remains Issue #47 Product Semantics authority.
```

Exact invariants:

```text
DC-PI-M4-01
One runner Execution maps to one M4 callId.

DC-PI-M4-02
One selected-v1 M4 call invokes Models.streamSimple exactly once.

DC-PI-M4-03
Selected v1 starts at most one provider/transport attempt.

DC-PI-M4-04
No second fetch may cross the provider boundary.

DC-PI-M4-05
Provider/model requested values come only from immutable M4 operation binding.

DC-PI-M4-06
Fresh Context contains only exact prompt plus exact packet and zero tools.

DC-PI-M4-07
onPayload is observational and returns undefined.

DC-PI-M4-08
Provider identity comes only from raw provider events.

DC-PI-M4-09
Completed rawContent equals exact provider textual-delta concatenation and exact
Pi terminal text projection byte-for-byte.

DC-PI-M4-10
Every receipt-admissible technical failure has transportAttemptCount == 1.

DC-PI-M4-11
Abort/network interruption/missing terminal evidence never manufacture
technical failure.

DC-PI-M4-12
No selected-backend provider recovery or pending capability is assumed.

DC-PI-M4-13
Credential values never enter durable evidence.

DC-PI-M4-14
Issue #47 remains unresolved.
```

Construction classification:
QUALIFIED-WITH-REQUIRED-ADAPTER

GREEN status:
This Dependency Contract closes the Pi-specific M4-A dependency design surface.
GREEN remains subject to the rest of the accepted construction sequence,
including NIB-T and hostile review.
