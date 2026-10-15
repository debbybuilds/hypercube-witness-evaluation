# Hypercube Witness Evaluation

Building on my master's research in hypercube graph theory, I evaluated LLM-generated monochromatic antipodal paths using independent checks of every submitted solution.

**Pilot complete: 20 user-pasted responses on 10 graphs.** Both model selections supplied valid displayed paths on 10/10 graphs. ChatGPT passed JSON-only compliance in 10/10 replies; Claude in 6/10. These are observations from a small manual-app pilot with user-reported labels, not a general ranking of model capabilities.

| Measure | ChatGPT: “Gpt 6.1 Sol Light” | Claude: “Sonnet 5.5” |
|---|---:|---:|
| Valid displayed paths | 10/10 | 10/10 |
| JSON-only responses | 10/10 | 6/10 |
| Valid paths recovered by frozen response parser | 10/10 | 6/10 |

Four Claude replies included prose followed by a valid path. Their automatic extraction failures are **not mathematical errors in the displayed paths**. Exact underlying model versions and hidden app settings are unknown.

Read the [research report](REPORT.md), inspect the [per-response audit](results/pilot-20/audit.csv), or review [provenance and authorship](docs/provenance.md).

## Why this matters

Mathematical validity, instruction compliance and automatic extraction are separate properties. Here the selected graphs did not expose a difference in displayed-path correctness, but formatting differed. Independent verification makes that conclusion inspectable rather than relying on plausible explanations or a preferred outcome.

My master's thesis, *Combinatorial Properties of Hypercubes*, provides the mathematical foundation. This project applies that background to AI evaluation through generated instances, saved response evidence and reproducible scoring. Source attribution and AI assistance are documented in the [provenance notes](docs/provenance.md).

## Reproduce the completed pilot

Python 3.10+; standard library only. No API keys, model calls or network needed.

```sh
python3 -m hypercube audit-pilot
python3 -m hypercube audit-pilot --check
python3 -m unittest discover -v
```

The first command rebuilds `results/pilot-20/audit.json` and `audit.csv` from the raw replies and source mappings. `--check` verifies those files without rewriting them. The JSON audit includes source hashes, per-response outcomes, model/dimension totals and limitations. Original provider sampling cannot be reproduced from these records.

The audit applies the explicit Claude q3-04 correction, retains the earlier paste as superseded evidence, and checks two retained-record hashes. It recomputes scores rather than trusting saved score fields or progress counters. It rejects duplicate slots, changed retained evidence, mismatched prompts and inconsistent displayed-path annotations.

## The task

Vertices of Q_n are n-bit strings; an edge changes one bit and the antipode complements all bits. Edges have colors 0 or 1, with opposite colors on antipodal edges. A response should contain a simple path joining any antipodal pair using one edge color throughout.

Any valid simple path is accepted: it need not be a geodesic. The active study uses five Q3 graphs and five Q4 graphs, one response per model/graph. All included instances have directly checked reference paths.

The formal parser accepts strict JSON or one whole-response JSON fence (the latter fails JSON-only compliance). It does not strip explanatory prose. A separate diagnostic checks the final JSON line in prose-containing replies to establish the validity of the displayed solution; it does not change formal scores. See the [report's methods](REPORT.md#scoring-and-reproducibility).

## Evidence and protocol changes

Responses were pasted by the user, not obtained from authenticated provider logs. Labels are user-reported. Unknown run times, settings and context/tool controls remain null; receipt timestamps are not generation timestamps.

The original plan had 120 trials. After two restarted responses, the user reduced it to this 20-response feasibility pilot because of manual workload. The first five ascending graph IDs per dimension were chosen and the two responses retained with explicit lineage. This was not preregistration. One collection-order deviation arose from conflicting assistant model instructions; one Claude paste was later corrected by the user. Earlier uncertain-model practice and an off-schedule Claude observation are excluded. No trial was rerun to replace a received failure in the active pilot.

These limitations constrain the conclusions: no causal account of formatting differences, broad model superiority, exact-version performance or safety/alignment performance is established.

## Dataset and implementation

The original toolkit generated 20 graphs (ten per dimension); this pilot uses IDs 01–05 per dimension. Original 120-slot scheduling artifacts are retained as history. Use the [amended schedule](responses/cohorts/gpt-6-1-sol-light/pilot-20/schedule.json) and [amendment manifest](responses/cohorts/gpt-6-1-sol-light/pilot-20/manifest.json) to inspect the active study.

```sh
python3 -m hypercube verify --dataset data
python3 -m hypercube generate --output /tmp/hypercube-pilot-reproduction
```

Generation uses seed `hypercube-pilot-v1`. Each canonical antipodal edge pair receives a color from the low bit of the first SHA-256 digest byte, hashing compact UTF-8 JSON `[seed,n,candidate,[u,v]]`; the other edge receives the complementary color. Exact duplicates are logged. Any unexpected no-path candidate stops generation. Independent topology checks use Hamming distance; reference search uses breadth-first monochromatic connectivity, not SAT software. Tests separately enumerate simple paths on small fixtures and verify ordinary non-geodesic paths are accepted.

| Location | Purpose |
|---|---|
| `REPORT.md` | Finding, thesis connection, methods, amendments and interpretation |
| `hypercube/pilot_audit.py` | Reproducible audit of the amended pilot |
| `hypercube/validation.py` | Independent topology and path checks |
| `hypercube/generation.py`, `search.py` | Fresh instance generation and reference search |
| `hypercube/scoring.py` | Strict response parsing and original attempt-log scoring |
| `data/instances/`, `prompts/`, `reference/` | Graphs, solution-free prompts and separate certificates |
| `responses/cohorts/gpt-6-1-sol-light/pilot-20/` | Active schedule, mappings, correction and raw intake |
| `results/pilot-20/` | Authoritative regenerated JSON/CSV results |
| `tests/` | Fixtures, adversarial inputs, reproducibility and correction tests |
| `docs/experiment-spec.md`, `provenance.md` | Protocol history and contribution record |

`score` and `results/summary.json` belong to the original, stricter 120-slot attempt log. That log is empty because unknown metadata was not fabricated. They are not the active study's results. The completed manual pilot is rebuilt with **`audit-pilot`**.

## Authorship and publication

The research direction, collection and thesis background belong to the researcher; design, implementation, testing and writing were developed with AI assistance. The material is provided for inspection and explanation, not represented as entirely unaided authorship or a novel theorem. See [provenance](docs/provenance.md).

This is a standalone local repository prepared for publication. It has not been published to GitHub. No license has been selected; this version does not grant reuse permission. A larger study should use a separate, prospectively frozen protocol if its expected value justifies the collection cost.
