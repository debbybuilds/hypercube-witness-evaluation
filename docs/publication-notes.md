# Publication preparation

Repository name: `hypercube-witness-evaluation`

Repository description: “Thesis-connected pilot evaluating LLM-generated hypercube paths, with independent verification, preserved response evidence and reproducible scoring.”

The local project directory remains `hypercube-llm-evaluation`; no rename is required to use the suggested GitHub name.

## Current state

The user approved public publication on 15 October 2026. Public repository: [debbybuilds/hypercube-witness-evaluation](https://github.com/debbybuilds/hypercube-witness-evaluation). The separate `llm-graph-coloring-audit` repository is a different study.

The source files, raw pasted responses, amendments, correction history, report and audit outputs are prepared for review. The author has not selected a reuse license. AI assistance and the distinction from third-party thesis reproduction are documented in `docs/provenance.md`.

For publication, describe the study as an exploratory manual-app feasibility pilot: 20 replies on ten graphs. Both models supplied valid displayed paths in all ten cases; four Claude replies contained prose and failed the JSON-only/extraction rules. Exact provider versions/settings and original generation timestamps are unknown. Do not market these records as a general model ranking, authenticated API study or new mathematical theorem.

The report's results are backed by `python3 -m hypercube audit-pilot --check` and the complete test suite. A future publication step should verify the public remote and pushed commit before claiming the project is online. Do not publish the thesis itself or introduce a license without the user's choice.
