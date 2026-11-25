# Plan

Orbitline is built in sessions, each with a clear success test. Later sessions build on
earlier ones.

| # | Session | Success |
|---|---|---|
| 1 | TLE parsing and validation (checksums, epochs, element ranges) and SGP4 propagation, including deep-space orbits | Positions match the reference SGP4 on its published verification cases within a stated tolerance; bad TLEs are rejected with the line and field |
| 2 | Frames and visibility: TEME to Earth-fixed, station look angles, and rise, peak and set times above a minimum elevation | Pass times match Skyfield to within a second on a test catalogue; no pass is missed or split |
| 3 | Ground-station network and constraints: antennas, slew rates, maintenance windows, sunlight and eclipse, request priorities | Every constraint has a test that breaks it and a checker that catches it |
| 4 | Scheduler: assign antennas to passes with no clashes, maximise priority-weighted contact time, explain every rejected request | On small cases the result matches an exact solver's optimum; on large cases it beats a greedy baseline and is never infeasible |
| 5 | Changes during the day: a station going down, a new urgent request, a satellite manoeuvre, with minimal changes to the schedule | Re-planning keeps every rule and moves as few passes as the tests require |
| 6 | An independent schedule checker and planted bugs: a checker that reads only the schedule, the catalogue and the station files and re-derives every pass; deliberately broken propagators, pass finders and schedulers kept as permanent tests | Every planted bug is caught by the checker or a reference comparison; the checker never imports the planner |
| 7 | Scale: thousands of satellites and dozens of stations, an operator command line and reports, profiling and benchmarks | A day's plan for the large catalogue runs within the budget; benchmarks fail the build on regression |

## Out of scope

A web UI, Playwright, containers and Kubernetes. None could be verified here, and the hours go
to the references and the checker. Operators get a command line, a written schedule report and
machine-readable output.

## The numbers

- **Propagation:** positions within 1 m of the reference SGP4 on its published verification
  cases (near-Earth and deep-space), and within 1 mm/s in velocity.
- **Passes:** rise, peak and set times within 1 s of Skyfield over a fixed catalogue of at
  least 500 satellites and 20 stations over 7 days; zero missed and zero split passes.
- **Scheduling:** on every small case (up to 12 passes and 3 antennas), the priority-weighted
  contact time equals an exact solver's optimum; on large cases it is at least the greedy
  baseline's on every seed, and never infeasible.
- **Teeth:** at least 12 planted bugs (for example: deep-space terms dropped, TEME treated as
  Earth-fixed, sidereal time off by a day, a pass split at its peak, slew time ignored, an
  antenna double-booked), each caught and kept as a permanent test.
- **Scale:** a day's plan for 5,000 satellites and 40 stations within a stated budget.

## Rules

- No layer starts until the layer below passes its gates: a pass finder is only trusted once
  propagation matches the reference, and a schedule is only reported once it matches the exact
  solver on small cases.
- The references are the `sgp4` package and Skyfield, run in a separate tool environment.
  The project's own propagator and pass finder never call them.
- All randomness comes from named, seeded streams. Every run replays exactly.
- Orbital data in tests is from bundled fixture files. The test suite never downloads.
