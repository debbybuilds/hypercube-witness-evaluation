# Evaluating LLM-Generated Paths in Hypercube Graphs

**Deborah Ologundudu · Feasibility pilot · 15 October 2026**

## Overview

Building on my master's research in hypercube graph theory, I investigated whether language models could construct valid monochromatic paths between antipodal vertices.

I evaluated 20 responses from ChatGPT and Claude across ten colored hypercube graphs. Each submitted path was checked for adjacency, distinct vertices, consistent edge color and antipodal endpoints. Mathematical validity and JSON-only compliance were assessed separately.

Both models supplied valid paths on all ten graphs. ChatGPT followed the JSON-only requirement in all ten responses, while Claude did so in six. The four remaining Claude replies included explanations followed by valid path objects. These results illustrate why mathematical correctness and response-format compliance should be evaluated independently.

| Measure | ChatGPT, displayed label “Gpt 6.1 Sol Light” | Claude, displayed label “Sonnet 5.5” |
|---|---:|---:|
| Received responses | 10/10 planned | 10/10 planned |
| Displayed paths independently verified as valid | 10/10 | 10/10 |
| Complete response satisfies JSON-only requirement | 10/10 | 6/10 |
| Valid path recovered by the frozen response parser | 10/10 | 6/10 |

The names above are user-reported app labels, not independently verified provider version identifiers. The source material is user-pasted output rather than authenticated provider traces.

## Research background

My master's thesis, *Combinatorial Properties of Hypercubes*, studied antipodal colorings and computational verification. This project applies that background to evaluating model-generated mathematical solutions. I used generated instances, saved prompts and responses, reference graph search, and independent path checks to make the evaluation reproducible.

## Task and instances

Vertices of the n-dimensional hypercube are n-bit strings. Adjacent vertices differ in one bit, and antipodes complement every bit. Every edge has color 0 or 1; antipodal edges receive opposite colors. A submitted path must use listed edges, contain no repeated vertex, have one color throughout, and join antipodal endpoints.

Any qualifying simple path is accepted. It need not be a shortest path or geodesic, and the model may choose the antipodal pair.

The active pilot uses instances q3-01 through q3-05 and q4-01 through q4-05: five labeled colorings of Q3 and five of Q4. Each model has one response per graph. Q3 has 8 vertices and 12 edges; Q4 has 16 vertices and 32 edges.

The original toolkit generated ten colorings per dimension. Color selection uses the documented seed `hypercube-pilot-v1` and SHA-256 over canonical antipodal edge pairs. The generator logs duplicate candidates. An independent topology validator derives adjacency from Hamming distance, separately from generation. A reference breadth-first search establishes a monochromatic antipodal connection; the direct witness validator checks its returned path. Tests also compare reference search with a separate simple-path enumeration on small fixtures.

## Collection and evidence

The pilot contains one user-pasted response per model and graph. Fresh chats with no browsing or tools were instructed, but those conditions, exact model versions, hidden settings and generation times were not independently confirmed. Unknown metadata remains null.

The workload was reduced from 120 planned trials to 20 after two responses had been observed, so this was not a preregistered study. Earlier uncertain-model practice was excluded. A collection-order deviation and a user-corrected transcription are preserved in the [collection history](docs/collection-history.md) and source records.

## Scoring and reproducibility

Three outcomes must remain distinct:

1. **Displayed-path correctness:** direct mathematical checks on the submitted path. For prose-plus-JSON replies, the audit separately checks the final JSON line. This is a diagnostic check of the displayed solution, not a replacement for the original parser score.
2. **JSON-only compliance:** whether the entire response parses as strict JSON. Duplicate keys and nonstandard constants are rejected.
3. **Frozen parser path validity:** whether the original extraction policy can recover a valid path. It permits direct JSON or one whole-response fenced JSON block; it does not strip arbitrary prose.

The diagnostic final-line check is explicitly documented separately from the unchanged formal extraction rule. The four explanatory Claude replies fail automatic extraction under that rule while still containing mathematically valid paths. Reporting them as four incorrect mathematical solutions would conflate parsing with reasoning.

The audit resolves the retained-record mappings and correction, checks prompt/record fingerprints, verifies model-label consistency, recomputes outcomes from complete raw replies, and emits a source hash inventory. Stored scores and manually updated progress counters are not accepted as ground truth.

Run from the repository root with Python 3.10+:

```sh
python3 -m hypercube audit-pilot
```

This rebuilds [audit.json](results/pilot-20/audit.json) and [audit.csv](results/pilot-20/audit.csv). To verify the checked-in outputs without rewriting them:

```sh
python3 -m hypercube audit-pilot --check
python3 -m unittest discover -v
```

Reproducibility here means recalculating results from the preserved dataset and pasted replies, not reproducing the providers' original sampling.

## Interpretation and limits

Both models passed displayed-path checks on Q3 (5/5 each) and Q4 (5/5 each). ChatGPT's replies passed JSON-only checks on Q3 and Q4 (5/5 each); Claude's passed on Q3 in 1/5 and Q4 in 5/5. Dimension was not isolated experimentally: prompt size, order and other conditions also differ. No causal effect of dimension is inferred.

The result is consistent with these small instances being insufficient to distinguish mathematical performance, but it does not prove equal capability or explain why Claude supplied extra prose. There is one observed response per model/graph, related graph structures, unknown settings, prior researcher exposure to prompts and solutions, and no authenticated provider trace. No statistical significance or population-level accuracy claim is made.

The AI safety connection is evaluation reliability: independently checking a mathematical witness and distinguishing answer validity from formatting and extraction. The pilot does not measure alignment or real-world safety performance.

## What this contributes and what comes next

This study contributes a reproducible evaluation workflow grounded in hypercube graph theory. It separates the validity of a mathematical solution from formatting and extraction, with independently checked paths and preserved response evidence. On these instances, both model selections produced valid paths; the observed difference was in formatting.

The next useful decision is whether a harder study is worth its collection cost. A follow-up could first assess instance difficulty offline and then freeze a separate protocol with full provider logs and exact model identifiers when available. More trials are not needed to finish this pilot, and follow-up results should not be pooled silently with it.

Source attribution and AI assistance are documented in the [provenance notes](docs/provenance.md).
