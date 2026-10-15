# Verifying LLM Solutions to Hypercube Coloring Problems

Status: pilot scope approved by the user on 15 October 2026; authorship requirements clarified afterward. Implementation approved and in progress. No model responses collected.

## Purpose and thesis connection

Build a reproducible pilot grounded in the definitions and computational approach of Combinatorial Properties of Hypercubes, especially Chapters 3 and 4. Evaluate whether models can construct a mathematical witness whose validity can be checked independently. This extends graph-theoretic verification methods into AI evaluation; it does not test alignment or establish broad model superiority.

The thesis studies antipodal edge-colorings. The previous portfolio instead studied vertex 3-coloring. This project uses the thesis's edge-coloring setting directly. No novel theorem or counterexample is claimed.

## Ownership, attribution and research contribution

The user's priority is a distinct project they can accurately present as their own research work. The thesis used another author's published repository for part of its computational reproduction. That repository is background, not the implementation base for this project. Do not copy, fork, translate, adapt, or wrap its implementation, SAT encodings, stored search artifacts, or results. Do not imply that reproduced work in the thesis was an original implementation.

Implement the generator, validators, reference search, dataset builder and scoring tools afresh from the mathematical definitions and this protocol. Use newly generated instances, newly recorded model responses, and independently computed reference paths. Standard algorithms such as breadth-first search are established methods, not novel algorithms claimed by this project.

The intended contribution is a new, reproducible evaluation study: its research question, task protocol, generated dataset, response records, validation pipeline and analysis. New implementation does not by itself establish scientific novelty; no first-of-its-kind claim is made without a literature review. Cite the thesis and relevant mathematical sources. Identify the earlier repository accurately if discussed as background, after its URL and authorship have been checked in thesis references; do not invent a citation.

Maintain `docs/provenance.md` recording each project's component origin, relevant background sources, any third-party code actually introduced, and AI assistance. State that implementation and documentation were prepared with AI assistance. Do not imply that the user personally wrote every line; support ownership through inspectable code, tests, explanations, and the user's research decisions. Avoid copying thesis text or publishing its private identifiers or full contents.

## Mathematical task

Vertices of Q_n are length-n binary strings. An undirected edge joins strings differing in exactly one coordinate. The antipode of a vertex is its bitwise complement; the antipodal edge complements both endpoints. Every edge has color 0 or 1, and antipodal edges must receive opposite colors.

Given the complete colored edge list, return a simple path joining any vertex to its antipode, with every edge on the path having the same color. Any qualifying simple path is accepted. It need not be a geodesic and need not begin at a specified vertex. A path contains at least two vertices, has no repeated vertex, and uses only listed edges.

## Fixed dataset

Use Python 3.10+ and the standard library only. Generate 10 distinct labeled colorings for each of n=3 and n=4. Canonicalize vertex strings and undirected endpoint pairs lexicographically. List every edge exactly once. Group edges into antipodal pairs and choose one binary color per pair, assigning its complement to the other edge.

Use SHA-256 of a documented seed, dimension, candidate number and canonical edge-pair label to derive each pair's color. Use the fixed seed `hypercube-pilot-v1`. This avoids relying on unspecified random-generator behavior. Record candidate numbers, seed, generation algorithm version and instance fingerprints. Reject exact duplicate colorings within a dimension; do not claim non-isomorphism or statistical independence.

An independent validator must check complete topology, unique edges, binary color domains and the antipodal rule. A monochromatic connectivity search must establish an antipodal path before an instance is included. Record every exclusion and its reason; do not silently replace failures. If any candidate lacks a qualifying path, stop generation for investigation rather than assuming the relevant theorem or resampling it away.

## Verifier and reference search

The witness verifier consumes an instance and a JSON path. It checks vertex syntax, dimension, distinctness, adjacency, monochromaticity and antipodal endpoints directly. It does not trust the generator or model's declared status. Return explicit reasons for rejection.

The reference search uses breadth-first search in each color subgraph to find an antipodal connection. Acceptance is independently checked by the witness verifier. A second exhaustive simple-path search cross-checks existence on Q_3 fixtures. Tests include known valid examples and adversarial paths: mixed colors, missing edges, wrong antipodes, repeated vertices, malformed binary strings and Boolean values where strings are required. Instance validation tests cover missing/duplicate edges, self-loops, wrong dimensions, nonbinary colors and antipodal-rule violations.

Reference paths are stored under `reference/`. Model prompts are generated only from instance fields, never from reference files. The public repository is not a confidential test set: run models without browsing or tools, record that policy, and disclose possible contamination in later uses.

## Prompt and response format

Use one fixed prompt template describing the definitions above and the full edge list. Request exactly one JSON object of the form `{"path":["000","001","011","111"]}` (example shape only; actual prompt uses placeholders rather than a worked solution). Do not require a claim of SAT or UNSAT: every included instance has a checked path.

Store exact prompt text and its SHA-256. Do not include solutions, trial-specific hints or feedback. Prompt size differs by dimension; do not interpret dimension differences as a pure reasoning effect.

## Trial protocol

Plan two models, three independent trials per instance: 120 planned responses. Exact provider model identifiers must be entered before collection; do not substitute product names. Record provider, model ID, UTC timestamp, requested and returned settings, tool policy, prompt hash, instance ID, trial number and raw response. Mark unavailable settings as unknown. Use fresh contexts, fixed prompts and a saved randomized trial schedule. No feedback or selective retries.

Record transport errors separately. A replacement request must preserve the failed attempt and be labeled as a replacement; model refusals, incomplete answers and malformed outputs remain outcomes. No API calls, costs, credentials or model collection are part of this implementation stage. Provide an empty response template and manual import/scoring instructions.

## Scoring

Report JSON-only compliance, exact schema compliance and verified path validity separately. The primary mathematical measure is the fraction of received responses yielding valid paths, with a fixed extraction policy: parse a JSON object directly or recover exactly one fenced JSON object occupying the whole response. Fenced JSON fails JSON-only compliance. Do not extract JSON from arbitrary prose. Reject duplicate JSON keys and nonstandard constants. A mathematically valid path can pass mathematical scoring despite extra object fields; extra fields fail exact schema compliance.

Report planned, received, missing, transport-failed and mathematically correct counts for each model and dimension, plus the observed-response denominator. Also report correct/planned as collection coverage progresses, clearly labeling missing outcomes rather than silently treating them as model errors. No results are displayed as measured until responses exist. Repeated trials on one instance are clustered observations; no significance or general ranking claims are planned for this pilot.

## Deliverables and acceptance

Deliver a standalone local repository with README, protocol, generator, instance and witness validators, reference search, response scorer, test suite, 20 instance files, 20 solution-free prompts, reference certificates, generation manifest and empty trial records. Commands regenerate byte-identical data and validate all instances and certificates without network access. All generated reference paths pass direct checks; independent search agrees on the small fixtures. No changes to the thesis files or previous portfolio repository. No publication of this new project until requested.

## Limitations

Small dimensions may produce ceiling performance. An invalid model path does not establish a general reasoning mechanism. Generation and verifier code are AI-assisted and must be tested; computational checks are not a replacement for mathematical proof. The thesis's ordinary-path and geodesic formulations must remain distinct. A larger or adversarial study is a later protocol revision, not an unrecorded change to this pilot.
