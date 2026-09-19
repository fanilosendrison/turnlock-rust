# Gate A adjudication prompt — v1

Use only the supplied canonical packet and the exact finding or candidate
supplied in the task packet.

Rules:

* never introduce new product semantics;
* never choose among multiple authority-compatible behaviors;
* an inability to refute does not establish truth;
* any proposed `derived-from-existing-authority` conclusion must show a complete
  derivation and why no alternative remains;
* any proposed `decision-required` conclusion must identify at least two
  materially distinct authority-compatible outcomes or a genuine authority
  conflict;
* no majority reasoning;
* no preference or implementation convenience;
* output only the role-specific JSON requested by the task packet;
* no chain-of-thought transcript.

Do not define or emit a universal free-form verdict field. The adjudication
result is derived from the role-specific structured fields requested by the
task packet.
