# Provenance and contribution record

## Research ownership

This is Deborah Ologundudu's thesis-connected pilot project, developed collaboratively with AI assistance at the user's request. The user chose to pursue a distinct study with their own generated data and verified evaluation pipeline. The concrete protocol and implementation were developed with Codex; the study has not yet collected model responses or established a novel scientific result.

The project should be described as an AI-assisted research project led by the researcher, not as entirely unaided code authorship or a newly proved mathematical theorem. The researcher should inspect, run and understand the verification before presenting experimental conclusions.

## Background inspected locally

- Deborah Ologundudu, *Combinatorial Properties of Hypercubes*, master's thesis, Silesian University of Technology, 2026: definitions of antipodal vertices/edges/colorings, ordinary paths versus geodesics, and computational methods in Chapters 3–4. Local thesis/defense material was read as reference. No thesis source or private institutional identifiers are bundled here.
- The thesis describes reproducing another group's published SAT implementation for part of its computational work. Its reference list includes M. Kirchweger, T. Peitl, B. Subercaseaux and S. Szeider, *From the Finite to the Infinite: Sharper Asymptotic Bounds on Norin's Conjecture via SAT*, arXiv:2511.08386 (2025). This bibliographic entry is transcribed as thesis background, not independently verified publication metadata or an attribution of this project's code. The thesis excerpts inspected do not identify the exact repository URL; none is invented here. Confirm that URL and attribution before describing a specific repository publicly.

No external theorem's present proof status is needed for inclusion: each small instance has an explicitly checked witness. Mathematical background is not claimed as this project's discovery. A scientific-priority claim would require a separate literature review.

## Component origins

| Component | Origin and role |
|---|---|
| Protocol and pilot design | Developed in this project from the thesis connection and user discussions, with AI assistance |
| Cube generator and hash-based sampling | Implemented afresh in this project; new deterministic instances |
| Topology and witness validation | Implemented afresh; topology derived by Hamming-distance checks independently of generation |
| Reference search | Fresh implementation of established breadth-first search, not a novel algorithm |
| Test-only simple-path search | Fresh exhaustive depth-first check of small fixtures |
| Response parsing, attempt provenance and scoring | Implemented afresh for this protocol |
| Dataset and reference certificates | Computed by this project's generator/search, then directly checked |
| Model response records and conclusions | Not yet collected; no experimental findings claimed |
| Documentation and tests | Prepared with AI assistance; supplied for independent inspection |

No earlier repository code, CNF encodings, SAT solver outputs, stored cubes, external datasets or third-party runtime packages were copied, adapted or introduced. The earlier SAT repository itself was not inspected for implementation. The previous graph-coloring portfolio is separate and was not modified.

## Reproduction and integrity

`data/manifest.json` records seed, algorithm version, candidates and fingerprints. Prompts are built from instance fields alone. Independent constraints verify reference paths; tests separately enumerate simple paths on small fixtures. The generated Q3 dataset logs a naturally duplicated candidate as an exclusion, not an experimental failure.

Tests use synthetic response strings and provider/model labels as fixtures. They are not model-generated experimental records. Real response logs start empty. Keep this distinction in any report.

## Before making results public

Record and freeze actual model identifiers/settings before collection, retain all responses and transport attempts, and preserve the original dataset and prompt hashes. Credit sources when discussing the thesis's reproduced work; disclose AI assistance and public dataset exposure. Do not claim that new code establishes scientific novelty or that this pilot measures general safety.

## Manual-app selection before collection

The user reported `GPT 6` for ChatGPT and `Sonnet 5.5` for Claude. These labels are retained exactly as supplied, with exact provider identifiers left null. No independent check of their availability, model routing or hidden settings was performed. This label-based cohort must not be described as an exact-model/API evaluation. The protocol was amended before responses were collected; no mathematical instance or prompt changed.

## Completed manual pilot

Twenty user-pasted responses were collected for ten selected graphs, with labels `Gpt 6.1 Sol Light` and `Sonnet 5.5`. The original 120-trial proposal was reduced after two responses had been seen. All amendments, excluded practice, collection-order deviation and the user-corrected Claude q3-04 paste are retained. No API calls or authenticated provider traces are represented. Exact IDs, original generation times, hidden settings and most context/tool controls remain unknown.

`hypercube/pilot_audit.py` was freshly implemented with AI assistance to rebuild the amended results. It resolves retained source mappings and the transcription correction, recomputes strict scores from raw replies, and separately checks the final JSON line for diagnostic displayed-path validity. The latter is explicitly separated from the frozen extraction policy; extraction failures must not be described as incorrect mathematical paths. `results/pilot-20/` is authoritative for the completed study; earlier collection snapshots are historical.
