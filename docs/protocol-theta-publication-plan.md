# Publication plan: GödelOS recursive feedback and Protocol Theta

## Recommended publication route

Publish this as a reproducibility-first technical artefact, not as a priority brief:

1. merge a clean, reviewed repository snapshot containing the provenance report, technical note, three-condition harness, tests, and a curated historical-data manifest;
2. create a signed, immutable Git tag and GitHub release;
3. archive that exact tag on Zenodo and publish a version DOI under a concept DOI;
4. upload the technical note as a preprint, preferably to arXiv if its category and endorsement requirements are met, citing the Zenodo bundle and exact Git tag; and
5. retain the repository as the living implementation while treating the DOI snapshot as the cited scientific record.

This order makes code, data, provenance, and claims inspectable together. The release should emphasize independent convergence and the larger recursive-cognition programme. It should not imply that publication date establishes invention of a recurrence already present in earlier LLM telephone-game work.

## 1. Repository cleanup

Create a release branch and limit it to publication-relevant changes. Preserve historical files in Git history; do not rewrite, normalize, or silently “fix” them. Instead, add a curated index that states which artefacts are original, migrated, synthetic, retrospectively analysed, or newly reconstructed.

Recommended release tree:

```text
docs/
  protocol-theta-provenance-report.md
  protocol-theta-recursive-feedback-note.md
  protocol-theta-publication-plan.md
  self-feeding-authors-note.md
experiments/recursive-feedback/
  README.md
  recursive_feedback.py
  run.py
  test_recursive_feedback.py
reproducibility/
  historical-artifact-manifest.tsv
  checksums.sha256
  environment/
  analysis/
CITATION.cff
LICENSE
```

Before release:

- remove credentials, request headers, personal paths, transient caches, and provider tokens from tracked and historical release files;
- identify every generated data file and mark `synthetic:true` records in the curated manifest;
- exclude `publication_summary.json` values from scientific results because their generator hard-codes demonstration statistics;
- retain raw JSONL unmodified and put any repaired/normalized data in a new derived directory with a transformation log;
- add a data dictionary for every retained field, including null fields;
- record that historical `input_prompt` and RNG seeds are missing;
- add a script that reproduces every table from raw or curated inputs;
- pin Python and all analysis dependencies with hashes;
- make all tests and analyses runnable without model credentials by default; and
- ensure the external-model path fails clearly when credentials or immutable model identifiers are absent.

Do not put the old MVP tree back at HEAD merely to make it look current. Use Git object links and a manifest that extracts exact historical blobs by commit hash.

## 2. Historical artefact manifest

Add `reproducibility/historical-artifact-manifest.tsv` with one row per cited source or data object and these fields:

| Field | Purpose |
|---|---|
| `artifact_id` | Stable local identifier |
| `path_at_commit` | Exact repository-relative historical path |
| `blob_sha` | Content-addressed Git blob ID |
| `commit_sha` | Commit that first introduces the cited version |
| `author_time` / `commit_time` | ISO 8601 Git timestamps |
| `internal_time_min` / `internal_time_max` | Self-recorded run timestamps, kept distinct from Git time |
| `head_status` | Present, renamed, deleted, or superseded |
| `artifact_class` | Concept, source, runnable source, raw execution, derived analysis, or simulation |
| `generation_status` | Historical, migrated, synthetic, retrospective, or reconstruction |
| `model_id` | As recorded, without guessing a revision |
| `claim_supported` | Bounded claim supported by this artefact |
| `known_limitations` | Missing inputs, incompatible source, null metrics, etc. |
| `sha256` | Exported-file checksum for the release bundle |

Generate, rather than hand-edit, the checksums and timestamp fields. Keep the generation script in the bundle. The manifest should state that Git timestamps do not independently establish first public availability.

## 3. Licensing and data-rights gate

No repository-root `LICENSE` file was found during this review. Resolve this before any archival release; absence of a licence leaves reuse rights unclear.

Complete a written rights check covering:

