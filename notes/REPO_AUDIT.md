# Repository audit

Read-only audit of `origin/main` at `e6f4b6ae8f5baf6e972d03d09e26cf6904f09ac2` (2026-10-07). The 9D matrix is the stated target, but the tracked corpus mapper uses hard-coded heuristic values, the two trainers form different datasets, and two non-contained branches retain distinct work. No pruning or code changes were performed; line references below are from `e6f4b6a` unless another revision is stated.

## 1. Branches

`Ahead/behind` is relative to `origin/main`; containment means commit ancestry (not merely matching patches). Branch-only paths are present in that branch's tree and absent from main.

| Branch (tip) | Ahead / behind | Contained? | Branch-only paths | Commit author classes | Purpose from commits/diff | Verdict |
|---|---:|---|---|---|---|---|
| `chore/add-sfl-pi-actions-launcher` (`88797190`) | 0 / 36 | Yes | — | Human; GitHub Actions | Adds manual SFL-pi workflow (`.github/workflows/train-sfl-pi.yml`; PR #1, head `88797190`). | ALREADY-MERGED-DELETE-SAFE |
| `ci/resume-sfl-pi-training` (`aee2ba3`) | 0 / 31 | Yes | — | Human; GitHub Actions | Diagnostic workflow stops after schema inspection (`.github/workflows/train-sfl-pi.yml`); no separate training result. | ALREADY-MERGED-DELETE-SAFE |
| `copilot/research-train-sfl-pi-workflow-issues` (`e6f4b6a`) | 0 / 0 | Yes | — | No unique commits | Same commit and tree as main. | ALREADY-MERGED-DELETE-SAFE |
| `docs/non-ceremonial-experimentation-directive` (`709efc96`) | 0 / 30 | Yes | — | Human; GitHub Actions | Adds the experimentation directive (`notes/non_ceremonial_experimentation.md`; PR #4, head `709efc96`). | ALREADY-MERGED-DELETE-SAFE |
| `feature/add-meaning-state-animation-reader` (`8d492bc`) | 1 / 27 | No* | — | Human; GitHub Actions | Adds `meaning-state.html`. Its change is also in main as `378ad6f` (PR #7); `8d492bc` itself is not an ancestor. | ALREADY-MERGED-DELETE-SAFE |
| `feature/implementation-evidence-reader` (`3f0d2cf`) | 0 / 27 | Yes | — | Human; GitHub Actions | Static implementation reader (`index.html`); its history is contained in main. | ALREADY-MERGED-DELETE-SAFE |
| `feature/olmo-core-sfl-random-init` (`e80de20`) | 0 / 7 | Yes | — | Human; Copilot SWE Agent; GitHub Actions | Adds random-initialised trainer (`train_sfl_pi.py`, `sfl_pi_model.py`; PR #3, head `e80de20`). Workflow still defaults `code_ref` to this branch (`.github/workflows/train-sfl-pi.yml:6-10`). | KEEP |
| `feature/sfl-pi-full-run-inspection` (`aebeea8`) | 0 / 33 | Yes | — | Human; GitHub Actions | Adds trajectory inspections/run artifacts (`train_sfl_pi.py:128-186,262-267`). | ALREADY-MERGED-DELETE-SAFE |
| `fix/install-pytorch-for-sfl-pi` (`f07ebde`) | 0 / 34 | Yes | — | Human; GitHub Actions | Installs/verifies PyTorch in the SFL-pi workflow (PR #2, head `f07ebde`). | ALREADY-MERGED-DELETE-SAFE |
| `fix/sfl-pi-jsonl-ingestion` (`f01114a`) | 0 / 31 | Yes | — | Human; GitHub Actions | Groups contiguous empirical JSONL states (`train_sfl_pi.py:17-100`; PR #5, head `f01114a`). | ALREADY-MERGED-DELETE-SAFE |
| `kpml-investigation` (`7726eb3`) | 0 / 38 | Yes | — | Human; GitHub Actions | Revises the interactive realisation path (`interact.py`); history is contained in main. | ALREADY-MERGED-DELETE-SAFE |
| `kpml-sandbox` (`83bd0b3`) | 22 / 38 | No | `experiments/kpml-sandbox/{00-sandbox-scope.md,01-kpml-input-contract.md,02-kpml-adapter-probe.md,02-kpml-adapter-probe.py,examples/minimal-request.json,runtime/README.md,runtime/bootstrap/{build_remote_runtime.sh,resolve_kpml_source.py},runtime/deployment-manifest.yaml,runtime/hf-space/{Dockerfile,README.md,app.py,requirements.txt},runtime/results/.gitkeep,runtime/source-lock.yaml}` | Human; GitHub Actions | Adds KPML adapter probe/runtime and 9D README corrections (`experiments/kpml-sandbox/`, `README-*.md`); 22 commits are not in main. | UNIQUE-WORK-NEEDS-OWNER-DECISION |
| `main` (`e6f4b6a`) | 0 / 0 | Yes | — | Human; GitHub Actions; Copilot SWE Agent | Current 9D snapshot. | KEEP |
| `nemotron3-proposal-reader` (`75b0601`) | 0 / 28 | Yes | — | Human; GitHub Actions | Adds static implementation reader (`index.html`; PR #6, head `75b0601`). Main still links to this branch (lines 103-132). | KEEP |

*The #7 branch commit is not contained by ancestry; its patch is present in main as `378ad6f5b6afcdd605f2e65205c54b96785fbc10`. Branch tips and commit subjects are from the named refs; PR states were checked through GitHub: PRs [#1](https://github.com/simon-drury/sfl-meaning-matrix-llm/pull/1), [#2](https://github.com/simon-drury/sfl-meaning-matrix-llm/pull/2), [#3](https://github.com/simon-drury/sfl-meaning-matrix-llm/pull/3), [#4](https://github.com/simon-drury/sfl-meaning-matrix-llm/pull/4), [#5](https://github.com/simon-drury/sfl-meaning-matrix-llm/pull/5), [#6](https://github.com/simon-drury/sfl-meaning-matrix-llm/pull/6), and [#7](https://github.com/simon-drury/sfl-meaning-matrix-llm/pull/7) are all closed **merged**. PR #6's head is `nemotron3-proposal-reader`; `feature/implementation-evidence-reader` is a separate, contained ref.

## 2. Main files

Each requested root/target-directory path is listed once. “Calls” means an import, workflow invocation, or explicit document/data reference found in the repository; “—” means none found. Status wording is qualified where an item is stale or currently broken.

| File (main @ `e6f4b6a`) | Purpose | Calls / references | Verdict |
|---|---|---|---|
| `.github/workflows/infer.yml:1-52` | Manual inference workflow; invokes `interact.py`. | Actions invokes `interact.py:52`. | KEEP (import path is broken; see `interact.py`) |
| `.github/workflows/train-sfl-pi.yml:1-120` | Manual SFL-pi training; checks schema, runs trainer, uploads `artifacts/sfl_pi`. | Runs `train_sfl_pi.py:107-119`; default ref is `feature/olmo-core-sfl-random-init:9`. | KEEP (retarget default before deleting that branch) |
| `.github/workflows/train.yml:1-46` | Manual legacy-model training and checkpoint commit; default 25 epochs. | Runs `traincore.py:32-45`. | KEEP |
| `.nojekyll` (empty marker) | Disables Jekyll processing for static Pages. | GitHub Pages. | KEEP |
| `ABSTRACT.md:1-12` | Project abstract. | Human/docs. | KEEP |
| `CITATION.cff:1-35` | Citation metadata. | Citation tooling. | KEEP |
| `LICENSE:1-21` | Repository license. | Repository users. | KEEP |
| `MANIFOLD.md:1-189` | Manifold model/design description. | Human/docs; linked from `index.html:127`. | KEEP (historical claims need checking against implementation) |
| `README.md:73-80` | Main project README and implementation inventory. | Human/docs. | KEEP (stale claims: 10-epoch workflow; 32,580 vocabulary items vs 2,327 entries; “500 trajectories”) |
| `README-adapter.md:1-77` | English adapter guide. | Human/docs. | KEEP |
| `README-api.md:1-138` | English API guide. | Human/docs. | KEEP |
| `README-api-ES.md:1-114` | Spanish API guide. | Human/docs. | KEEP |
| `README-api-FR.md:1-19` | French API translation. | Human/docs. | UNREFERENCED (incomplete stub vs 138-line English guide) |
| `README-gpt4all.md:1-98` | GPT4All adapter guide. | Human/docs. | KEEP (experimental path) |
| `README-manifold-ES.md:1-102` | Spanish manifold guide. | Human/docs. | KEEP |
| `README-realize.md:1-97` | English realisation guide. | Human/docs. | KEEP |
| `README-realize-ES.md:1-98` | Spanish realisation guide. | Human/docs. | KEEP |
| `README-visualise.md:1-74` | English visualisation guide. | Human/docs. | KEEP |
| `README-visualise-ES.md:1-76` | Spanish visualisation guide. | Human/docs. | KEEP |
| `README-visualise-FR.md:1-22` | French visualisation guide. | Human/docs. | UNREFERENCED (incomplete translation) |
| `RESEARCH-LOG.md:1-120` | Dated research decisions and jotter. | Human/docs. | KEEP |
| `api.py:32-34` | FastAPI wrapper. | Imports from `sfl_matrix_engine.py` and `sfl_manifold.py`. | KEEP (imports `MeaningTrajectory`, `encode_en`, `encode_es`, absent from current engine) |
| `app.py:19-30` | Gradio application. | Imports engine/manifold/realisation/visualisation modules. | KEEP (imports absent `encode_en`/`encode_es`) |
| `interact.py:17-20` | CLI interaction and model training/inference. | `.github/workflows/infer.yml:52`; `sfl_matrix_engine.py` imports. | KEEP (imports absent `MeaningTrajectory`, `encode_en`, `encode_es`) |
| `build_uam_dataset.py:19-56` | Builds UAM clause matrices and lexical-boundary index. | Calls `uam_corpus_ingest.py`; requires external UAM root. | UNREFERENCED (no trainer reads its `.npz` or index output) |
| `uam_corpus_ingest.py:5-24` | Reads UAM annotation XML and projects features. | Called by `build_uam_dataset.py:6,10,23`; ingestion function returns empty data. | UNREFERENCED |
| `download_and_ingest_treebank.py:25,78-187` | Parses UD EWT into heuristic matrices and vocabulary centroids. | Produces `data/empirical_trajectories.jsonl` and `data/empirical_vocabulary_9d.json`; no workflow runs it. | KEEP (regenerates committed UD-derived data; separate seed generator also exists) |
| `ingest_corpus.py:24-161` | Builds a 12-sentence heuristic seed corpus. | Can overwrite the same two `data/` outputs as downloader; no caller/workflow found. | UNREFERENCED (overwrites trainer input if run) |
| `traincore.py:63-128,181-196` | Legacy transformer trainer; reads empirical plus default gold JSONL and saves checkpoint. | `.github/workflows/train.yml:34`; dataset defaults include gold at line 64. | KEEP (produces committed `sfl_model_3x3.pt`) |
| `train_sfl_pi.py:17-100,189-267` | Causal SFL-pi trainer and run-inspection artifacts. | `.github/workflows/train-sfl-pi.yml:109-119`; reads empirical JSONL. | KEEP (separate experimental trainer) |
| `sfl_pi_model.py:1-76` | SFL-pi neural model. | Imported by `train_sfl_pi.py:12`. | KEEP |
| `sfl_matrix_engine.py:1-128` | Imported 3×3 matrix type and prompt encoder. | `sfl_manifold.py:9`, `interact.py:17`, `app.py:23`, `api.py:32`, `sfl_animate.py:22`, `sfl_visualise.py:35`, `sfl_gpt4all.py:59`. | KEEP (canonical imported engine; lacks several names requested by importers) |
| `sfl_matrix_engine_v3.py:1-136` | Second 3×3 matrix/manifold implementation. | No Python importer found; HTML links in `preprocessing.html:92` and `index.html:103`. | DUPLICATE-OF-`sfl_matrix_engine.py` (unreferenced runtime code; contains extra unused manifold metrics) |
| `sfl_manifold.py:1-69` | Manifold analysis over meaning matrices. | Imported by `interact.py:18`, `app.py:24`, `api.py:33`. | KEEP |
| `sfl_adapter.py:1-33` | Meaning-to-embedding projection layer. | Imported by `interact.py:20`; documented in `README-adapter.md`. | KEEP |
| `sfl_attention.py:1-41` | Attention operations for meaning states. | Imported by `app.py:25`; HTML link `index.html:104`. | KEEP |
| `sfl_realize.py:1-39` | Maps meaning state to lexical output. | Imported by `interact.py:19`, `app.py:26`, `api.py:34`. | KEEP |
| `sfl_visualise.py:1-201` | Static trajectory visualisation. | Imported by `app.py:30`; linked by `meaning-state.html:88`. | KEEP (imports absent encoder names) |
| `sfl_animate.py:18-22,187` | Animation prototype and embedded encoder. | Linked by `meaning-state.html:87`; no workflow call. | UNREFERENCED (imports absent encoder names) |
| `sfl_gpt4all.py:56-60` | GPT4All bridge. | No Python caller found; imports absent encoder names. | UNREFERENCED |
| `data/empirical_trajectories.jsonl` (blob `40a93f53`; 500 lines) | UD sentence texts and 9D heuristic state/matrix pairs. | `traincore.py:64-108`; `train_sfl_pi.py:191`; both training workflows. | KEEP |
| `data/empirical_vocabulary_9d.json` (blob `cb8dcf67`) | Word-frequency/centroid map from the same first 500 sentences; 2,327 entries, not 32,580. | Generated by `download_and_ingest_treebank.py:171-183`; no trainer reads it. | KEEP (realisation data; no trainer consumer) |
| `data/en_ewt-ud-train.conllu` (blob `90f7d75e`) | Cached UD English-EWT source corpus. | `download_and_ingest_treebank.py:27,30-37`. | KEEP |
| `data/meaning_matrix_gold_v0.1.jsonl` (blob `4fd098fd`) | Seven 9D gold examples; creator/source rationale UNKNOWN, no generation script found. | `traincore.py:64-69`; not read by `train_sfl_pi.py`. | KEEP |
| `data/meaning_matrix_schema_v0.1.json` | Schema for gold examples. | No loader/schema-validation call found. | UNREFERENCED |
| `docs/RESEARCH_POSITION.md:1-47` | Research position/evidence framing. | Human/docs. | KEEP |
| `notes/non_ceremonial_experimentation.md:1-26` | Experimental decision directive. | Human/docs. | KEEP |
| `notes/understanding_log.md:1-33` | Learning/understanding notes. | Human/docs. | KEEP |
| `notes/REPO_AUDIT.md` | This requested branch/file/data/training audit. | No callers. | KEEP |
| `simulation/sfl_control_plane_simulation.md:1-101` | Illustrative control-plane simulation. | Human/docs. | KEEP (simulation narrative, not executable code) |
| `index.html:1-145` | Implementation-repository research/architecture reader. | Links local HTML figures and component code; links are branch-qualified `nemotron3-proposal-reader` at lines 103-132. | KEEP (retarget links before deleting that branch) |
| `preprocessing.html:42,91-93` | Preprocessing figure page. | `figures.html:29`; links both engines and `ingest_corpus.py`. | KEEP (links unreferenced/duplicate scripts) |
| `meaning-state.html:37,86-88` | M0→M1 figure page. | `figures.html:33`; links engine, animation, visualiser. | KEEP |
| `trajectory.html:33,51-53` | M0→M3 trajectory figure page. | `figures.html:37`; links engine/manifold/animation. | KEEP |
| `computation.html:36,53,59-60` | Computation figure page. | `figures.html:45`; falsely says PR #5 branch is not merged. | KEEP (stale PR status) |
| `realisation.html:36,71-73` | Boundary-realisation figure page. | `figures.html:41`; links engine/realiser/interact. | KEEP |
| `figures.html:23,29-45` | Index for five figure pages. | Links preprocessing, meaning-state, trajectory, realisation, computation. | KEEP |
| `colab_SFL_llm.ipynb` (67 cells) | Colab notebook for setup and demonstrations. | Google Colab/manual execution; no workflow caller. | UNREFERENCED (runnability unverified) |
| `wadapt_lora_training_sketch.ipynb` (19 cells) | Adapter/LoRA training sketch. | Imports `sfl_matrix_engine` in notebook; no workflow caller. | UNREFERENCED (sketch; runnability unverified) |
| `requirements.txt:1-5` | Python dependency list. | Installed by `.github/workflows/train-sfl-pi.yml:43-46`; legacy workflow installs torch/numpy directly. | KEEP |
| `test_pipeline.py:1-70` | Manual pipeline tests for matrix parsing and dimensions. | Imports `sfl_matrix_engine`; no workflow invokes it. | KEEP (manual test file) |
| `sfl_model_3x3.pt` (blob `3b675d23`) | Committed legacy trainer checkpoint. | Written by `traincore.py:176`; commit workflow `.github/workflows/train.yml:36-45`. | KEEP |
| `done.txt` (1 byte) | Empty/probe content. | No reference found. | SCRATCH |
| `ok.txt` (2 bytes) | Probe content. | No reference found. | SCRATCH |
| `t.txt` (1 byte) | Probe content. | No reference found. | SCRATCH |
| `test.py` (1 byte) | Empty/probe content; not a runnable test. | No reference found. | SCRATCH |
| `test.txt` (1 byte) | Probe content. | No reference found. | SCRATCH |
| `test2.txt` (5 bytes) | Probe content. | No reference found. | SCRATCH |
| `test3.txt` (5 bytes) | Probe content. | No reference found. | SCRATCH |
| `test4.txt` (5 bytes) | Probe content. | No reference found. | SCRATCH |
| `test5.txt` (5 bytes) | Probe content. | No reference found. | SCRATCH |
| `final_test.txt` (4 bytes) | Probe content. | No reference found. | SCRATCH |
| `test_final.txt` (4 bytes) | Probe content. | No reference found. | SCRATCH |
| `test_xyz.txt` (3 bytes) | Probe content. | No reference found. | SCRATCH |

**Ingester/output resolution.** `download_and_ingest_treebank.py` writes `data/empirical_trajectories.jsonl` and `data/empirical_vocabulary_9d.json` (`:165-183`); both trainers read the former, neither reads the latter. `ingest_corpus.py` writes those same paths (`:125-143`) from its 12 literal seed sentences and can overwrite committed trainer input; no caller was found. `uam_corpus_ingest.py:23-24` currently returns empty arrays. `build_uam_dataset.py:47-51` would write `uam_meaning_trajectories.npz` and `uam_lexical_boundary_index.json` under its output directory (default `data/`); neither trainer reads either file.

**Readers in the other repository.** The local `index.html` and six linked local figure pages describe the implementation and prototype evidence; they link into this repository (`figures.html:23-45`). `simon-drury/sfl-native-language-modelling/index.html` at `da7bb5c0b6996361cdb64da735299f1514577945` is a distinct proposal reader (research questions, SFL framework, design, evaluation, references); its README describes it as the public doctoral proposal (`README.md`, blob `92a1865e`). It is not a duplicate of the local implementation/figure pages.

## 3. Data provenance

| File | Provenance of values | Script / line | Commit, author, object |
|---|---|---|---|
| `data/empirical_trajectories.jsonl` | 500 rows, step indices 0–499 and text from the first 500 parsed UD EWT train sentences. Each matrix/vector coordinate is emitted from hard-coded conditions in `map_sentence_to_matrix`; there is no annotation source or derivation for those constants documented. | `download_and_ingest_treebank.py:25` (unpinned URL), `:40-70` (sentence parsing), `:78-137` (all mapping literals/conditions), `:139-169` (step, text, vector and matrix writes). | Script added by `5957cfd79a8d0da8b0f19ed82254252e75050a72` (Simon); data first committed by `ab83686eebf1536f7f515f4a296bc37ad00a8623` (GitHub Action); current blob `40a93f530db9b1d6a17b551c052887e36e786da6`. |
| `data/meaning_matrix_gold_v0.1.jsonl` | Seven examples with explicit vectors/matrices and systemic-feature labels; no repository generation script or external derivation is documented. | Data rows; schema `data/meaning_matrix_schema_v0.1.json:1-131`. | `0092e1f5bb086a44de98f2552ec3c264d64698ae` (Simon); current blob `4fd098fdde69f01feaa955f2e1cf658ba9508a5d`. |
| `data/en_ewt-ud-train.conllu` | Cached UD EWT corpus. The URL uses `/master/` and is unpinned; the downloader uses the cached file when present. Original upstream commit/version is UNKNOWN. | `download_and_ingest_treebank.py:25,30-37`. | Current Git blob SHA `90f7d75edc3147331665c38f668401a96b49e7c8` (`git ls-tree`); commit `ab83686` added it, author GitHub Action. |

**Empirical-vs-gold comparison.** The empirical JSONL has 76 distinct vectors; none of its 500 vectors equals any of the seven gold vectors. The mapper does not read the gold file, and the gold file predates the mapper (`0092e1f`, 2026-09-20; `5957cfd`, 2026-09-21): the constants do not appear to be derived from gold v0.1. Exact numeric origins beyond the script's heuristic literals are UNKNOWN.


## 4. Training reality

| Fact | Result | Evidence |
|---|---|---|
| SFL-pi JSONL grouping | Consecutive valid `vector_9d` rows form one trajectory; `step` is ignored. Blank/invalid rows delimit it. The 500 committed lines form one 500-state trajectory, then default `max_seq_len=64` truncates it to one 64-state sequence (63 next-state targets). | `train_sfl_pi.py:24-31,34-89,191-201`; source JSONL has 500 lines. |
| SFL-pi optimizer steps | One dataset trajectory, batch size 16 → one DataLoader batch and **1 optimizer step/epoch**; default 25 epochs → 25 steps. | `train_sfl_pi.py:193-200,208-209,231-250`. |
| SFL-pi claimed epochs | Trainer default 25; SFL-pi workflow dispatch default 25 and passes it to `train_sfl_pi.py`. | `train_sfl_pi.py:193`; `.github/workflows/train-sfl-pi.yml:11-15,107-113`. |
| README / legacy workflow claims | README says `train.yml` runs 10-epoch training (`README.md:80`); the workflow input defaults to 25 and calls `traincore.py`, not `train_sfl_pi.py`. | `.github/workflows/train.yml:6-10,32-45`. |
| Committed model producer | `sfl_model_3x3.pt` was last updated by `85a44aa32a31e86c5c94661a6988d45e0bcfc2e2` (“Auto-update … (25 epochs),” `github-actions[bot]`); the committing workflow invokes `traincore.py`. SFL-pi instead writes `artifacts/sfl_pi/sfl_pi_random_init.pt` and uploads artifacts. | `.github/workflows/train.yml:32-45`; `traincore.py:128-176`; `train_sfl_pi.py:267`; `.github/workflows/train-sfl-pi.yml:115-120`; main model blob `3b675d239461e1bf39e59ef40de49aeffdbbbaa6`. |
| Difference between trainers | `traincore.py` also loads default `meaning_matrix_gold_v0.1.jsonl` (`:64-108`); `train_sfl_pi.py` reads only empirical trajectories. With current files, traincore forms one 500-state block + one 7-state block = 505 adjacent transitions and, at batch 32, 16 optimizer batches/epoch. | `traincore.py:64-108,128-169`; `.github/workflows/train.yml:34`. |

## 5. Proposed pruning/consolidation — NOT EXECUTED

1. Retarget branch-qualified references before pruning the referenced refs:
   ```sh
   git switch main
   git pull --ff-only origin main
   sed -i 's@feature/olmo-core-sfl-random-init@main@g' .github/workflows/train-sfl-pi.yml
   sed -i 's@nemotron3-proposal-reader@main@g' index.html
   sed -i 's@fix/sfl-pi-jsonl-ingestion@main@g' computation.html
   git diff --check
   git diff -- .github/workflows/train-sfl-pi.yml index.html computation.html
   git add .github/workflows/train-sfl-pi.yml index.html computation.html
   git commit -m "docs: retarget merged branch references"
   ```
2. After review/commit of that reference cleanup, delete only fully merged branches with no remaining live reference:
   ```sh
   git push origin --delete chore/add-sfl-pi-actions-launcher ci/resume-sfl-pi-training copilot/research-train-sfl-pi-workflow-issues docs/non-ceremonial-experimentation-directive feature/add-meaning-state-animation-reader feature/implementation-evidence-reader feature/olmo-core-sfl-random-init feature/sfl-pi-full-run-inspection fix/install-pytorch-for-sfl-pi fix/sfl-pi-jsonl-ingestion kpml-investigation nemotron3-proposal-reader
   git fetch --prune origin
   ```
3. Do not delete `kpml-sandbox` or its 22 non-main commits before the owner decides whether to retain/merge its KPML probe/runtime and 9D documentation revisions. Keep `main`; do not delete it.

## 6. Owner-only questions

- Should the KPML probe/runtime and 9D README corrections on `kpml-sandbox` be merged, archived, or discarded?
- Is `sfl_matrix_engine_v3.py` needed despite being a second unimported engine and having only HTML links?
- Should the local implementation/figure reader remain alongside the separate public proposal reader?
- Before any affected branch deletion, should the workflow and reader links be retargeted to `main` as proposed?
