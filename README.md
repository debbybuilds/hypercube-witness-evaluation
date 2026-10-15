# Verifying LLM Solutions to Hypercube Coloring Problems

A thesis-connected evaluation pilot asking whether language models can construct valid mathematical witnesses on small hypercubes, with every submitted path checked directly.

**Status: local pilot toolkit built; manual-app labels selected; no model responses collected and no model performance results yet.** There are 20 fixed instances, separate reference paths, and a randomized schedule for 120 planned responses. This is a newly implemented project, not a fork or wrapper of the SAT repository used for part of the thesis's computational reproduction.

## Why this study

A model can produce plausible or correctly formatted mathematics without producing a valid solution. Here the requested solution is concrete: a sequence of vertices forming a monochromatic path between antipodes of a colored hypercube. Every adjacency, color, endpoint and repeated vertex is checkable.

The intended research contribution is the evaluation protocol, newly generated dataset, prospectively collected responses, and analysis of verified performance. Hypercube definitions, antipodal coloring, and breadth-first search are established mathematics and algorithms. A fresh implementation does not by itself establish scientific novelty.

This builds on Deborah Ologundudu's master's thesis, *Combinatorial Properties of Hypercubes*, especially its definitions and computational investigation. The thesis also reproduced published SAT work; that work must retain its original credit. This project uses a fresh generator, direct constraint checks and graph search, with no external SAT solver, copied encodings or stored solver artifacts. See [provenance](docs/provenance.md) and the [approved protocol](docs/experiment-spec.md).

## The task

Vertices of Q_n are binary strings of length n. An edge changes one bit. The antipode complements all bits. Each edge is colored 0 or 1, and an edge and its antipodal edge have opposite colors.

Given the complete colored edge list, the model must return a **simple monochromatic path between any antipodal pair**. The path need not be shortest: this is an ordinary-path task, not a geodesic task. All 20 included colorings have independently checked reference paths.

The pilot contains 10 distinct labeled colorings of Q3 and 10 of Q4. Distinct does not mean non-isomorphic or statistically independent. Three trials for each of two models produce 120 scheduled response slots.

## Run locally

Python 3.10 or later; no dependencies, network, API keys or model calls.

```sh
python3 -m unittest discover -v
python3 -m hypercube verify --dataset data
python3 -m hypercube score --dataset data --attempts responses/attempts.jsonl --output results/summary.json
```

The supplied attempts file is empty. Its summary explicitly says **no responses collected**; observed response rates are null. A zero collection-progress fraction is not a measured accuracy.

To reproduce the dataset without overwriting the supplied copy:

```sh
python3 -m hypercube generate --output /tmp/hypercube-pilot-reproduction
python3 -m hypercube verify --dataset /tmp/hypercube-pilot-reproduction
```

Generation uses seed `hypercube-pilot-v1`. For each antipodal edge pair, the color of the lexicographically smaller edge is the low bit of the first SHA-256 digest byte. Hash input is a compact UTF-8 JSON array `[seed,n,candidate,[u,v]]`. The other edge gets the opposite color. Candidate numbering starts at zero independently per dimension; exact duplicate colorings are logged and excluded. An unexpected no-path candidate stops generation for investigation.

File hashes and accepted/excluded candidates are in `data/manifest.json`. Schedule slots are ordered by SHA-256 of compact JSON `[seed,slot_id]`, providing a fixed pseudorandom order. Generated files contain no timestamps. Validation checks every graph and certificate directly, fingerprints all files, and checks byte-for-byte reproduction of the frozen protocol.

## Collect responses

