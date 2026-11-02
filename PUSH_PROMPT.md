# Prompt for the LLM that publishes this folder to GitHub

You are given the folder `cbdc-dataset-v11/` (this file is inside it). Publish it as a NEW GitHub repository exactly as it is. Do not add, rename, reformat or "improve" any file; do not add a build system, CI, package.json, or extra documentation. The repository must stay this clean.

Steps:

1. Create a new repository `cbdc-dataset-v11` under the user's GitHub account (ask for the account name if unknown; the owner is Martin Bok). Visibility: **public** if GitHub Pages is wanted on a free plan, otherwise private (Pages on a private repo needs a paid plan). Do not initialise it with a README, licence or .gitignore — the folder already has them.
2. In the folder, replace the placeholder `https://github.com/OWNER/cbdc-dataset-v11` with the real repository URL in these files only: `site/features.html`, `site/paper.html`, `site/pipeline.html`, `site/method.html` (plain text replace of `OWNER`). Nothing else changes.
3. Delete this file (`PUSH_PROMPT.md`) — it is instructions for you, not part of the repository. Then initialise git in the folder, commit everything in ONE commit with the author identity `Martin Bok <bok@cbdcdataset.org>` and the message:
   `v11 work in progress: frozen corpus registry, measurement contract v1.1, extraction pipeline, mock website`
   Push to `main`.
4. Enable GitHub Pages: Settings → Pages → Source "Deploy from a branch" → branch `main`, folder `/site`. Wait for the deployment, open `<pages-url>/map.html` and confirm that the world map renders with the stacked chart under it, that the yellow "Mock-up" banner is visible, that the year slider recolours the map, and that `<pages-url>/map.html?project=NO` opens the Norway panel tagged "real · verified quotes".
5. Report back: repository URL, Pages URL, the commit hash, and the output of `git ls-files | wc -l` (expected 38 files; the folder is about 2.5 MB — the largest file is `site/assets/vendor/countries-50m.json`).

Rules: never commit API keys, tokens or PDFs (the `.gitignore` already excludes `*.pdf`); if any file in the folder looks like it contains a credential, stop and report it instead of pushing. Do not run any of the scripts in `scripts/extraction/` — they call paid APIs. Do not change `site/assets/data.json`; it is generated and intentionally contains mock values labelled `"provenance": "MOCK"`.