- authority of repository contributors to license their code and documentation;
- a code licence, preferably a standard OSI licence compatible with existing dependencies;
- an explicit documentation/data licence, which may differ from the code licence;
- model-provider terms governing redistribution of generated outputs from Grok/OpenRouter and DeepSeek endpoints at the time of generation;
- attribution obligations for third-party code, prompts, model names, plots, or copied documentation;
- whether any logs contain personal data, API identifiers, private prompts, or secrets;
- whether generated outputs require notices or model cards; and
- whether the chosen Zenodo/arXiv licences match the repository licences.

Do not infer permission from the repository being public. If contributor or output rights cannot be cleared, archive hashes and provenance descriptions while withholding the affected payload, and state the access restriction.

## 4. Reproducibility bundle

The DOI deposit should contain:

1. the exact source archive for the signed Git tag;
2. PDF and Markdown versions of the technical note and provenance report;
3. unmodified historical raw data that passes the rights/privacy review;
4. the artefact manifest and SHA-256 checksums;
5. extraction scripts for historical Git blobs;
6. a version-pinned environment file or container recipe;
7. the three-condition reproduction harness and tests;
8. a deterministic mock run as a schema fixture;
9. analysis scripts that recreate every reported retrospective statistic;
10. a machine-readable results table with historical and modern namespaces kept separate;
11. a README giving one-command offline verification and credential-free test instructions; and
12. a `KNOWN_LIMITATIONS.md` restating the missing runner, missing inputs, control defects, null embeddings, and metric divergences.

For any new live-model run, record exact request messages, raw bytes, provider request ID where permitted, model revision, tokenizer, finish reason, supported seed, retry count, timestamp, and errors. Store environment-variable names but never credentials. If an endpoint is mutable, archive a model card and provider response metadata and avoid calling the run bitwise reproducible.

## 5. Citation metadata

Add `CITATION.cff` and validate it with GitHub's CFF tooling. At minimum include:

- title: *Recursive Output Feedback in GödelOS: Historical Provenance and Reproducible Protocols*;
- full author names in the agreed order;
- ORCID identifiers where available;
- release version and date;
- repository URL and exact release URL;
- Zenodo concept DOI and version DOI after reservation;
- preprint DOI/arXiv identifier after acceptance;
- preferred citation type (`software` for the repository, `article` for the note);
- licence identifiers; and
- keywords such as recursive feedback, output-to-input loop, recursive cognition, self-model, machine phenomenology, and Protocol Theta.

Optionally add `codemeta.json`, a `README` citation section, and BibTeX copied from the final DOI metadata. Keep software and article citations distinct so readers can cite the implementation, the frozen data bundle, or the argument precisely.

## 6. Tagged GitHub release

Suggested tag: `protocol-theta-recursive-feedback-v1.0.0`. Use a signed annotated tag on the reviewed release commit. The release notes should contain:

- a one-paragraph result and scope statement;
- exact commit and tag hashes;
- links to the technical note, provenance report, and experiment README;
- historical versus reconstructed artefact labels;
- test command and verified environment;
- data and code licence statements;
- checksums and Zenodo DOI;
- the critical non-claims; and
- a concise list of unresolved provenance questions.

Do not call the tag “original 2025 release.” It is a 2026 archival/reconstruction release containing historical Git objects and should say so.

## 7. Zenodo archival snapshot

Connect Zenodo to the GitHub repository before cutting the tag, or upload the source archive manually if organizational policy requires it. Reserve the DOI early so it can appear in the note and `CITATION.cff`, but publish the deposit only after verifying that its archive hash matches the signed tag.

Use Zenodo's versioning:

- the **concept DOI** identifies the evolving GödelOS recursive-feedback record;
- the **version DOI** identifies the exact first provenance/reproduction bundle.

In the description, state that internal 2025 timestamps are repository evidence and are not the DOI publication date. Include related identifiers for the GitHub release and preprint. Upload checksums separately and verify a fresh download before publishing the record.

## 8. Preprint route

Prepare the technical note in a conservative computer-science/AI methodology category. If arXiv endorsement or category fit blocks timely release, first publish the Zenodo technical report with a DOI, then submit to arXiv or an institutional repository without changing the historical claims.