1. The user selected manual collection with user-reported app labels **GPT 6** (ChatGPT/OpenAI) and **Sonnet 5.5** (Claude/Anthropic). The saved configuration uses `collection_mode: "manual_app"`, `identity_resolution: "display_label_only"`, the literal `display_label`, and `model_id: null`. Unknown settings are null. Freeze and retain this configuration before collection. This exploratory variant cannot identify exact underlying model versions or hidden app settings. An exact-version study instead requires provider-supplied identifiers and a separately documented configuration; never invent an ID from a display label.
2. Follow `data/schedule.json` in order. For each slot, open a fresh context, disable tools and browsing, and send the exact matching file from `data/prompts/`. Do not send reference paths, previous responses, hints or correctness feedback.
3. Capture the **complete raw response**, displayed label and identity-resolution status, actual UTC timestamp, requested/returned settings, prompt hash, and context/tool policy. Preserve refusals and truncated or malformed responses as received outcomes. Do not delete failures or retry received answers.
4. Copy the field structure from `responses/attempt-template.json`, replace every placeholder, and append one compact JSON object per line to `responses/attempts.jsonl`. The template is documentation, not a trial record. Raw responses may contain newlines encoded as `\n` within the JSON string. Do not manually normalize responses into JSON answers.
5. For a transport failure, record `status: "transport_error"`, `raw: null`, and an error description without credentials or private request data. A replacement must have a new attempt ID and point to the immediately preceding failed attempt using `replaces_attempt_id`. Only transport failures may be replaced; keep the whole chain in file order.
6. Run scoring. Nonempty collections require both model slots to be configured and must match their frozen identity records and requested settings exactly (including null when unknown). Manual-app records preserve display labels and null exact IDs, and the report explicitly carries the identification limitation. Returned settings are retained separately and are not assumed to equal requested settings. For another config location use `--models PATH`. Scoring rejects unknown slots, mismatched prompt hashes, duplicate attempt IDs, changed model identifiers and unlinked retries.

The toolkit makes no API calls and does not automate collection. Public instances can become contaminated; run the pilot without external retrieval, record the conditions, and disclose public exposure in future reuse.

## What is scored

Three measures are kept separate:

- **JSON-only:** the complete response parses as strict JSON. Duplicate keys and nonstandard constants are rejected.
- **Exact schema:** the parsed object has only `path`, whose value is a list of strings. Vertex correctness is checked mathematically.
- **Valid path:** the listed vertices form a simple, adjacent, monochromatic path with antipodal endpoints.

One fenced JSON object occupying the whole response can be scored for path validity but fails JSON-only compliance. Extra object fields fail exact schema compliance while a valid path may still pass. Arbitrary prose is not stripped to salvage JSON. Mathematical failures include malformed responses, refusals and empty received text.

For each model and dimension, the report includes planned, received, never-attempted, unresolved transport-failed, correct, and total transport-error event counts. `planned = received + never_attempted + transport_failed`. Observed rates use received responses only. `correct_per_planned_collection_progress` is coverage progress, not model accuracy. The complete attempt history and source-file hashes remain in the scored output.

Repeated trials are clustered by instance. Small dimensions may produce ceiling performance; this pilot is not designed to establish general superiority, a causal reasoning mechanism, or safety/alignment performance. Its safety relevance is evaluation reliability: using independently checked evidence instead of trusting output presentation.

## Layout

| Location | Purpose |
|---|---|
| `hypercube/validation.py` | Independent topology, antipodal coloring and path checks |
| `hypercube/search.py` | Reference breadth-first monochromatic search |
| `hypercube/generation.py` | Fresh deterministic dataset and prompt generation |
| `hypercube/scoring.py` | Strict parsing, trial validation and metric calculations |
| `hypercube/dataset.py` | Saved-artifact integrity and reproducibility checks |
| `tests/` | Hand-checked fixtures, adversarial inputs, independent path search and CLI tests |
| `data/instances/`, `data/prompts/` | Frozen graph inputs and solution-free prompts |
| `data/reference/` | Reference certificates; never include in model inputs |
| `responses/` | Model configuration, record template and empty response log |
| `results/summary.json` | Empty-collection summary, not experimental findings |

Implementation and documentation were prepared with AI assistance. The code and tests are available for inspection and explanation; do not describe every line as manually written by the researcher. No license has been selected; public reuse permission is not granted by this initial local version.
