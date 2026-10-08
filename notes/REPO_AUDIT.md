# REPO AUDIT — simon-drury/sfl-meaning-matrix-llm

Audited at `main` = `e6f4b6a` (2026-10-07, simon). Full history fetched (not shallow). Nothing was edited, moved, deleted or pushed other than adding this file. Items not provable from git/GitHub metadata are marked UNKNOWN.

## (i) Summary

`main` has 150 commits; 14 of 17 remote branches have no commits that `main` lacks, so they are safe to delete. Seven PRs (#1–#7) are merged. PRs #8 and #9 are the open audit PRs. Two branches hold unmerged work needing owner decision: `purge/6d` (1 commit, RESEARCH-LOG.md only) and `kpml-sandbox` (22 commits, branched 2026-09-22). `data/empirical_trajectories.jsonl` is reproducible byte-for-byte from `download_and_ingest_treebank.py` plus the committed UD EWT train file, and uses 500 hardcoded-heuristic 3x3 mappings, not values derived from the gold file. `sfl_model_3x3.pt` was produced by `traincore.py` through `train.yml`, not by `train_sfl_pi.py`. `train_sfl_pi.py` on the 500-line JSONL builds **one** trajectory, truncated to 64 states. That is 1 optimizer step per epoch and 25 steps for a 25-epoch run. README claims about parameter count, vocabulary size, epochs and the workflow do not match the code.

## (ii) Branch table

Ahead/behind are `main...branch` (behind = commits on main missing from branch; ahead = commits on branch missing from main). The task listed 15 branches; the remote has 17 (adds `main` and `copilot/complete-repo-audit`).

| Branch | Behind | Ahead | Unique files vs main (3-dot) | Tip (author, date) | Purpose (1 line) | PR | Verdict |
|---|---|---|---|---|---|---|---|
| chore/add-sfl-pi-actions-launcher | 36 | 0 | none | 8879719 (simon, 2026-09-25) | adds train-sfl-pi.yml launcher | #1 merged | ALREADY-MERGED-DELETE-SAFE |
| ci/resume-sfl-pi-training | 31 | 0 | none | aee2ba3 (simon, 2026-09-25) | CI schema-inspection steps for SFL-pi | none | ALREADY-MERGED-DELETE-SAFE (tip is ancestor of main) |
| copilot/complete-repo-audit | 0 | 1 | none (empty "Initial plan" `c8b8d09`, then this file) | c8b8d09 (copilot-swe-agent[bot], 2026-10-08) | this audit, PR #9 | #9 open | KEEP until #9 merged |
| copilot/repo-audit | 0 | 1 | none (empty "Initial plan" `983a992`) | 983a992 (copilot-swe-agent[bot], 2026-10-08) | interrupted earlier audit attempt | #8 open (WIP, 0 files) | ALREADY-MERGED-DELETE-SAFE after closing #8 (no content; duplicate of #9) |
| copilot/research-train-sfl-pi-workflow-issues | 0 | 0 | none | e6f4b6a (simon, 2026-10-07) | tip == main tip | none | ALREADY-MERGED-DELETE-SAFE |
| docs/non-ceremonial-experimentation-directive | 30 | 0 | none | 709efc9 (simon, 2026-09-26) | notes/non_ceremonial_experimentation.md | #4 merged | ALREADY-MERGED-DELETE-SAFE |
| feature/add-meaning-state-animation-reader | 27 | 1 | `meaning-state.html` (A) | 8d492bc (simon, 2026-09-29) | M0→M1 figure page | #7 merged (squash `378ad6f`) | ALREADY-MERGED-DELETE-SAFE (`git diff 378ad6f 8d492bc -- meaning-state.html` empty; ahead=1 is a squash artifact) |
| feature/implementation-evidence-reader | 27 | 0 | none | 3f0d2cf (simon, 2026-09-28) | tip is merge commit of PR #6 | none of its own | ALREADY-MERGED-DELETE-SAFE |
| feature/olmo-core-sfl-random-init | 7 | 0 | none | e80de20 (copilot-swe-agent[bot], 2026-10-06) | SFL-pi (`sfl_pi_model.py`, `train_sfl_pi.py`) | #3 merged (`9a6722d`) | ALREADY-MERGED-DELETE-SAFE |
| feature/sfl-pi-full-run-inspection | 33 | 0 | none | aebeea8 (simon, 2026-09-26) | inspection output in train_sfl_pi.py | none | ALREADY-MERGED-DELETE-SAFE |
| fix/install-pytorch-for-sfl-pi | 34 | 0 | none | f07ebde (simon, 2026-09-25) | pip install torch in workflow | #2 merged | ALREADY-MERGED-DELETE-SAFE |
| fix/sfl-pi-jsonl-ingestion | 31 | 0 | none | f01114a (Simon James Drury, 2026-09-26) | JSONL grouping fix in train_sfl_pi.py | #5 merged (`e5541d2`) | ALREADY-MERGED-DELETE-SAFE |
| kpml-investigation | 38 | 0 | none | 7726eb3 (simon, 2026-09-22) | tip is ancestor of main | none | ALREADY-MERGED-DELETE-SAFE |
| kpml-sandbox | 38 | 22 | 47 files: `experiments/kpml-sandbox/**` (15 A), 20 README/ABSTRACT/RESEARCH-LOG edits (3x3/9D rewording), 12 junk-file deletions (done/ok/t/test*/final_test, test.py) | 83bd0b3 (simon, 22 commits, 2026-09-22) | KPML adapter/HF-space sandbox + README 9D rewrite + junk cleanup | none | UNIQUE-WORK-NEEDS-OWNER-DECISION (base 7726eb3 is stale; README/junk changes overlap main) |
| main | 0 | 0 | — | e6f4b6a (simon, 2026-10-07) | default | — | KEEP |
| nemotron3-proposal-reader | 28 | 0 | none | 75b0601 (simon, 2026-09-28) | static research reader (index.html) | #6 merged (`3f0d2cf`) | ALREADY-MERGED-DELETE-SAFE |
| purge/6d | 2 | 1 | `RESEARCH-LOG.md` | 996b5c1 (simon, 2026-10-07) | "Purge 6D from decision protocol" | none | UNIQUE-WORK-NEEDS-OWNER-DECISION (see §iv) |

Authors of unique commits: kpml-sandbox 22× simon; purge/6d 1× simon; audit branches 1× copilot-swe-agent[bot] each.

### PR status

| PR | Head branch | State | Merge evidence on main |
|---|---|---|---|
| #1 | chore/add-sfl-pi-actions-launcher | merged 2026-09-25 | `30a1db7` |
| #2 | fix/install-pytorch-for-sfl-pi | merged 2026-09-25 | `b02e1c8` |
| #3 | feature/olmo-core-sfl-random-init | merged 2026-10-06 | `9a6722d` |
| #4 | docs/non-ceremonial-experimentation-directive | merged 2026-09-26 | `e3090b0` |
| #5 | fix/sfl-pi-jsonl-ingestion | merged 2026-10-06 | `e5541d2` |
| #6 | nemotron3-proposal-reader | merged 2026-09-28 | `3f0d2cf` |
| #7 | feature/add-meaning-state-animation-reader | merged 2026-09-29 (squash) | `378ad6f` |
| #8 | copilot/repo-audit | open, WIP, no file changes | — |
| #9 | copilot/complete-repo-audit | open (this PR) | — |

Source: `list_pull_requests` (`merged_at` set for #1–#7; the list endpoint reports `merged:false`, ignore) cross-checked against `git log origin/main`.

## (iii) File table

### Root and directories

| Path | Purpose | Last/first commit | Status |
|---|---|---|---|
| sfl_matrix_engine.py | `MeaningMatrix`, `SFLMatrixEngine`; imported by api.py, app.py, interact.py, sfl_animate/manifold/visualise/gpt4all.py, test_pipeline.py | cc85bb7 2026-09-20 | CANONICAL |
| sfl_matrix_engine_v3.py | `SemioticMatrix3x3`, `SemioticManifold3x3`; **no importers** (only HTML links) | 270e82e 2026-09-20 | ORPHAN near-duplicate; see below |
| traincore.py | `SFLManifoldTransformer` + trainer; run by train.yml | 3c17a11 2026-09-21 | ACTIVE (produced sfl_model_3x3.pt) |
| train_sfl_pi.py (+ sfl_pi_model.py) | `SFLPi` causal trainer; run by train-sfl-pi.yml | f01114a 2026-09-26 | ACTIVE (experimental) |
| download_and_ingest_treebank.py | UD EWT → 500 sentences → trajectories + vocab | 5957cfd 2026-09-21 | ACTIVE (data source) |
| ingest_corpus.py | rule extractor over 12 hardcoded sentences; **writes the same two output files** | 3e417ac 2026-09-21 | HAZARD: running it overwrites 500-row data with 12 rows |
| uam_corpus_ingest.py | UAM XML parser; `ingest_uam_corpus` returns empty stub | 076727d 2026-09-21 | STUB, needs external UAM corpus |
| build_uam_dataset.py | builds npz/json from UAM project via uam_corpus_ingest | 8192972 2026-09-21 | UNUSED (no UAM corpus in repo) |
| interact.py | CLI infer/train; infer.yml runs it; default model `sfl_pi_model.pt` (not in repo) | e6f4b6a | ACTIVE |
| api.py, app.py, sfl_adapter.py, sfl_animate.py, sfl_attention.py, sfl_gpt4all.py, sfl_manifold.py, sfl_realize.py, sfl_visualise.py | pipeline modules / demos | various | KEEP (sfl_gpt4all.py still has 6D wording, 6 hits) |
| test_pipeline.py | e2e check | — | KEEP |
| sfl_model_3x3.pt | traincore checkpoint, 2,181,670 B | 85a44aa | KEEP; see §v |
| colab_SFL_llm.ipynb, wadapt_lora_training_sketch.ipynb | notebooks | — | KEEP (runnability UNKNOWN) |
| index/figures/meaning-state/preprocessing/realisation/trajectory/computation.html | GitHub Pages reader (7 pages); `.nojekyll` present | 75b0601…0e4225a, 2026-09-28/29 | KEEP |
| ABSTRACT.md, MANIFOLD.md, RESEARCH-LOG.md, CITATION.cff, LICENSE, requirements.txt, .devcontainer/ | meta | — | KEEP. requirements.txt lacks torch (workflows pip-install it separately) |
| data/ | see §iv | — | KEEP |
| docs/RESEARCH_POSITION.md (47 L), notes/{non_ceremonial_experimentation,understanding_log}.md, simulation/sfl_control_plane_simulation.md (101 L) | prose notes | 5f94b09, 709efc9 | KEEP |
| experiments/README.md | describes `lassm_baseline_comparison.py` (6D/3x2) which `8b97a7d` deleted from main; README is stale; still on purge/6d branch | dbab308 | STALE |
| .github/workflows/train.yml | `python traincore.py … --epochs ${{inputs.epochs\|\|'25'}}`, commits `sfl_model_3x3.pt` to main | 2bcc3dc/88bc86e/10c4a9a | ACTIVE |
| .github/workflows/train-sfl-pi.yml | checks out `inputs.code_ref` (default `feature/olmo-core-sfl-random-init`), runs `train_sfl_pi.py`, uploads artifact `sfl-pi-<seed>` | 8879719…e80de20 | ACTIVE; default ref is a branch recommended for deletion |
| .github/workflows/infer.yml | runs `interact.py "<prompt>"` | fddd064…39e4015 | ACTIVE |

### Resolved pairs

| Question | Resolution |
|---|---|
| sfl_matrix_engine.py vs _v3.py | Both `Author: sjd`, both "3x3 continuous manifold", different class names (`MeaningMatrix`/`SFLMatrixEngine` vs `SemioticMatrix3x3`/`SemioticManifold3x3`). v3 was added in 270e82e alongside traincore.py. Nothing imports v3. Verdict: keep `sfl_matrix_engine.py`; v3 is an orphan. Reader pages (preprocessing.html:92, index.html:103) link to v3, so deletion breaks those links (index.html links the `nemotron3-proposal-reader` blob). Owner decision. |
| traincore.py vs train_sfl_pi.py | `train.yml` → traincore.py → `sfl_model_3x3.pt`. `train-sfl-pi.yml` → train_sfl_pi.py → artifact `sfl_pi_random_init.pt` (artifact only; never committed). `sfl_model_3x3.pt` contains 540,553 parameters in tensors `in_proj.*`, `pos_encoder`, `transformer.layers.N.*`, which matches `SFLManifoldTransformer` (traincore.py:17–37) exactly; it is a bare state_dict with no `model_state`/`manifest` keys that train_sfl_pi.py:267 would write. Commit chronology: traincore.py `3c17a11` 2026-09-21 19:42:32Z → checkpoint `85a44aa` 19:45:17Z by github-actions[bot]. train_sfl_pi.py did not exist until 2026-09-25. |
| ingest_corpus vs download_and_ingest_treebank vs uam_corpus_ingest vs build_uam_dataset | Only download_and_ingest_treebank.py produced committed data (byte-identical regeneration, §iv). ingest_corpus.py: 12 hardcoded sentences, same output paths (overwrite hazard). uam_*/build_uam_*: an unused pair requiring an external UAM project; `ingest_uam_corpus()` is a stub; `build_uam_dataset.py` only needs `UAMCorpusIngest`. |
| Junk files | `done.txt`("1"), `ok.txt`("ok"), `t.txt`("x"), `test.txt`("x"), `test.py`("x"), `test2-5.txt`("testN"), `test_final.txt`/`final_test.txt`("done"), `test_xyz.txt`("xyz"). All 1–5-byte CI-probe leftovers, commits `88a5521 a61df1d 1126d16 292df78 e614110` (all "test", simon, 2026-09-21). Not referenced anywhere. `kpml-sandbox` (`bea4663`, `6282537`) already deletes them. DELETE-SAFE. |
| README variants | `README.md` (4,649 B) + module READMEs: adapter, api, gpt4all, manifold, pilot, realize, visualise (7). ES translations: README, adapter, api, manifold, realize, visualise (6). FR translations: same 6. No ES/FR for `gpt4all` and `pilot`. FR module files are stubs (407–1,132 B vs 2.2–4.4 KB for ES/EN). README-ES/FR still contain 3x2/6D wording (5 and 3 hits); `kpml-sandbox` has a 9D rewrite of these. README-pilot.md (12.9 KB) is the largest after README-ES. |
| HTML reader pages | Repo has 7 pages (index.html 14,489 B …). `simon-drury/sfl-native-language-modelling` (HEAD `860fff1`) holds `index.html` (11,726 B), `PROPOSAL_READER_CONTENT_LEDGER.md`, `assets/`, `.github/`, `CITATION.cff`, `README.md`. Content equivalence of the two `index.html` files: UNKNOWN (second repo is only partially readable via API; no diff done). The repo's reader is the `nemotron3-proposal-reader` lineage (75b0601). Owner decision on canonical home. |

## (iv) Data provenance

| File | Source | Script / line | Commit / author | Notes |
|---|---|---|---|---|
| data/empirical_trajectories.jsonl (500 lines; blob `40a93f5`) | first 500 sentences of UD English-EWT `train` | `download_and_ingest_treebank.py`: `parse_conllu_sentences(max_sentences=500)` (l.40, call l.142), `build_real_dataset(num_sentences=500)` (l.139–), called at l.187 | `ab83686` "GitHub Action <action@github.com>" 2026-09-21 11:31:51Z, after script `5957cfd` (simon, 11:47:44+02:00 = 09:47Z); the committing mechanism is UNKNOWN | **Verified**: ran the committed script on the committed conllu in a /tmp copy; `cmp` identical for trajectories and for `empirical_vocabulary_9d.json` (2,327 words). Fields `step` 0–499, `text`, `vector_9d`, `matrix_3x3`. |
| mapping constants | hardcoded in `UniversalDependencySFLMapper.map_sentence_to_matrix` | `download_and_ingest_treebank.py` l.78–137 (ideational 0.60/0.40/0.80/0.20, participants/6 clipped [0.1,0.9], 0.50; interpersonal 0.35/0.60/0.40, 0.30/-0.60/-0.30, 0.20/0.10/0.15; textual 0.65/0.40/0.85, 0.40/0.20/0.40, 0.30/0.15/0.30) | 5957cfd simon | Only 76 distinct vectors across 500 rows; most frequent vector appears 52×. Row-level text is UD only; the 3x3 values are from no annotation in UD. |
| constants derive from gold file? | **No.** | `grep gold` in all .py/.yml: only traincore.py:64–69 *reads* the gold file; the mapper never does | — | Gold file's range includes -0.75…0.90; mapper has only 2 negative constants. No code path links them. Any similarity is coincidental or hand-copied: UNKNOWN. |
| data/en_ewt-ud-train.conllu | raw UD EWT train | `UD_EWT_URL = https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/master/en_ewt-ud-train.conllu` (l.25), **unpinned `/master/`**; downloaded only if absent | `ab83686` | Git blob SHA `90f7d75edc3147331665c38f668401a96b49e7c8`; 15,034,493 B; 247,863 lines; 12,544 `sent_id`. UD release/commit it came from: UNKNOWN. Since the file is committed, CI never re-downloads it. |
| data/empirical_vocabulary_9d.json | same script | l.171–183 | `ab83686` | 32,579 lines = 2,327 entries (frequency, centroid_9d). |
| data/meaning_matrix_gold_v0.1.jsonl (7 rows, 3 pair groups; blob `4fd098f`) | hand-authored EN minimal pairs with `systemic_features` | no generating script in repo: UNKNOWN | `0092e1f` simon 2026-09-20, with `meaning_matrix_schema_v0.1.json` | Predates ingestion script. Consumed by `traincore.py:64` default `gold_path` (appended to training) and by `interact.py` glob `data/*.jsonl`. |
| data/seed_turn_transitions.csv (20 rows; blob `9912ad1`) | manually constructed heuristic seeds (`experiments/README.md:21`) | consumer `experiments/lassm_baseline_comparison.py` (deleted from main by `8b97a7d`) | `dbab308` simon 2026-09-18 | **6D** columns (3 src × 2, `src_ideational…src_mode`), inconsistent with the 9D engine; now unconsumed on main. |
| Purge 6D `996b5c1` (purge/6d) | — | `RESEARCH-LOG.md` only (+15/−4) | simon 2026-10-07 12:08+02:00 | Adds "2026-10-07 / 6D purged" section; changes "Assign 6-dim meaning state" → "9-dim" (l.88 on main still says 6-dim); also unrelated wording swaps: "token sequences"→"lexical sequences", "first token"→"first semiotic unit", and a one-space indent change. Not on main. Main instead removed 6D code via `8b97a7d` (experiment) and `e6f4b6a` (`interact.py parse_vector_any`). |

## (v) Training reality

### train_sfl_pi.py on `data/empirical_trajectories.jsonl`

| Item | Value | Basis |
|---|---|---|
| Trajectory rule | contiguous `vector_9d` lines are accumulated into one trajectory; a trajectory ends only at a blank/invalid line or an explicit `states`/`trajectory` record; the `step` field is **ignored** | `TrajectoryDataset`, l.34–89, commit `f01114a` "without step reset" |
| 500 lines → trajectories | **1** (lines 1–500 contiguous, all valid 9D finite); source_lines = [1] | executed `TrajectoryDataset` with torch stubbed: `1 [(64, 9)] [1]` |
| Length | truncated to `--max-seq-len 64` → 64 states (500 if limit raised); 63 input→target pairs per step | l.27, 238–239 |
| Batch/loader | `--batch-size 16`, `DataLoader(shuffle=True)` | l.194, 209 |
| Optimizer steps/epoch | `ceil(1/16)` = **1** | l.236–250 |
| Default run | `--epochs 25` → **25 optimizer steps**, trained on 63 of the 499 available transitions (the same ones every epoch) | l.193; workflow default `"25"` |
| If one trajectory per sentence were intended | not what the code does; 500 single-state trajectories would be rejected (<2 states) | l.26 |

### traincore.py (produced `sfl_model_3x3.pt`)

| Item | Value |
|---|---|
| Data | `empirical_trajectories.jsonl` (500 states, one block) + `meaning_matrix_gold_v0.1.jsonl` (7 states, one block; unrelated pairs chained) → 499 + 6 = **505** adjacent-state transitions (reproduced with the parser logic) |
| Batch | `batch_size=32` → `ceil(505/32)` = **16 steps/epoch**; 25 epochs (workflow default) = 400 steps |
| Model | 540,553 params (arithmetic; matches checkpoint tensor bytes 2,162,212 = 4×540,553) |
| Note | model is encoder-only (`TransformerEncoder`, no causal mask) and sees `m_t` as a length-1 sequence in the training loop |

### Claims vs code

| Claim (location) | Reality |
|---|---|
| README.md:75 "2.37M-parameter `SFLMeaningTransformer` and linear adapter" | class is `SFLManifoldTransformer`; 540,553 params; no adapter in traincore.py |
| README.md:78 "32,580 lexical items" | 2,327 vocabulary entries (32,579 is the JSON line count) |
| README.md:79 "500 parsed continuous sentence trajectories" | 500 states forming 1 trajectory under train_sfl_pi.py |
| README.md:80 "train.yml … executing data ingestion, 10-epoch training, and validation" | train.yml has no ingestion, no validation; default epochs 25 |
| README.md:77 "checkpoint trained over empirical treebank trajectories" | partially: also trained on 7 gold rows |
| train-sfl-pi.yml default `code_ref` = `feature/olmo-core-sfl-random-init` | code is already on main; deleting that branch breaks default dispatch |
| train-sfl-pi.yml "Inspect empirical trajectory schema" step | diagnostic only; no effect on training |

## (vi) Proposed git commands — NOT EXECUTED

Run in a fresh clone after owner approval. Tag first, then delete.

1. `git fetch --all --prune`
2. `git tag archive/purge-6d 996b5c1 && git tag archive/kpml-sandbox 83bd0b3 && git push origin archive/purge-6d archive/kpml-sandbox` (only if owner chooses archive for these)
3. Fix default dispatch ref first (PR): change `code_ref` default in `.github/workflows/train-sfl-pi.yml` from `feature/olmo-core-sfl-random-init` to `main`.
4. Close PR #8 (no content).
5. `git push origin --delete chore/add-sfl-pi-actions-launcher ci/resume-sfl-pi-training docs/non-ceremonial-experimentation-directive feature/add-meaning-state-animation-reader feature/implementation-evidence-reader feature/olmo-core-sfl-random-init feature/sfl-pi-full-run-inspection fix/install-pytorch-for-sfl-pi fix/sfl-pi-jsonl-ingestion kpml-investigation nemotron3-proposal-reader copilot/research-train-sfl-pi-workflow-issues copilot/repo-audit`
6. After owner decides `purge/6d`: either `git cherry-pick 996b5c1` onto a new branch from main and PR it, or `git push origin --delete purge/6d` (after step 2).
7. After owner decides `kpml-sandbox`: either rebase onto main (conflicts expected on README-*.md, RESEARCH-LOG.md) or `git push origin --delete kpml-sandbox` (after step 2).
8. Junk removal PR: `git rm done.txt ok.txt t.txt test.py test.txt test2.txt test3.txt test4.txt test5.txt test_final.txt test_xyz.txt final_test.txt`
9. Optional, only if owner agrees: `git rm sfl_matrix_engine_v3.py experiments/README.md data/seed_turn_transitions.csv`; update the links in `preprocessing.html` and `index.html` first.
10. README correction PR for the claims listed in §v.

## (vii) Open questions for owner

1. `purge/6d` `996b5c1`: cherry-pick (including the incidental word swaps) or discard? Main's RESEARCH-LOG.md l.88 still says "6-dim".
2. `kpml-sandbox`: keep experiment (rebase), archive as tag, or drop? Its README/junk changes duplicate or conflict with main.
3. Is `sfl_matrix_engine_v3.py` intended to supersede `sfl_matrix_engine.py`? Reader pages link to it.
4. Should `traincore.py` keep appending the gold file to training (adjacent unrelated pairs are chained into fake transitions)?
5. Is the intended unit for `train_sfl_pi.py` one trajectory per document/paragraph rather than all 500 sentences in one? As written, only 63 transitions are trained on and 25 steps are taken.
6. Pin the UD source to a release tag/commit (current URL uses `/master/`)? Which UD version was `en_ewt-ud-train.conllu` taken from?
7. What process made commit `ab83686` ("GitHub Action") and the two checkpoint rewrites `d5eac9f` (9.5 MB → 421 KB)? UNKNOWN from repo.
8. Which repo is canonical for the HTML reader: this one or `sfl-native-language-modelling`?
9. Delete or repurpose `ingest_corpus.py` (overwrites the 500-row data) and the UAM pair (stub)?
10. Remove stale `experiments/README.md` and 6D `seed_turn_transitions.csv`?
