# Integrated TLC configurations

Integrated `.cfg` files will exercise all currently formalized TURNLOCK core execution forms together within finite bounds.

Planned profiles:

- `smoke.cfg` — small bounds, fast cross-feature feedback.
- `standard.cfg` — ordinary CI bounds.
- `stress.cfg` — deliberately larger/expensive bounds.

No configuration is created until the executable `Turnlock.tla` model exists; the planned paths are already recorded in `formal/verification.yaml`.
