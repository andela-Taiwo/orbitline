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
| 6 | Live engine and web UI: clock, ground tracks, station coverage, schedule timeline and replay | Playwright covers an outage being re-planned and an urgent request being fitted in |
| 7 | Scale: thousands of satellites and dozens of stations, profiling and benchmarks | A day's plan for the large catalogue runs within a set budget; benchmarks fail the build on regression |

## Rules

- The references are the `sgp4` package and Skyfield, run in a separate tool environment.
  The project's own propagator and pass finder never call them.
- All randomness comes from named, seeded streams. Every run replays exactly.
- Orbital data in tests is from bundled fixture files. The test suite never downloads.
