# video-understanding

Machine-readable video understanding for agents. One mandatory 1fps catalog
pass per video produces a per-second index of what's visible and what's said;
frame-precision cuts resolve through that index instead of re-scanning.

The format is designed for the agent, not for people. People get derived
views — like the [timeline demo](https://kitbyfez.github.io/video-understanding/)
built from the example catalog.

- [`spec/FORMAT.md`](spec/FORMAT.md) — the catalog data format (v1)
- [`workflow/WORKFLOW.md`](workflow/WORKFLOW.md) — the mandatory pass + precision procedure
- [`examples/`](examples/) — real catalogs; each is a complete worked example

## Example

[`examples/iwa-s02e01-trailer-v2/`](examples/iwa-s02e01-trailer-v2/) is the
first catalog: a 37.5s trailer, 38 per-second records, word-level transcript,
reference frames. Rendered as a timeline
[here](https://kitbyfez.github.io/video-understanding/).
