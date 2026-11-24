# Orbitline

Plan satellite passes over a network of ground stations: where every satellite is, when each
station can see it, and which antenna talks to which satellite, without clashes.

> **Status: foundation only.** The project layout, tooling, time scales, WGS84 geodesy and
> seeded random streams exist and are tested. Orbit propagation, visibility windows,
> scheduling and the web UI are not built yet. See [the plan](docs/PLAN.md).

## What it will do

- **Orbits**: read two-line element sets and propagate them with SGP4, matching the reference
  implementation to a stated tolerance.
- **Visibility**: find every window in which a station sees a satellite above its minimum
  elevation, with rise, peak and set times.
- **Constraints**: antennas that take time to slew, stations that cannot transmit during
  maintenance, satellites that must not downlink in sunlight, and priority requests.
- **Scheduling**: assign antennas to passes with no clashes, and explain why a request could
  not be scheduled.
- **Live view**: a map with ground tracks, station coverage and the schedule on a timeline.

All randomness comes from a seed, so every run replays exactly.

## What exists today

| Module | What it does |
|---|---|
| `orbitline.timescales` | Calendar dates to Julian dates, and Greenwich mean sidereal time |
| `orbitline.geodesy` | WGS84 latitude, longitude and height to Earth-fixed positions and back, and azimuth, elevation and range from a station |
| `orbitline.rng` | Named, independent random streams from one run seed |

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
make setup   # install locked dependencies
make check   # lint, format check, type check and tests
make help    # list every target
```

## Layout

```
src/orbitline/  # the planner package
tests/          # unit and property tests
docs/PLAN.md    # what is being built, in order
docs/adr/       # architecture decision records
```

## Licence

MIT. See [LICENSE](LICENSE).