The abstract should lead with the verified mechanism and the different research motivation. It should not lead with a consciousness claim or a dispute. Suggested positioning:

> We reconstruct a September 2025 GödelOS implementation in which complete model outputs were reinjected into fresh requests as external cognitive state, alongside an earlier transformed-state variant. We compare it with stateless self-feeding for black-box backdoor detection, identify the latter as a formal restriction of the generalized architecture, audit the historical measurements, and provide reproducible controlled protocols.

The related-work section must cite the 2024 LLM telephone-game and cultural-evolution studies and the 2025 broken-telephone study. This prevents an overbroad novelty claim. Upload the provenance report as supplementary material rather than compressing its qualifications out of the main note.

## 9. Review gates

Require sign-off from at least one reviewer not involved in the original experiments on each gate:

| Gate | Passing criterion |
|---|---|
| Provenance | Every historical claim resolves to a path, blob, commit and timestamp; internal and Git dates are distinct |
| Protocol | A, B and C request messages match their mathematical definitions in tests and a fixture |
| Data | Synthetic/migrated/real lines are machine-labelled; counts reproduce from raw files |
| Metrics | Formal \(C_n\), lowercase `c`, simulation composite and modern metrics are never conflated |
| Statistics | No hard-coded demo statistic appears as a result; grouped dependence and multiple comparisons are handled |
| Interpretation | Alternative compliance/length/prompt explanations are stated; no phenomenal-consciousness inference |
| Related work | Pre-GödelOS iterative-transmission literature is cited and novelty wording is narrow |
| Rights | Code, docs and output licences are documented; sensitive data scan passes |
| Reproduction | Clean environment runs tests and regenerates all included tables |
| Archive | Tag, GitHub tarball and Zenodo payload checksums agree |

## 10. Release checklist

### Evidence and writing

- [ ] Resolve or explicitly retain every open question in the provenance report.
- [ ] Verify all hashes and timestamps from a fresh clone with all referenced refs fetched.
- [ ] Add blob IDs and generated SHA-256 hashes to the historical manifest.
- [ ] Have an independent reviewer reproduce the earliest-source and earliest-run findings.
- [ ] Convert the note to publication PDF and inspect equations, tables, links, and pagination.
- [ ] Include all critical non-claims in the abstract-adjacent scope statement or introduction.
- [ ] Check every novelty sentence against the earlier literature.

### Code and data

- [ ] Run unit tests, static checks, formatting, and a deterministic mock fixture.
- [ ] Run the full analysis from raw data in a clean container.
- [ ] Confirm synthetic DeepSeek duplicates are excluded from inferential analyses.
- [ ] Confirm no report treats lowercase `c` as formal \(C_n\).
- [ ] Record exact dependency and platform versions.
- [ ] Scan source, history exports, logs, figures and archives for secrets and personal data.
- [ ] Test the archive on a machine without repository-local state or model credentials.

### Rights and metadata

- [ ] Add and review repository, documentation, and data licences.
- [ ] Complete the generated-output redistribution review.
- [ ] Collect author names, affiliations, ORCIDs and contribution roles.
- [ ] Validate `CITATION.cff` and optional `codemeta.json`.
- [ ] Reserve Zenodo DOI and update every citation target consistently.

### Release and archive

- [ ] Merge the reviewed release commit without history rewriting.
- [ ] Create and verify the signed annotated tag.
- [ ] Create the GitHub release from that tag.
- [ ] Compare GitHub source archive and local tag checksums.
- [ ] Publish the Zenodo version and verify a fresh download.
- [ ] Submit the preprint and add its identifier after acceptance.
- [ ] Send the collegial authors' note only after the public evidence bundle is accessible.

## Success criterion

The release succeeds if a reader can independently answer four questions from immutable evidence: what GödelOS actually implemented, when the relevant Git objects and recorded executions date from, how the historical protocol differs from stateless self-feeding, and which measurements/results are formal proposals, implemented proxies, raw observations, simulations, or modern reanalyses. Discoverability and reproducibility—not escalation of a priority dispute—are the publication goals.

