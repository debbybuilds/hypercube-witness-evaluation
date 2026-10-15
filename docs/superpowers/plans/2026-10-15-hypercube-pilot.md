# Hypercube Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution, or superpowers:subagent-driven-development if the user chooses delegation. Steps use checkbox syntax for tracking.

**Goal:** Build the approved, reproducible hypercube evaluation kit without collecting model responses or publishing it.

**Architecture:** Separate instance generation, direct validation, reference search, and response scoring. The generator must pass its output through independent validation; reference paths never enter prompt generation. A small command-line interface generates, verifies, and scores local files.

**Tech Stack:** Python 3.10+, standard library, unittest, local Git repository.

**Spec:** ../../experiment-spec.md (relative to this plan).

## Global Constraints

- Use Python 3.10+ and the standard library only.
- Generate 10 distinct labeled colorings for each of n=3 and n=4.
- Use the fixed seed `hypercube-pilot-v1`.
- Any qualifying simple path is accepted. It need not be a geodesic and need not begin at a specified vertex.
- No API calls, costs, credentials or model collection are part of this implementation stage.
- No changes to the thesis files or previous portfolio repository. No publication of this new project until requested.
- Implement afresh from definitions; do not copy, fork, translate, adapt, or wrap the earlier author's repository, encodings, stored artifacts or results.
- Attribute mathematical background and thesis reproduction accurately; disclose AI assistance and distinguish a new evaluation study from a claim of scientific novelty.
- Keep reference paths separate from prompts; record hashes, candidate exclusions, and missing trial data explicitly.

## Review Focus

- Boolean values masquerading as integer colors must fail validation.
- A valid non-geodesic path must pass; a repeated-vertex walk must fail.
- Reversed or repeated edges must not bypass topology validation.
- Missing responses, empty received responses, and transport failures must remain distinct.
- Duplicate JSON keys, fenced JSON, and extra schema fields require separate mathematical and formatting outcomes.

## File and data contracts

- `hypercube/validation.py`: `validate_instance(instance: dict) -> None` raises descriptive ValueError; `check_path(instance: dict, path: object) -> dict` returns `valid` and `reason` after validating the instance.
- `hypercube/search.py`: `find_path(instance: dict) -> list[str] | None`, breadth-first search of each monochromatic subgraph, checked against the direct verifier.
- `hypercube/generation.py`: `make_instance(n: int, candidate: int, seed: str) -> dict`, `make_prompt(instance: dict) -> str`, `build_dataset(output: Path) -> dict`.
- `hypercube/scoring.py`: `score_response(instance: dict, raw: str) -> dict`, `summarize(schedule: list, attempts: list, instances: dict) -> dict`.
- `hypercube/__main__.py`: commands `generate --output DIR`, `verify --dataset DIR`, `score --dataset DIR --attempts FILE --output FILE`.
- `tests/`: independent topology fixtures, invalid-input checks, independent simple-path enumeration, parser/denominator tests, and a temporary-directory end-to-end test.
- `data/instances/`, `data/prompts/`, `data/reference/`: instance JSON, exact prompt text, and reference JSON respectively. `data/manifest.json` records all file SHA-256 hashes, seed, generator version, accepted candidates, exclusions, and the schedule hash.
- `data/schedule.json`: 120 unique slots, model labels `model_a`/`model_b`, instance ID and trial 1–3. Sort slots by SHA-256 of seed plus canonical slot identity for a deterministic pseudorandom order.
- `responses/model-config.json`: two explicit unconfigured model slots; collection requires exact provider/model identifiers. `responses/attempts.jsonl` starts empty; a separate documented template shows required attempt metadata.
- Instance schema: `id`, `n`, `edges` (sorted `[u,v,color]` triples), generation seed/candidate/version. IDs are assigned after unique candidates are accepted, independent of trial order.
- Each attempt has a unique attempt ID and slot ID, `status` (`received` or `transport_error`), raw response or transport-error detail, provider/model ID, UTC timestamp, requested/returned settings, prompt hash, tool policy, fresh-context flag, and optional replaced-attempt ID. Reject unknown slots, mismatched prompt hashes, duplicate IDs, branching replacements, or multiple unlinked attempts for one slot. Preserve all attempts. The last attempt in an explicit replacement chain is the effective slot outcome; separately retain total transport-error events.
- An unresolved transport-error slot is reported separately from a never-attempted slot. For each model/dimension, planned = received + never-attempted + unresolved-transport-failed. A received empty string is an incorrect received response. No received responses means observed rates are null, not zero. Correct/planned is labeled collection progress, never model accuracy.

## Task 1: Independent instance and path validation

**Files:** `hypercube/__init__.py`, `hypercube/validation.py`, `tests/__init__.py`, `tests/test_validation.py`.

