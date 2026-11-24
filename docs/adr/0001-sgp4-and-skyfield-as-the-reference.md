# 0001: SGP4 and Skyfield are the reference, not dependencies

## Status

Accepted

## Context

A satellite's position from a two-line element set is only meaningful if it is computed the
way the element set was produced: with SGP4. The `sgp4` package on PyPI is the reference
implementation, and Skyfield builds pass prediction on top of it. Using them directly would be
quicker, but then Orbitline's results could not be checked independently, and the scheduler
would depend on code it cannot change.

## Decision

- Orbitline implements its own propagator, frame conversions and pass finder.
- `sgp4` and Skyfield are used only to produce reference results. They run in a separate,
  pinned tool environment and write fixtures that the tests compare against.
- `make check` never needs `sgp4` or Skyfield installed, and never downloads orbital data.

## Consequences

- Every position and pass time has an independent check against trusted tools.
- Reference fixtures must be regenerated deliberately when the reference versions change.
- Earth orientation is simplified (no polar motion, UT1 taken as UTC), so the tolerance against
  Skyfield must allow for it and the ADR that sets the tolerance must say so.
