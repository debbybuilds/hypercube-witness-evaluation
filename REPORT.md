# Valid hypercube paths, different formatting outcomes

**A thesis-connected feasibility pilot · 15 October 2026**

## Finding

In this 20-response manual-app pilot, both model selections supplied valid monochromatic antipodal paths on all ten graphs. The responses attributed to ChatGPT followed the JSON-only instruction in 10/10 cases; those attributed to Claude did so in 6/10. The remaining four Claude replies included explanations followed by valid JSON path objects.

This pilot therefore found no difference in displayed-path correctness on the selected instances. It found a difference in formatting compliance in these particular pasted responses. It does not establish general model superiority or a mathematical failure mechanism.

| Measure | ChatGPT, displayed label “Gpt 6.1 Sol Light” | Claude, displayed label “Sonnet 5.5” |
|---|---:|---:|
| Received responses | 10/10 planned | 10/10 planned |
| Displayed paths independently verified as valid | 10/10 | 10/10 |
| Complete response satisfies JSON-only requirement | 10/10 | 6/10 |
| Valid path recovered by the frozen response parser | 10/10 | 6/10 |

The names above are user-reported app labels, not independently verified provider version identifiers. The source material is user-pasted output rather than authenticated provider traces.

## Question and connection to the thesis

Can language models construct mathematical witnesses whose validity can be checked independently of their explanations?

This study builds on Deborah Ologundudu's master's thesis, *Combinatorial Properties of Hypercubes*, specifically its treatment of antipodal colorings and computational verification. For each instance, the model receives a complete colored hypercube and must supply a simple monochromatic path between some antipodal pair.

The new work is an AI-assisted implementation and evaluation study: a fresh generator, new instances, reference search, witness validation, saved prompts, response records and an auditable analysis. The earlier SAT repository used in part of the thesis's reproduction is not this project's codebase. Hypercube theory, graph search and independent constraint checking are established methods; scientific novelty is not claimed merely because the implementation is fresh. See [provenance](docs/provenance.md).

## Task and instances

Vertices of the n-dimensional hypercube are n-bit strings. Adjacent vertices differ in one bit, and antipodes complement every bit. Every edge has color 0 or 1; antipodal edges receive opposite colors. A submitted path must use listed edges, contain no repeated vertex, have one color throughout, and join antipodal endpoints.

Any qualifying simple path is accepted. It need not be a shortest path or geodesic, and the model may choose the antipodal pair.

The active pilot uses instances q3-01 through q3-05 and q4-01 through q4-05: five labeled colorings of Q3 and five of Q4. Each model has one response per graph. Q3 has 8 vertices and 12 edges; Q4 has 16 vertices and 32 edges.

The original toolkit generated ten colorings per dimension. Color selection uses the documented seed `hypercube-pilot-v1` and SHA-256 over canonical antipodal edge pairs. The generator logs duplicate candidates. An independent topology validator derives adjacency from Hamming distance, separately from generation. A reference breadth-first search establishes a monochromatic antipodal connection; the direct witness validator checks its returned path. Tests also compare reference search with a separate simple-path enumeration on small fixtures.

## Collection history and amendments

The initial proposal contained 120 trials: 20 graphs, two models and three repetitions. Early practice responses had uncertain ChatGPT model identity and remain excluded. The user then reported “Gpt 6.1 Sol Light” and restarted collection with that label; the Claude label remained “Sonnet 5.5.”

After two restarted responses had been seen, the user approved reducing the workload to 20 responses. The selected graph IDs are the first five in each dimension, and the two existing responses were retained. Their original slot and repetition identifiers are preserved and mapped into the revised plan. Selection was not preregistered; the amendment occurred after results were available.

The revised order retains those two responses, then proceeds through selected graphs and model pairs. Claude's q3-02 response arrived before ChatGPT's because the assistant initially named the wrong model in its instructions. That deviation is retained. The user later corrected a mistaken paste for Claude q3-04; both versions are preserved, and the explicit correction map selects the actual response. This is a transcription correction, not an additional or selectively retried model trial.

Fresh chats and no tools or browsing were instructed for each collection step. Those conditions, exact model versions, hidden settings and original generation times are not independently confirmed. Unknown metadata stays null; receipt times are not presented as generation times. These incomplete records are audited as manual intake and are not silently promoted into the stricter original attempt log.

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

The completed contribution is an inspectable feasibility study, including honest documentation of protocol changes, model-identity uncertainty, a collection-order mistake and a transcription correction. It demonstrates a working verification pipeline without manufacturing a performance gap.

The next useful decision is whether a harder study is worth its collection cost. A follow-up could first assess instance difficulty offline and then freeze a separate protocol with full provider logs and exact model identifiers when available. More trials are not needed to finish this pilot, and follow-up results should not be pooled silently with it.