- [ ] Write tests before implementation: a hand-constructed antipodal Q2 coloring with valid path `['00','01','11']`; expected edge counts 12 for Q3 and 32 for Q4; direct rejection of mixed-color, nonadjacent, wrong-antipode, repeated-vertex and malformed paths.
- [ ] Add fixture-based tests for missing/duplicate/reversed edges, self-loops, invalid n, nonbinary colors, Boolean colors, and broken antipodal pair colors. Include one hand-checked longer-than-n valid simple antipodal path on a small valid coloring.
- [ ] Run `python3 -m unittest discover -v`; confirm missing validation behavior fails before implementation.
- [ ] Implement the specified interfaces. Derive topology by independently enumerating all binary-string pairs at Hamming distance one; do not import generation or reference search. Use explicit exceptions rather than assertions for input validation.
- [ ] Run the whole test suite; require all cases pass. Initialize the local repository with `.gitignore` excluding caches, environments and credentials, then commit this deliverable using an appropriate configured author identity.

## Task 2: Reference search and reproducible dataset

**Files:** `hypercube/search.py`, `hypercube/generation.py`, `tests/test_generation.py`, `tests/test_search.py`.

**Consumes:** Validation and witness interfaces from Task 1.

- [ ] Write tests first: generated instances satisfy complete topology and antipodality; generation is deterministic; the 20 accepted colorings are distinct within each dimension; injected duplicate candidates are recorded as exclusions; a no-path result stops generation.
- [ ] Add a second search implemented only in tests that enumerates simple monochromatic paths on fixed Q3 fixtures; compare existence with breadth-first reference search. Verify every returned certificate with direct path validation.
- [ ] Run the suite and observe missing generator/search behavior fail.
- [ ] Implement `find_path` using fixed iteration order and predecessor reconstruction. Implement canonical antipodal edge pairing and SHA-256 color selection. Serialize hash inputs as compact UTF-8 JSON arrays; color is the low bit of the digest's first byte. Store the exact algorithm version and hash inputs in documentation.
- [ ] Implement prompt rendering from validated instance fields only. Describe any simple antipodal monochromatic path as acceptable; use `{"path":["<vertex>","..."]}` as schematic format, with no worked path. Prompt tests vary or remove reference files and confirm prompt bytes are unchanged.
- [ ] Build the 20-instance dataset, reference certificates, prompts, 120-slot schedule and manifest. Test regeneration to a second temporary directory yields identical bytes for every file, including schedule and manifest. Commit after all tests pass.

## Task 3: Response parsing and honest denominators

**Files:** `hypercube/scoring.py`, `tests/test_scoring.py`, `responses/model-config.json`, `responses/attempt-template.json`, `responses/attempts.jsonl`.

**Consumes:** Direct path validation and manifest/slot contracts.

- [ ] Write tests first: valid direct JSON passes all three measures; one whole-response JSON fence fails JSON-only but passes schema/path; extra fields fail schema but retain path validity; prose-wrapped JSON, duplicate keys, NaN, invalid types, and refusals fail appropriate checks.
- [ ] Write denominator tests: 120 empty slots produce 0 received and null observed rates; received empty strings count as received failures; an unresolved transport error is distinct from an unattempted slot; a linked successful replacement counts once and retains the error event. Duplicate IDs, hash mismatches and unlinked retry attempts raise descriptive errors.
- [ ] Run tests and confirm missing parsing/summary behavior fails.
- [ ] Implement strict parsing, narrow fence recovery, path scoring, attempt validation and summaries. Never infer model IDs or unknown settings; allow explicit unknown metadata where the protocol permits it. Implement empty collection templates without fabricating responses.
- [ ] Run the full suite; commit only on success.

## Task 4: CLI, documentation and complete local verification

**Files:** `hypercube/__main__.py`, `tests/test_cli.py`, `README.md`, `data/`, `docs/experiment-spec.md`, `docs/provenance.md`.

**Consumes:** Dataset generation, direct checks, scoring and summaries.

- [ ] Write a CLI integration test first: generate into a temporary directory, verify all 20 instances/reference certificates plus prompt/schedule hashes, then score an empty attempts file with zero received outcomes and null observed rates. Alter one generated file and require verification to fail with a useful diagnostic and nonzero exit status.
- [ ] Run tests and observe absent CLI behavior fail.
- [ ] Implement the three local commands. Give argparse errors for missing files/malformed JSON; do not print fictitious research results. Limit scoring output to supplied attempts.
- [ ] Write README instructions for generation, verification, unittest, model configuration, fresh-context manual collection, attempt import and scoring. Explain 120 planned responses, any-path/geodesic distinction, thesis connection, AI assistance, limitations, and that no model measurements exist yet. Link the approved protocol and reference files.
- [ ] Create `docs/provenance.md` identifying freshly implemented components, newly generated data, standard algorithms, AI assistance and background sources. Check original repository authorship and URL in thesis references before citing it. Review the README so the user's evaluation contribution is explicit and the thesis's reproduced third-party work is not presented as theirs. Do not claim personal authorship of every line or scientific priority.
- [ ] Run `python3 -m unittest discover -v`, `python3 -m hypercube generate --output data`, `python3 -m hypercube verify --dataset data`, and empty-response scoring. Independently compare regenerated files and verify no reference data is embedded in prompts. Run `git diff --check` and a credential/private-path scan of tracked files.
- [ ] Review the implementation against every spec section and fix uncovered requirements. Commit verified local files. Deliver links and test evidence; do not create a GitHub repository or contact models in this stage.

## Plan review

Native implementation is recommended: these four tasks share small, tightly coupled data contracts, and no external integration is required. The user approved native implementation after clarifying fresh authorship. No subagents are authorized by this document alone.
