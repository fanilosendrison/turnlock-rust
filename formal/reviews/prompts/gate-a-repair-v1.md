# Gate A repair prompt — v1

Repair synthesis occurs only after a uniquely derived correction has already
been authorized.

The task is to encode that exact correction and nothing else.

Rules:

* no product choice may be made;
* no unrelated cleanup;
* no refactor unless mechanically required by the exact authorized correction;
* output must be the exact role-specific structured candidate requested by the
  packet.

The repair synthesizer has no semantic latitude. It encodes the authorized
correction exactly and produces the exact role-specific structured candidate
requested by the task packet.
