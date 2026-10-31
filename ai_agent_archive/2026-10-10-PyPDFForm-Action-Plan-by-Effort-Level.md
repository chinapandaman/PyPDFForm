# PyPDFForm Action Plan by Effort Level

**Date:** October 10, 2026, America/Chicago

**Basis:** [PyPDFForm Code Quality, Stability, Roadmap, and Architecture Review][review], dated October 10, 2026

**Evidence baseline:** Commit `0b5cc1dc8604b36693864852d76ed7e60f903451`, package version `6.0.0`, as evaluated in the source report

**Deliverable:** Implementation backlog, ordered by increasing effort. Completed items record subsequent implementation and validation below.

The recommended direction is to fix preservation and output safety first, then strengthen the existing architecture incrementally. A wholesale rewrite is an option to evaluate only if narrower changes prove insufficient; the source review does not recommend one.

This plan contains **42 action items in six effort groups**. Each item identifies concrete work, a completion test, and relevant dependencies or decisions. Findings R01–R13 refer to the source report; references to numbered sections cover its additional recommendations. Reported failures and test results from that review remain baseline evidence; subsequent validation is recorded under completed items.

## How to use this plan

Effort reflects implementation breadth, verification burden, compatibility risk, and uncertainty. The bands are relative planning estimates, not promised durations. A short code change can still require substantial interoperability testing. Reassess an item's band if its acceptance criteria uncover a wider problem.

| Group | Relative effort | Typical scope | Items |
| --- | --- | --- | ---: |
| 1 — Lowest-hanging fruit | Very small | A focused guard, conversion, tool fix, or documentation change | 8 |
| 2 — Bounded repairs | Small | One operation or helper, including failure handling and regression coverage | 9 |
| 3 — Coordinated correctness and delivery work | Medium | Several modules or workflows with shared invariants | 10 |
| 4 — Subsystem improvements | Large | A reusable subsystem, compatibility policy, or performance change | 7 |
| 5 — Architectural refactoring | Very large | Changes to state ownership and internal execution across the library | 4 |
| 6 — Conditional redesign or rewrite | Exploratory; potentially largest | Engine replacement or major API migration justified by measured limits | 4 |

**Effort order is not release priority.** R01–R07 are P1 findings in the source report. In particular, selected-page isolation (E3-01), safe writes (E2-01), and annotation preservation (E2-02) should lead the maintenance work even though easier items appear earlier below. Do not finish every item in one group before starting urgent work in another.

Unchecked items remain proposed. A dependency marked **requires** is a prerequisite; **coordinates with** identifies overlapping work without requiring a separate refactor first. Policy choices are recommendations for future implementation, not decisions already adopted by maintainers. Drafting them here does not change public behavior.

## Group 1 — Lowest-hanging fruit

These changes have narrow scope and can usually be reviewed independently. Their completion gates still require meaningful assertions when behavior changes.

### E1-01 — Propagate every local lint failure

- [x] **Work:** Update `scripts/linting.sh` so a failure in Pylint, Pyright, Ruff, or the documentation checker makes `make linting` fail. Choose fail-fast execution or explicit status aggregation; do not return only the last command's status.
- **Done when:** Injecting a nonzero status into each command, with all other commands succeeding, always yields a nonzero script status. An all-success run still succeeds and identifies the checks performed.
- **Basis and dependencies:** R13. Independent of PDF implementation changes; useful early because later contributors rely on this gate.
- **Completed:** October 10, 2026, [PPF-2054](https://github.com/chinapandaman/PyPDFForm/issues/2054). Explicit status aggregation runs all four checks, identifies each command, reports failures with their exit statuses, and exits nonzero if any check fails.
- **Validation:** Temporary failure-injection checks passed for each individual failure, combined failures, and all-success execution through both the script and `make linting`, covering local and container environment branches. `make test-all` passed with 100% statement coverage, and `make linting` passed using the local `./venv` with standard `zlib`.

### E1-02 — Make the documentation example checker fail on tool errors

- [x] **Work:** In `scripts/doc_examples_type_check.py`, enforce subprocess outcomes and reject malformed or missing Pyright JSON. Keep temporary-file cleanup in failure paths and distinguish diagnostics from an inability to run the checker.
- **Done when:** A missing executable, nonzero tool exit, malformed output, and reported type errors all fail the check with useful messages. Valid, clean output passes.
- **Basis and dependencies:** R13. Coordinates with E1-01; both the checker and its calling script must propagate failure.
- **Completed:** October 10, 2026, [PPF-2055](https://github.com/chinapandaman/PyPDFForm/issues/2055). Checker execution and JSON failures now exit nonzero with useful stderr messages. Pyright's type-error exit status preserves documentation source mapping, unmapped diagnostics are reported at their checker locations, and cleanup runs in a `finally` block.
- **Validation:** Failure injection reconfirmed the original false successes before implementation. All 25 temporary failure-injection cases passed, covering executable failures, unsuccessful exits, missing/malformed JSON and diagnostic fields, mapped/unmapped diagnostics, clean output, and cleanup after extraction failure. Isolated `make linting` failure injection passed seven cases through each of the local and container script branches. After removing the temporary tests, `make test-all` passed all 381 existing tests with 100% configured statement coverage. `make linting` passed using the local `./venv` with standard `zlib`. Container branch injection exercised shell behavior using the local interpreter; a development-container run and the cross-platform CI matrix were not performed locally.

### E1-03 — Accept integer coordinates wherever numeric geometry is supported

- [x] **Work:** Correct the geometry hooks in `PyPDFForm/lib/hooks.py` so accepted integer coordinates are normalized and serialized like equivalent floats. Apply the change consistently to relevant coordinate and dimension properties, including supported per-option geometry.
- **Done when:** Setting `x = 123` changes the reopened field to 123; equivalent integer and float inputs agree. Invalid types fail without silently retaining the old geometry.
- **Basis and dependencies:** R10. Keep this focused on the documented numeric API; broader geometry validation belongs to E4-01.
- **Completed:** October 11, 2026, [PPF-2056](https://github.com/chinapandaman/PyPDFForm/issues/2056). Scalar integers and floats share one normalization helper for `x`, `y`, `width`, `height`, and checkbox/radio `size`. Scalar radio updates apply to every option. Invalid types, including booleans, raise `TypeError` inside the hooks before changing the annotation rectangle; a comment identifies the raise for a future centralized exception raiser. `None` still queues no update. Scope remains scalar-only: per-option list updates were unsupported before this change and now raise rather than being silently ignored.
- **Validation:** Reconfirmed the defect at pre-change commit `928cc13c`: integer `x = 123` reopened as `73.3365`, while float `x = 123.0` persisted. Added a happy path and an unhappy path test in `tests/test_functional.py`, covering reopened text/checkbox/radio geometry, integer/float byte equivalence, zero coordinates, preserved positions or dimensions, checkbox/radio size, and deferred rejection of strings, booleans, and lists. `make test-all` passed all 383 tests with 100% configured statement coverage, and `make linting` passed using the local `./venv` with standard `zlib`. The development container and cross-platform CI matrix were not run locally.

### E1-04 — Enforce choice-index bounds in schema and runtime validation

- [x] **Work:** Align dropdown and radio schemas with the valid index range and enforce the same bounds before updating PDF or middleware state. Handle empty option lists explicitly rather than generating a range that accepts unusable selections.
- **Done when:** Negative indices, indices equal to the option count, and larger values are rejected by both validation paths; first and last valid indices work. A failed selection leaves existing values and appearance states unchanged.
- **Basis and dependencies:** R10. Coordinates with E3-03 and E4-01; a small shared bounds check can precede the wider validation refactor.
- **Completed:** October 12, 2026, [PPF-2057](https://github.com/chinapandaman/PyPDFForm/issues/2057). `Dropdown` and `Radio` own their index schemas and bounds checks. `Widget` provides the shared prepare/apply flow, using `PreparedValue` from `base.py`. Filling prepares supplied and retained values once, then applies only supplied updates; new dropdown strings stage choices until preparation succeeds. Fields without options reject every integer index and are omitted from `sample_data`. Dropdown discovery returns an empty tuple for missing or empty options, honoring explicitly empty widget options over inherited options.
- **Documentation follow-up:** October 14, 2026. The completion audit found that the claimed User Guide updates were missing. Added [choice-index validation](../docs/fill.md#choice-index-validation), including bounds, empty options, schema/CLI checks, and the limited pre-mutation guarantee, plus [schema and sample-data guidance](../docs/inspect.md). Runtime behavior is unchanged.
- **Scope:** Out-of-range integers raise `ValueError` before widget values, pending hooks, or PDF state change. Dropdown string insertion, `None` assignments, and text behavior are preserved. Broader type validation remains E4-01; rollback for later hook, image, or serialization errors remains E5-02. The existing dropdown-zero read defect remains E1-05.
- **Validation:** Pre-change commit `e5da16b1` accepted `-999` in schemas; dropdown filling then raised `IndexError` after storing it, while radio filling silently accepted it. Regression tests cover valid endpoints, invalid indices, empty options, direct assignments, retained selections, staged choices, preserved state, and serialized dropdown `/V` and `/I` and radio `/V` and `/AS`. All 64 focused tests and all 385 tests passed with 100% configured statement coverage. `make linting`, `make format-code`, a strict MkDocs build, and `git diff --check` passed using local `./venv` with standard `zlib` and a temporary Pylint cache. Container, cross-platform CI, and viewer rendering were not run locally.
- **Documentation follow-up validation:** The three existing choice-index and sample-data tests passed. `make linting`, a strict MkDocs build, verification of the nine section anchors referenced by the E1-04/E1-08 follow-up, and `git diff --check` passed using local `./venv` with standard `zlib`. The full suite, container, cross-platform CI, and viewer rendering were not repeated for these documentation-only changes.

### E1-05 — Preserve dropdown selection zero

- [x] **Work:** Replace truthiness-based handling of the selected index with an explicit distinction between zero and no selection in the dropdown read path.
- **Done when:** Create → fill with index 0 → serialize → reopen returns 0, while an actually unselected field remains unselected. Include ordinary string options and the existing supported representation of empty values.
- **Basis and dependencies:** R07, a P1 finding. This is a separately useful repair; it does not resolve display/export conversion, which is E3-03.
- **Completed:** October 12, 2026, [PPF-2058](https://github.com/chinapandaman/PyPDFForm/issues/2058), verified at commit `5c66b16f`. `get_dropdown_value()` stores the matched option index directly, preserving zero instead of converting it to `None`. The two existing first-option extraction assertions now expect zero, and the image-fill fixture reflects retention of an existing zero selection. The reader docstring was corrected in a subsequent documentation-only follow-up to describe zero preservation and unchanged values when no choice matches.
- **Validation:** The pre-change reader from parent commit `cb9d675f` returned `None` for the same serialized zero selections that the current reader returns as zero. All 24 temporary acceptance cases passed across ordinary strings, single-space options, and an empty-string first option with the existing single-space creation workaround, in both appearance modes. Assertions covered live and reopened values, serialized `/V` and `/I`, retained selections during subsequent fills, and unselected fields with missing or null `/V`. An empty `/V` remains unselected when it matches no option, and selects zero when it matches the empty first option. All 97 focused tests and all 385 tests passed with 100% configured statement coverage; `make linting` passed using local `./venv` with standard `zlib` and a temporary Pylint cache. Both pages of the changed `560_expected.pdf` rendered identically to the previous fixture with Poppler at 100 DPI, and its dropdown choices and reopened selections were preserved.
- **Documentation follow-up validation:** `make linting` and `git diff --check` passed using the same local `./venv` with standard `zlib`. Behavioral tests and rendering checks were not repeated because the follow-up changes only the docstring and this plan.
- **Remaining limitations:** Display/export conversion remains E3-03. The existing default-fill appearance defect (E3-05) is now exercised by the retained zero selection in `560_expected.pdf`: field `Ct 2` has a string `/AP` instead of an appearance dictionary, despite the unchanged Poppler rendering. Development-container, cross-platform CI, and other-viewer checks were not run locally.

### E1-06 — Skip an empty rename commit during full-name merges

- [x] **Work:** In `wrapper.py`, avoid the unsupported full-name rename path when no rename is queued. Preserve the explicit limitation for an actual unsupported rename rather than suppressing all errors.
- **Done when:** Full-name wrappers containing distinct `left` and `right` fields merge successfully; true collisions still follow an explicit existing or documented limitation. Exercise page slices that rely on merging as well.
- **Basis and dependencies:** R09. Does not require choosing a new collision policy; E4-02 addresses broader identity and operand behavior.
- **Baseline:** Reconfirmed at pre-change commit `a4dd54cb`: merging distinct full-name `left`/`right` fields, merging matching partial names under distinct parents, and multi-page slices raised `NotImplementedError`.
- **Scope:** Addition now commits renames only when the right-hand wrapper has queued updates. Full-name collisions, direct rename methods, and pending renames after switching to full-name mode retain `NotImplementedError`. Ordinary queued renames still commit and modify the right-hand wrapper; broader collision and operand policies remain E4-02. The merge docstring describes these boundaries.
- **Validation:** The retained three regression tests cover distinct full-name merges, the existing collision error, and multi-page slices, checking reopened values, page order, and preserved source streams. All 10 focused tests and all 388 full-suite tests passed with 100% configured statement coverage for the full suite. `make linting`, `make format-code`, and `git diff --check` passed using local `./venv` with standard `zlib` and a temporary Pylint cache. The development container, cross-platform CI matrix, and viewer rendering were not run locally; the repair changes merge control flow rather than appearance generation.

### E1-07 — Allocate font resource names without assuming every name is numeric

- [x] **Work:** Restrict numeric suffix parsing in `font.py` to the exact resource-name pattern it owns, and allocate an unused name without changing existing arbitrary resource keys.
- **Done when:** `/FontA`, `/FCustom`, sparse `/F1` and `/F9` entries, and unrelated names all survive registration; the new resource does not collide and remains usable after reopening.
- **Basis and dependencies:** R12. Independent of registry cleanup in E2-04 and later resource ownership in E5-04.
- **Baseline:** At pre-change commit `0800f8de`, `/FontA` caused custom-font registration to raise `ValueError`. Regression cases also reproduced failures for non-numeric suffixes and non-ASCII digits in both `need_appearances` modes.
- **Completed:** October 14, 2026, [PPF-2060](https://github.com/chinapandaman/PyPDFForm/issues/2060). The allocator parses only `/F[0-9]+` names, preserves other resource keys, and retains the lowest unused numeric suffix, including existing leading-zero handling. Updated the allocator docstring and consolidated font tests in `tests/test_font_related.py`.
- **Validation:** All 402 full-suite tests passed with 100% configured statement coverage. After the final filename-only change, full collection, 27 focused tests, and Ruff linting/formatting checks passed; the full suite was not repeated. The 14 new regression cases verify allocation, preserved font resources, embedded TrueType bytes, and font use after reopening through generated text appearances. `make linting`, `make format-code`, and `git diff --check` passed using local `./venv` with standard `zlib`. Container, cross-platform CI, and viewer checks were not run locally; appearance generation is unchanged.

### E1-08 — Publish migration and capability guidance

- [x] **Work:** Draft the 5.6-to-6.0 migration guide and link it from appropriate documentation. Cover the Python minimum/support window, removed Python arguments and CLI options, available replacements or lack of equivalents, and the supported release/security policy. Add a compact table distinguishing signature images, signature fields, cryptographic signing, read-only fields, and flattening.
- **Done when:** Users can identify affected calls and supported alternatives, including the former `flatten` alias's read-only behavior, without assuming that read-only fields provide flattening or integrity protection. Explain the silent-keyword behavior in 6.0.0 and update the guide when E2-05 changes it. State where viewer and appearance limitations are documented.
- **Basis and dependencies:** R10; report §§5.6, 7.1–7.2. Verify statements against the release being documented; do not advertise planned fixes as delivered.
- **Completed:** October 14, 2026, [PPF-2061](https://github.com/chinapandaman/PyPDFForm/issues/2061). Added the [5.6-to-6.0 migration guide](../docs/news/2026-10-14.md) and linked it in the MkDocs News navigation. It covers the Python 3.11 minimum and 3.11–3.15 support/test window, removed Python/CLI options, before-and-after examples, automatic metadata preservation, silently ignored Python keywords, and latest-version-only security support.
- **Initial scope decision:** At the maintainer's request, the initial guide focused on migration changes and omitted the capability table and viewer/appearance limitations section because those capabilities are unchanged between 5.6.0 and 6.0.0.
- **Documentation follow-up:** October 14, 2026. Following the completion audit, the maintainer requested both omitted sections. Restored the broader completion criteria above and added the [capability table](../docs/news/2026-10-14.md#signatures-read-only-fields-and-flattening) and [viewer/appearance guidance](../docs/news/2026-10-14.md#viewer-and-appearance-limitations), with links to the relevant User Guide sections. E2-05 remains pending and must revisit the silent-keyword guidance when argument validation changes.
- **Initial validation:** Compared the `v5.6.0` and `v6.0.0` tags and checked the current implementation. Temporary assertion-based checks verified ignored removed Python arguments without deprecation warnings, preserved metadata, reopened field values and read-only flags, flag reversibility, removed CLI parameters, and the migrated CLI example. `make linting`, a strict MkDocs build, and whitespace checks passed using local `./venv` with standard `zlib`; the MkDocs build and whitespace checks were repeated after removing the capability sections. Full tests, the development container, cross-platform CI, and viewer rendering were not run for this documentation-only change.
- **Documentation follow-up validation:** Checked the capability statements against signature creation/filling, read-only flags, appearance handling, and the existing User Guide. The shared documentation checks recorded under E1-04 passed after restoring both sections. No runtime behavior or compatibility claims were changed, so the full suite and viewer checks were not repeated.
- **E2-05 follow-up:** October 29, 2026, [PPF-2075](https://github.com/chinapandaman/PyPDFForm/issues/2075). The silent-keyword section became [Removed Python arguments raise errors after 6.0.2](../docs/news/2026-10-14.md#removed-python-arguments-raise-errors-after-602). It limits the silent behavior to 6.0.0–6.0.2 and describes the `TypeError` in later releases without naming the next release. Validation is recorded under E2-05.

## Group 2 — Bounded repairs

These items change a complete operation or helper. They fit within the current architecture, but require failure-path and compatibility checks beyond a one-line repair.

### E2-01 — Make path-based output transactional

- [x] **Work:** Complete serialization before touching the destination, write a sibling temporary file, close it successfully, and atomically replace the destination in `PdfWrapper.write()`. Clean up failed temporary writes and preserve relevant file permissions. Make CLI overwrite paths use the same implementation.
- **Done when:** Hook, appearance-generation, temporary-write, and replacement failures preserve pre-existing destination bytes. Test both default in-place CLI updates and distinct outputs; successful writes reopen correctly. Document the weaker rollback guarantee for caller-owned streams.
- **Basis and dependencies:** R02, P1. Start immediately; no dependency on the inheritance fix in E3-04. Before implementation, settle behavior for symlinks and file metadata so replacement does not introduce an undocumented filesystem change.
- **Baseline:** Reconfirmed at pre-change commit `03bfe99f`: an injected deferred font-size hook failure truncated a 615,081-byte PDF to zero bytes through both `PdfWrapper.write()` and the CLI's default overwrite path. The document-level inherited-`/DA` hook failure also remains reproducible; fixing it is still E3-04.
- **Completed:** October 27, 2026, [PPF-2071](https://github.com/chinapandaman/PyPDFForm/issues/2071). `PdfWrapper.write()` serializes before output, then calls `write_path()` in `PyPDFForm/lib/egress.py` to write and close a sibling temporary file before atomic replacement. Failure cleanup handles partial writes and read-only temporary files. CLI writes already use the same wrapper method. Added two test functions in `tests/test_functional.py` and strengthened its existing write test; no new source or test files are required.
- **Confirmed policy and scope:** Follow symlinks, including dangling links, and replace their resolved targets while retaining the links. Preserve existing permission bits; new outputs have private permissions (0600 on POSIX). Ownership, ACLs, extended attributes, timestamps, and hard-link identity are not preserved; other hard links retain the old contents. The write docstrings describe the filesystem policy and weaker stream guarantee. A caller-owned stream can retain partial output on write failure, and truncation performed by the caller cannot be undone. The maintainer requested no User Guide change for this internal bug fix. Crash durability, concurrent-writer locking, and in-memory rollback remain outside this repair.
- **Validation:** All 18 focused write cases and all 418 full-suite tests passed, with 100% configured statement coverage for the full suite. The 16 added cases cover hook, appearance-generation, partial-write, close/flush, and replacement failures through library output, default in-place CLI updates, and distinct CLI outputs, plus symlink and hard-link behavior. Successful output is checked through reopened field values, PDF syntax, serialization byte equality, and POSIX permissions. `make test-all`, `make linting`, focused Ruff formatting checks, and `git diff --check` passed using local `./venv` with standard `zlib` and a temporary Pylint cache. The development container, cross-platform CI matrix, and viewer rendering were not run locally; appearance generation is unchanged by this file-publication repair.

### E2-02 — Preserve unrelated annotations during image and signature filling

- [x] **Work:** Replace the remove-all-and-selectively-restore path with removal or flattening of only the widgets consumed by the fill. Preserve other annotations by object identity, including unfilled signature/image widgets and fields addressed by full names. Refresh the affected wrapper view.
- **Done when:** Filling the first of two signatures retains the second, and notes, links, highlights, ordinary fields, and unfilled images survive. Inspect the annotation graph and reopened API, rather than checking only the original widget dictionary.
- **Basis and dependencies:** R03, P1. Coordinates with E3-06. If current cloning cannot satisfy these checks, expand the repair into E3-01 ownership work; do not make the whole E5 refactor a prerequisite.
- **Baseline:** Reconfirmed at pre-change commit `3b9fc375`: filling one of two signatures also removed the unfilled signature, an unfilled image field, and a note. Only the ordinary text field survived on reopening, while the live wrapper still exposed the removed fields.
- **Completed:** October 28, 2026, [PPF-2072](https://github.com/chinapandaman/PyPDFForm/issues/2072), commit `d6393e92`. Filling draws images onto page content and detaches only consumed widgets and empty field ancestors by object identity. The fill path avoids stripping and copying annotations, handles indirect annotation/field arrays, and refreshes the wrapper while retaining surviving middleware objects. Filling and AcroForm rebuilding skip non-widget annotations, preventing matching note titles from becoming form fields. Both User Guide sections briefly document drawing and field removal.
- **Validation:** Four added cases in `tests/test_signature.py` cover short/full names, sequential signature/image fills, preserved annotation and field references, reopened state, later value/style updates, invalid-image failure, and empty ancestor cleanup. A regression in `tests/test_functional.py` checks note-title collisions during AcroForm rebuilding. All 423 full-suite tests passed with 100% configured statement coverage. `make test-all`, `make linting`, and focused source formatting/whitespace checks passed using local `./venv` with standard `zlib`.
- **Rendering and limitations:** Poppler comparisons of 18 pages across 13 affected fixtures were identical except for three restored links. Synthetic short/full-name forms changed only inside the filled signature area; their second pages were unchanged. The development container, cross-platform CI matrix, and other PDF viewers were not run locally. Broader ownership/cache repairs and general in-memory rollback remain separate work.

### E2-03 — Treat radio selection as a group update

- [x] **Work:** Update the parent value once, set the selected widget appearance, and reset every non-selected sibling to `/Off`. Use actual appearance/export-state mappings rather than assuming one producer's names.
- **Done when:** A → B → A selection sequences agree across parent `/V`, child `/AS`, and reopened data. Include an initially selected external form and a group spanning pages; inspect and render representative output.
- **Basis and dependencies:** R08. Coordinates with E1-04; invalid indices must be rejected before group mutation.
- **Completed:** October 28, 2026, [PPF-2073](https://github.com/chinapandaman/PyPDFForm/issues/2073). Reconfirmed at baseline `15be7c6e` that selecting 0 → 1 → 0 left both child appearances active. The selected annotation now updates its parent's value once and every child's appearance through `/Kids`, including siblings on other pages. Selection uses the actual normal appearance name and retains `/Opt`, including duplicate export labels. The zero-based public API and existing pre-mutation index validation remain unchanged; fill helper docstrings describe the group update.
- **Validation:** Two regression cases in `tests/test_functional.py` cover the repository radio sample and Sejda, including a group spanning pages with page traversal order different from `/Kids` order. Initial selections are written independently of `PdfWrapper.fill`. Same-wrapper and reopened A → B → A sequences assert parent values, child appearances, and retained export mappings with pikepdf. The existing `test_invalid_choice_indices` covers rejection before changes to middleware state, pending hooks, or the PDF. All 425 tests passed with 100% configured statement coverage. `make test-all`, `make linting`, focused choice-selection tests and formatting checks, and `git diff --check` passed using local `./venv` with standard `zlib`.
- **Rendering and limitations:** Earlier Poppler checks covered the repository sample, Sejda, ReportLab, and a group spanning pages; changing selection affected the expected pages, including both pages of the spanning group, and returning to A restored identical pixels across all nine pages. Object comparisons of the 11 regenerated expected PDFs found only restored `/Opt` entries; all 19 rendered pages were pixel-identical. The development container, cross-platform CI matrix, and other PDF viewers were not run locally.
- **Maintainer review:** The maintainer completed the visual regression comparison, confirmed that the output looked correct, and regenerated the 11 expected PDFs.

### E2-04 — Clean up all temporary font registrations

- [x] **Work:** Track every inserted backend registry key independently of the current alias mapping. Put the full registration sequence inside cleanup protection, including partial setup failure and duplicate aliases. Document the supported concurrency assumptions while the registry remains global.
- **Done when:** Duplicate aliases, repeated operations, and an exception on a later registration all restore the registry to its starting state. Cleanup does not remove entries owned by other operations under the supported execution model.
- **Basis and dependencies:** R12. Coordinates with E1-07; concurrent resource management remains E5-04 if a local repair cannot guarantee it.
- **Baseline:** Reconfirmed at pre-change commit `eff4ad91`: duplicate aliases and a failure on a later font each leaked a temporary registration. Repeated draws with a duplicate alias leaked one additional registration per operation.
- **Completed:** October 28, 2026, [PPF-2074](https://github.com/chinapandaman/PyPDFForm/issues/2074). Registration setup now runs inside cleanup protection, with ownership tracked independently of alias lookup. Generated names skip existing registry keys, and cleanup removes an entry only while it still references the inserted font object. Repeated aliases continue to select the latest font.
- **Confirmed policy and scope:** Sequential and nested temporary registrations are supported. Callers must serialize entire threaded PyPDFForm and direct ReportLab operations in the same process using a shared caller-managed lock. The font documentation and helper docstring describe this policy; internal synchronization and broader concurrency guarantees remain E5-04.
- **Validation:** Retained five regression cases covering duplicate aliases and later setup failure, nested drawing failure with unrelated registrations, name collisions and replaced entries, and repeated public draws in both `need_appearances` modes. Reopened PDFs retain their fields and custom fonts; text extraction confirms the drawn text, and page resources retain the latest alias's embedded TrueType font. All 26 focused tests and all 430 full-suite tests passed, with 100% configured statement coverage. `make test-all`, `make linting`, `make format-code`, a strict MkDocs build to a temporary directory, and `git diff --check` passed using local `./venv` with standard `zlib` and a temporary Pylint cache. The built font page was checked for the expanded `info` card.
- **Rendering and limitations:** Before/after repeated-draw outputs were byte-identical in both `need_appearances` modes, and Poppler rendered all six pages pixel-identically. Expected PDFs were not regenerated. The development container, cross-platform CI matrix, and other PDF viewers were not run locally.

### E2-05 — Reject ignored arguments and distinguish empty input from invalid input

- [x] **Work:** Reject removed or unknown keyword arguments with actionable messages. Distinguish intentional empty construction from a nonexistent path or unsupported input. Define empty and single-item `PdfArray.merge()` behavior instead of exposing an incidental `IndexError`.
- **Done when:** `flatten=True` and removed metadata options cannot silently succeed, missing paths do not become empty PDFs, and zero/one/many-item merges follow documented behavior with regression coverage.
- **Basis and decisions:** R10. Recommended defaults: an explicitly empty constructor remains valid; a supplied invalid path raises; an empty merge yields an empty result and a one-item merge yields an independent result. Confirm compatibility and object-identity expectations before implementing these policy choices. Coordinate the migration text with E1-08.
- **Baseline:** Reconfirmed at pre-change commit `a98edafa` (6.0.2): `fill(flatten=True)`, `PdfWrapper(preserve_metadata=True)`, and misspelled keywords succeeded silently, leaving fields editable. Missing paths, directories, `None`, integers, and even existing `pathlib.Path` templates produced empty wrappers. Empty and one-item `PdfArray.merge()` raised `IndexError`, including a single-input CLI `create merge`. A missing font path was silently ignored.
- **Completed:** October 29, 2026, [PPF-2075](https://github.com/chinapandaman/PyPDFForm/issues/2075). The constructor and `fill()` validate keyword arguments before any mutation and raise `TypeError` in Python's unexpected-keyword format. Removed `preserve_metadata` and `flatten` add the release that removed them and migration guidance, both recorded per method and keyword in `REMOVED_KWARGS`; other unknown keywords list the supported ones. The shared file adapter opens `str` and `PathLike` paths directly, raises `TypeError` for unsupported types, and still treats empty bytes and empty readable streams as empty input. `PdfArray.merge()` returns a new empty wrapper for an empty array and never returns an input wrapper; such results are independent copies made by a private `PdfWrapper._copy()`. The copy reuses the current stream, title, and embedded font resources; copies the cached PDF version, font mappings, and registration events without embedding fonts again; and deep-copies widgets and pending key updates while sharing open stream values. Addition is unchanged. `PdfArray` moved from `types.py` into `wrapper.py` to remove their circular import; the public `PyPDFForm.PdfArray` import is unchanged. Pylint's module line limit (`C0302`) is disabled for the larger `wrapper.py`. Docstrings, the User Guide adapter tip, the bulk-merge note, and the [migration guide](../docs/news/2026-10-14.md#removed-python-arguments-raise-errors-after-602) describe the behavior.
- **Confirmed policy and scope:** Maintainer-confirmed: validated `**kwargs` rather than explicit signatures; `PathLike` templates are accepted; strict path handling applies to every adapter caller, so missing font, signature/image, and `RawImage` paths raise `FileNotFoundError`; invalid font bytes are still ignored. Merge identity and slicing behavior for `+` and `pages[...]` are unchanged and remain E4-02. The migration guide states the 6.0.0–6.0.2 behavior without naming the next release. The PPF-1599 tutorial test's `register_font` call referenced a nonexistent font and never registered it; the dead call was removed, and its expected PDF remains byte-identical.
- **Review follow-up:** [PR #2092](https://github.com/chinapandaman/PyPDFForm/pull/2092) review found two P2 regressions in the first merge-copy implementation, which rebuilt copies from bytes and replayed font registration. Middleware-only widget settings such as `preserve_aspect_ratio=False` were lost, changing image fill dimensions. Each copy also embedded registered fonts again, adding 91,161 bytes for `LiberationSerif-BoldItalic.ttf`. Both were reproduced and fixed by `_copy()`. Its private-state assignments use one method-scoped Pylint `W0212` suppression and an annotated local for Ruff. A second review found that copies dropped the cached PDF version. After a pending style change, the hook writer's PDF 1.3 header became authoritative on the copy, while the source restored 1.7 or 2.0; `_copy()` now copies the cached version as well. Separately, the existing behavior on `master` is unchanged: a wrapper that first reads its version after such a hook reports 1.3 instead of the template's version. The copy matches the source in that case.
- **Validation:** All 456 full-suite tests passed with 100% configured statement coverage. Added cases cover rejected constructor/fill keywords with unchanged state and read-only flags, template inputs (`Path`, empty inputs, missing paths, directories, unsupported types), missing font and image paths with preserved annotations, and zero/one-item and empty-padded merges. Merge cases check independence, inherited parameters, page counts, and live and reopened data. They also check byte-identical copies and copies of copies with unchanged font lists, preserved signature settings with identical fill output, pending key updates, and shared open JavaScript files. Version cases cover PDF 1.7 and 2.0 with a pending style change before one-item and empty-padded merges, checking the property, serialized header, and bytes. Each new merge test fails against the review baseline it addresses. A single-input CLI merge now succeeds. `make test-all`, `make linting`, a strict MkDocs build, Ruff formatting checks, and `git diff --check` passed using local `./venv` with standard `zlib`.
- **Remaining limitations:** Live data reports an unchecked checkbox as `False`, while reopened data reports `None`; that snapshot inconsistency predates this change and remains outside E2-05. The development container, cross-platform CI matrix (including the Windows directory error type), and viewer rendering were not run locally; no appearance generation changed.

### E2-06 — Validate property applicability in CLI field updates

- [x] **Work:** Validate the field type as well as the property name and value before assigning updates. Reuse library-side applicability checks so direct callers and CLI users cannot receive success for unsupported properties.
- **Done when:** Updating checkbox `max_length` fails with the field name and unsupported property; supported text updates succeed. A batch with one incompatible property leaves the document unchanged.
- **Basis and dependencies:** R10. This can establish a small applicability map now; E4-01 later consolidates validation without delaying the repair.
- **Baseline:** Reconfirmed at pre-change commit `80d45380` (6.0.2): `update field --field check --max_length 5` exited 0, and the reopened checkbox had no `max_length`. Direct assignments such as `pdf.widgets["check"].max_length = 5` or `size` on a text field queued no hook and raised nothing.
- **Completed:** October 30, 2026, [PPF-2076](https://github.com/chinapandaman/PyPDFForm/issues/2076). Each middleware subclass declares its type-specific properties in a class-level `TYPE_SPECIFIC_PROPERTIES` set: Text has `font`, `font_size`, `font_color`, `comb`, `alignment`, `multiline`, and `max_length`; Checkbox has `size`; Dropdown has `font`, `font_size`, `font_color`, and `choices`. Radio and Image inherit their parents' sets. The base `Widget` keeps an empty set, collects every subclass's declarations in `__init_subclass__`, and calls `check_property_supported()` from `__setattr__`. A property declared only by other widget types raises `AttributeError` naming the widget type, field, and property before any hook or tracked attribute changes. `update field` checks every requested field and property before registering fonts or assigning updates, and reports failures as parameter errors under `--file` or `--field`.
- **Confirmed policy and scope:** Maintainer-confirmed: rejection applies to any value, including `None`, and only to declared type-specific property names; other attribute names, including misspelled properties, remain unchecked. Per-subclass declarations were preferred over a module-level constant or class-level hook maps, so each property name also appears in its class's `SET_ATTR_TRIGGER_HOOK_MAP` update. Docstrings describe the check. The maintainer judged a User Guide note unnecessary because each style section already names its field type and the error message identifies the field and property; the migration guide is unchanged. The CLI schema still validates property names without field types; consolidation remains E4-01.
- **Validation:** All 464 full-suite tests passed with 100% configured statement coverage. A parametrized case in `tests/test_widget_attr_trigger.py` covers Text, Checkbox, Radio, Dropdown, Signature, and Image, assigning each unsupported property with a value and with `None`; it checks the message and unchanged hooks, tracked attributes, and PDF bytes. Two cases in `tests/cli_unhappy_path/test_cli_errors.py` cover the `--field` options form without creating output and an in-place file batch that mixes a custom font, supported text and checkbox updates, and checkbox `max_length`. The batch leaves the PDF byte-identical; without the incompatible property, the same batch succeeds and the reopened text `max_length` and checkbox size are applied. All eight new cases fail against the pre-change source. Each subclass's declared set matched the hook-map keys it adds. `make test-all`, `make linting`, Ruff formatting checks, a strict MkDocs build, and `git diff --check` passed using local `./venv` with standard `zlib`.
- **Remaining limitations:** Declared property sets and hook-map keys are maintained separately, so a property added to one must be added to the other. Value semantics, such as `comb` requiring `max_length`, are unchanged. The development container, cross-platform CI matrix, and viewer rendering were not run locally; no appearance generation changed, and expected PDFs were not regenerated.

### E2-07 — Resolve internal links to destination page references

- [ ] **Work:** Retain user-facing page numbers in the annotation definition, validate their bounds, and resolve them against the destination writer when inserting local links. Distinguish local from remote destination semantics.
- **Done when:** A link to page 2 serializes an indirect reference to that page and works in a viewer. Merge and reorder cases keep the intended target; out-of-range targets fail before mutation.
- **Basis and dependencies:** R11. Coordinates with E3-01 for extraction behavior when the target page is excluded.

### E2-08 — Protect contributor edits during PDF comparison

- [ ] **Work:** Remove the comparison helper's unconditional restoration of whole fixture directories. Prefer generating and comparing in an isolated temporary checkout or output area; define how existing local fixture edits are included. If isolation cannot be implemented in the first repair, reject affected dirty paths before any regeneration.
- **Done when:** In a disposable repository, staged and unstaged fixture edits, untracked files, and unrelated work survive successful comparisons, generation failures, and interruptions byte-for-byte, with the index preserved. Diagnostics identify where comparison artifacts live.
- **Basis and dependencies:** R13. Applies to `scripts/pdf_diffs.sh` and its generation helpers. A clean-tree guard is a containment fix; isolated comparisons are the stronger final outcome.

### E2-09 — Make release-helper failures explicit and target an exact commit

- [ ] **Work:** Make `scripts/create_release.py` fail on unexpected API responses, validate semantic version progression, and pass an explicit commit target. Handle request errors and timeouts without reporting success.
- **Done when:** Mocked rejected requests fail the process; equal, older, malformed, and permitted newer versions have intentional outcomes; the requested target SHA is explicit and checked. Cover retry/idempotency behavior without creating a real release during tests.
- **Basis and dependencies:** R13. Coordinates with E3-08. Maintainer release initiation and the existing release policy remain in force.

## Group 3 — Coordinated correctness and delivery work

These items touch multiple representations or workflow stages. They should be split into small contributions with shared acceptance criteria, without postponing the urgent repairs until a broad redesign.

### E3-01 — Repair selected-page ownership and excluded-content retention

- [ ] **Work:** Change page extraction and annotation cloning in `wrapper.py` and `watermark.py` to build a destination graph deliberately. Remap widget `/P`, keep only relevant children of shared fields, and prevent annotation backreferences from importing the original page tree. Handle links to excluded pages under an explicit policy.
- **Done when:** The report's two-page reproduction passes and excluded text, image payloads, and field values are absent from the serialized object graph. Every retained widget belongs to a retained destination page. Include shared fields across pages, hierarchical parents, multiple selections, and internal links; page count alone is insufficient.
- **Basis and decisions:** R01, P1; report appendix A. Start in the first maintenance tranche. Recommended policy for unsupported cross-page dependencies: reject with an explanation rather than silently import excluded pages. Extraction is not a general redaction guarantee. Coordinates with E2-07 and E3-02.

### E3-02 — Preserve and edit the AcroForm catalog consistently

- [ ] **Work:** Stop rebuilding `/AcroForm /Fields` solely from recognized page widgets. Preserve catalog-only and unknown fields on no-op serialization. For explicit removal, update root fields, parent `/Kids`, page `/Annots`, and dependent entries such as calculation order, including removal of the final field.
- **Done when:** No-op serialization retains `hidden_business_id`, unsupported fields, resources, and valid hierarchies. Removing one field, one child, a radio group, or all fields leaves no corresponding active catalog entries or values. Unknown structures survive unrelated edits.
- **Basis and decisions:** R05–R06, P1; report appendix C. Coordinate preservation and deletion so fixing one cannot undo the other. Define unreachable-object cleanup separately; field removal must not be advertised as redaction. This repair precedes, rather than requires, E5-01.

### E3-03 — Normalize dropdown display values, exports, and selections

- [ ] **Work:** Introduce one internal option representation with explicit display/export values and central conversion rules. Use it across discovery, creation, choice updates, fill, serialization, and reopen. Specify how index, label, export, and editable string inputs are accepted and disambiguated.
- **Done when:** The report's tuple-string reproduction is eliminated. Create → fill → reopen and update choices → fill → reopen preserve the intended `/Opt`, `/V`, and selection index. Cover distinct and duplicate labels, exports, empty values, index zero, unknown strings, and forms from other producers.
- **Basis and decisions:** R07, P1. Recommended default: explicit index/export semantics, with ambiguous label matching rejected unless the caller chooses a policy. Confirm the public tuple convention and PDF/viewer mapping before changing behavior. Incorporates E1-05; coordinates with E1-04 and E4-01.

### E3-04 — Resolve inherited field attributes and parse default appearance safely

- [ ] **Work:** Replace repeated widget/immediate-parent lookups with a cycle-aware resolver that follows valid field inheritance and applicable AcroForm defaults. Apply it first to `/DA` and styling, then the field properties relying on the same rules. Replace fragile string splitting with token-aware default-appearance handling.
- **Done when:** Multi-level inherited font/appearance settings can be inspected and changed; widget overrides retain precedence. Missing values, cycles, and malformed appearance data yield deliberate errors without partial mutation. The inherited-`/DA` reproduction no longer raises the reported `KeyError`.
- **Basis and dependencies:** R02 and R10; report §5.5. E2-01 protects files independently. Do not assume every PDF property inherits by identical rules.

### E3-05 — Establish a valid default appearance policy

- [ ] **Work:** Remove assignments of value strings to `/AP` in text and dropdown fill paths. Implement a documented policy for preserving compatible appearances, generating valid appearances, or requesting viewer regeneration with valid structure. Make unsupported rendering cases explicit.
- **Done when:** Emitted `/AP` entries, where present, are valid dictionaries with valid referenced streams/state dictionaries. Representative outputs render in at least two independent engines, with printing checked as appropriate. Include Unicode, custom fonts, multiline text, alignment, and pre-existing appearances.
- **Basis and decisions:** R04, P1. Recommended default: a valid, tested path for the supported feature subset, with explicit limitations elsewhere. Do not simply enable the current generator for all input: the review identifies documented limitations. Record the policy before implementation; E4-03 formalizes the broader viewer matrix and E6-01 is optional expansion.

### E3-06 — Keep live middleware consistent with committed PDF state

- [ ] **Work:** Inventory state-changing wrapper operations and give each an explicit refresh or invalidation step for widgets, flags, renamed keys, and removed fields. Stage validation before updating live values; avoid preserving obsolete attributes through rebuilds.
- **Done when:** After fill, read-only updates, styling, removal, and merge, inspecting the current wrapper agrees with reopening its output for the supported properties. A rejected multi-field operation leaves both representations unchanged. Repeated reads do not reapply stale hooks.
- **Basis and dependencies:** R03 and R10; report §3.1. Coordinates with E2-02 and E3-02. Establish the behavior in the current design first; E5-02 later replaces scattered synchronization with transactions.

### E3-07 — Add independent semantic regression contracts across platforms

- [ ] **Work:** Convert the report's reproductions into targeted pytest regressions accompanying their fixes, and add reusable assertions for ownership, catalog contents, value round trips, preservation, and valid appearance types. Separate compression-sensitive byte comparisons from assertions that can run on every supported platform, including Windows and zlib-ng CI environments.
- **Done when:** Each fixed finding has a test that would fail on the reviewed defect independently of regenerated bytes. Compression-specific skips no longer suppress the corresponding semantic checks. Expected PDFs are reviewed against meaning and rendering before replacement; retain the existing canonical byte tests.
- **Basis and dependencies:** Report §§5.1–5.2 and 8. Coordinates with all repairs; tests ship with each fix rather than waiting for a large test-suite conversion. Broader sequence and hostile-input coverage continues in E4-03.

### E3-08 — Validate the exact release revision and artifact before publication

- [ ] **Work:** Make publication depend on successful checks for the final release SHA, including any formatting/version-bump commit. Build the artifact once, install it into a clean environment outside the checkout, run library/CLI smoke tests, and publish that same validated artifact. Retain restricted permissions and human release initiation.
- **Done when:** Failed tests, linting, builds, or artifact smoke tests block publication; evidence identifies the checked SHA and artifact. A source-tree import cannot accidentally satisfy the wheel test. Verify version, imports, create/fill/read, and CLI behavior with applicable extras installed; check package contents from the source distribution too.
- **Basis and dependencies:** R13; report §7.4. Requires E1-01/E1-02 for reliable reused gates and coordinates with E2-09. Update the Developer Guide when the workflow changes; test orchestration without publishing.

### E3-09 — Separate reproducible fixtures from dependency compatibility testing

- [ ] **Work:** Define a reproducible canonical environment for byte fixtures, recording Python, compression, and backend versions. Keep independent latest/minimum dependency coverage, broaden version-edge coverage where private APIs justify it, and pin moving build inputs where practical with an update process.
- **Done when:** Contributors can reproduce canonical fixture bytes; compatibility failures can be attributed to recorded environments. Latest/minimum jobs exercise semantic contracts, while third-party Action or container pins have an intentional update mechanism. Runtime dependency ranges remain a separate library-support decision.
- **Basis and dependencies:** Report §§5.2 and 7.6. Coordinates with E3-07/E3-08. Avoid turning one canonical environment into a claim that other supported combinations are untested or unsupported.

### E3-10 — Prevent maintenance automation from hiding unresolved defects

- [ ] **Work:** Update `scripts/close_staled_issues.py` to exclude confirmed correctness defects, security-sensitive reports, and roadmap decisions under a maintainer-defined classification policy. Add pagination, timeouts, response checks, and exclusion of pull-request records. Document responsibility for triage and compatibility decisions.
- **Done when:** Mocked paginated data retains exempt issues and pull requests; API failures stop safely. The policy explicitly separates inactivity from resolution and has a reviewable local preview of intended actions.
- **Basis and decisions:** Report §7.5. Maintainers must choose the classifications and authority for closure before enabling changed behavior. This item proposes tool and policy work, not creating or closing issues as part of this document.

## Group 4 — Subsystem improvements

These efforts consolidate policies and introduce reusable infrastructure. They should use the earlier correctness tests as constraints and preserve established entry points where practical.

### E4-01 — Unify validation and public error behavior

- [ ] **Work:** Build one library validation layer for field values, choice ranges, geometry, page bounds, property applicability, and operation arguments. Derive or check CLI schemas against it. Introduce a small documented error taxonomy for invalid input, unsupported features, invalid operations, and output failures, retaining original causes.
- **Done when:** Library and CLI callers accept/reject the same boundary inputs. Schema-accepted data does not subsequently fail a basic range/type check. Mixed valid/invalid batches are rejected before mutation, CLI messages are concise, and unexpected programming errors are not hidden by a blanket handler.
- **Basis and dependencies:** R10; report §5.4. Consolidates E1-03/E1-04 and E2-05/E2-06. Requires agreement on compatibility for changed exception types and strictness; introduce that behavior incrementally with documented migration where necessary.

### E4-02 — Make field identity and merge semantics predictable

- [ ] **Work:** Specify short-name versus full-name lookup, hierarchical collisions, repeated widgets, operand mutation, and empty-input identity. Implement an explicit collision policy and a way to obtain the resulting name mapping. Prefer a non-mutating merge path while preserving or deliberately migrating documented existing behavior.
- **Done when:** Distinct full names merge, identical partial names under different parents remain distinguishable, true collisions follow the selected policy, and reuse of source wrappers produces predictable results. Cover extraction → merge, page slices, custom fonts, and empty/one-item inputs.
- **Basis and decisions:** R09; report §§3.2 and 7.2. Recommended new behavior: deterministic, explicit collision handling and independent output objects. Random suffixes are already documented, so changing the existing default requires a compatibility decision. Builds on E1-06 and E3-02; E5-01 supplies the comprehensive field/widget model if the current representation cannot support the contract.

### E4-03 — Establish an interoperability corpus and operation-sequence suite

- [ ] **Work:** Curate small synthetic and appropriately shareable real-world PDFs covering producers, hidden fields, inheritance, mixed annotations, hierarchy, duplicate names, fonts, and supported languages. Record expected semantics and rendering for each. Add generated sequences of fill, restyle, rename, merge, extract, remove, and reopen; use ordinary pytest first where sufficient.
- **Done when:** A named viewer/renderer matrix distinguishes tested, unsupported, and unverified features. At least two independent rendering engines cover the appearance corpus. Sequence tests detect state divergence, and bounded malformed/cyclic-input checks run in isolated workers with resource limits. Test documentation explains how to review fixture changes independently.
- **Basis and dependencies:** Report §§5.1–5.2, 5.7, and 8. Builds on E3-07 and the appearance policy in E3-05. Publish processing-boundary guidance: application isolation/resource limits, encryption, existing digital signatures, accessibility, and PDF/A remain unverified until specifically tested. Do not infer these capabilities from ordinary form-fill success.

### E4-04 — Measure complete workflows and establish performance budgets

- [ ] **Work:** Add reproducible benchmarks for style → fill → write, mixed image/text filling, single-page extraction, 10/100-form merges, and repeated operations in a persistent worker. Measure elapsed time, peak memory, output size, parse/write counts, PDF object counts, and resource counts, with cold/warm cache conditions recorded.
- **Done when:** Repeatable measurements and environment details replace extrapolation from the report's small single-run benchmark. Maintainers select workload-specific regression budgets from the baseline; comparisons also verify preservation and round-trip correctness.
- **Basis and dependencies:** Report §6. Benchmark scaffolding can start early, but use E3-01/E3-02-corrected outputs for optimization decisions. No throughput or memory target is implied by this plan; record the target workload and acceptable tradeoffs before promising one.

### E4-05 — Implement selective page extraction with one source parse

- [ ] **Work:** Introduce a selective/lazy extraction path that reuses a source parse and deliberate cloning map, rather than building all page wrappers for `pages[0]`. Preserve the existing eager interface through an adapter if changing it would break sequence behavior.
- **Done when:** Extracting one page does not serialize all pages; page order, slicing, error behavior, and supported field/link semantics remain correct. Benchmarks show improved scaling and memory use on representative documents without excluded-content retention.
- **Basis and dependencies:** Report §6.1. Requires E3-01 and E4-04; coordinates with E4-02 for slice/merge semantics. Specify iterator lifetime and behavior after source-wrapper mutation if the new API is lazy.

### E4-06 — Bound retained document data and expose cache lifecycle controls

- [ ] **Work:** Inventory PDF/font/image caches and their retained bytes. Add supported clearing/disabling controls; evaluate document-scoped caches or a measured byte budget instead of relying solely on entry counts. Define cache ownership, invalidation, and behavior in long-lived workers.
- **Done when:** Repeated large-document workflows stay within an agreed retained-memory budget, clearing/disabling releases cache-owned references, and outputs remain identical in meaning with caches enabled or disabled. Document that clearing references is not a secure memory-erasure guarantee.
- **Basis and dependencies:** Report §6.2. Requires E4-04 measurements and coordinates with E4-05/E5-02. Preserve useful bounded caching unless measurements justify replacement; do not describe the current entry-limited caches as unbounded.

### E4-07 — Strengthen types at the boundaries that caused defects

- [ ] **Work:** Introduce typed option, field-reference, and operation records where dynamic dictionaries obscure contracts. Correct nullable annotations and progressively restore disabled Pyright diagnostic categories for migrated modules. If consumer typing is a supported goal, package `py.typed` and test an external consumer of the wheel.
- **Done when:** Type checking catches representative invalid option/property/reference combinations without broad suppressions. Runtime tests still cover PDF semantics. The wheel includes the intended typing assets, and consumer checks run without importing the checkout.
- **Basis and decisions:** Report §5.3. Builds on E3-03 and E4-01; coordinates with E3-08 for artifact checks. Confirm the scope of consumer typing before making it a support promise. Avoid a repository-wide annotation rewrite unrelated to the defect boundaries.

## Group 5 — Architectural refactoring

These changes alter internal ownership and execution. Keep `PdfWrapper` and documented workflows as compatibility boundaries, and migrate one operation family at a time behind the earlier regression contracts. Merely moving methods into different files does not complete these items.

### E5-01 — Introduce a document-owned field graph

- [ ] **Work:** Model root fields, hierarchy, stable object identity, inherited attributes, and multiple widget appearances separately. Preserve catalog-only and unknown fields as graph members even when no middleware class can expose them. Make middleware a view over that graph rather than the definition of all document content.
- **Staging:** Introduce read-only graph discovery and compare it with existing discovery; migrate inspection next, then fill/removal, then merge/extraction. Keep one authoritative representation for each migrated operation and retire the corresponding reconstruction paths.
- **Done when:** Repeated non-radio widgets no longer collapse into one lost appearance; hidden/unknown fields survive; lookup and serialization agree on identity and parent/child relationships. All earlier catalog, hierarchy, merge, and preservation contracts pass through the new model.
- **Basis and dependencies:** Report §§3.1–3.3 and 5.5. Requires the semantics established in E3-02/E3-04; coordinates with E4-02. Document invariants and extension rules so contributors can add a field type without recreating preservation bugs.

### E5-02 — Replace scattered state transitions with mutation transactions

- [ ] **Work:** Define a validate → stage → apply → serialize → publish lifecycle, with rollback on failure. Bring PDF state, widget views, deferred hooks, attribute tracking, and font replay under explicit ownership. Track dirty operations so unchanged reads need not repeatedly reconstruct the document, and batch compatible edits into one serialization boundary.
- **Staging:** Start with one operation family and fault injection at every stage; migrate other families after the behavior is stable. Preserve the current public entry points while deciding how retained middleware references behave after a commit.
- **Done when:** Failed operations leave both live and serialized state unchanged, repeated reads are semantically idempotent, and operation sequences agree with reopened results. Benchmarks demonstrate fewer parses/writes without unbounded memory retention or deferred surprises at output time.
- **Basis and dependencies:** Report §3.3 and §6.3; R10. Requires E3-06, E4-01, and E5-01 for the shared state model; uses E2-01 for filesystem publication. File replacement alone is not an in-memory transaction.

### E5-03 — Centralize graph-preserving copy, merge, and extraction

- [ ] **Work:** Build shared operations for transferring fields, annotations, pages, and resources with explicit destination ownership and source-to-destination identity maps. Define a preservation matrix for document-level structures such as metadata, forms, calculation order, links, and other supported references. Preserve unknown structures conservatively or reject operations whose preservation cannot be established.
- **Staging:** Move the verified extraction repair into the shared mechanism, then annotation copying and merge. Remove duplicate ownership logic only after each migrated path passes its existing semantic corpus.
- **Done when:** Every supported operation retains valid references and only its intended content; excluded page payloads cannot return through alternate copying paths. Shared fields/resources are handled consistently, and unsupported structures produce documented outcomes rather than silent deletion.
- **Basis and dependencies:** R01, R03, R05–R06, R09, R11; report §3.3. Requires E5-01 and the repaired contracts in E3-01/E3-02; coordinates with E5-02. Keep extraction and field removal distinct from redaction.

### E5-04 — Isolate backend details and resource ownership

- [ ] **Work:** Introduce explicit adapters around pypdf object manipulation, ReportLab drawing/font registration, and pikepdf appearance generation. Move private backend API access behind these boundaries. Establish document-owned font/resource identity, deduplication, deterministic cleanup, and a documented concurrency policy.
- **Staging:** Wrap existing behavior before changing engines; migrate font registration/replay and appearance generation first where the review identifies concrete coupling. Add adapter contract tests against supported dependency edges.
- **Done when:** Backend version changes are contained to adapters and their tests; repeated style/fill/draw operations do not accumulate unnecessary font resources or registry entries. Supported concurrent workflows follow a tested isolation/synchronization policy, and failures clean up resources predictably.
- **Basis and dependencies:** R12; report §§3.2–3.3, 6.3, and 7.6. Builds on E2-04, E3-09, E4-04, and E5-01. Wrapping can begin earlier; complete resource ownership coordinates with E5-02. This is not a requirement to replace all three dependencies.

## Group 6 — Conditional redesign or rewrite

These are decision-gated options, not scheduled commitments or prerequisites for repairing R01–R13. Select one only after the previous groups expose a specific unmet requirement and measurements support the investment. Each option starts with a bounded design/prototype effort and a written proceed/stop decision.

### E6-01 — Build or adopt a broader appearance and text-layout engine

- [ ] **Trigger:** Verified user demand requires Unicode shaping, multiline layout, alignment, font fallback, or printing behavior that the supported appearance path cannot deliver reliably.
- **Work:** Define the required language/layout corpus; compare extending the current generator, integrating a specialized engine, or owning a new renderer. Prototype editable field appearances with correct resources, then evaluate fidelity, packaging, licensing, performance, and maintenance cost.
- **Proceed/stop gate:** Proceed only if the prototype passes the agreed multi-engine rendering corpus and maintains correct form values/editability. Otherwise retain the valid limited policy and document unsupported cases.
- **Basis and dependencies:** R04; report §§5.6 and 7.2–7.3. Requires E3-05, E4-03, and a stable backend boundary from E5-04. This is a capability expansion, not justification to defer fixing invalid `/AP` objects.

### E6-02 — Replace a backend subsystem only after a comparative prototype

- [ ] **Trigger:** Measured correctness, resource, or dependency-maintenance limits remain after adapter isolation and focused repairs, and cannot reasonably be solved within the current backend.
- **Work:** Select one bounded subsystem—such as page-graph transfer or appearance generation—and implement a candidate behind the same adapter contract. Compare the existing and candidate implementations over the preservation corpus, dependency/platform support, installed size, speed, memory, and failure behavior.
- **Proceed/stop gate:** Adopt only if the candidate meets all required semantics and offers a material documented benefit with an acceptable migration/maintenance cost. Keep a rollback path and avoid an all-backend replacement by default.
- **Basis and dependencies:** An architectural option derived from report §3.3, not a confirmed need or a named recommendation to change dependencies. Requires E4-03/E4-04 and E5-04; narrower replacement precedes consideration of E6-04.

### E6-03 — Design a major-version public API around explicit documents and operations

- [ ] **Trigger:** The preserved wrapper API prevents clear transactions, stable field handles, non-mutating merges, or lazy extraction from being exposed without persistent surprises.
- **Work:** Draft a public API proposal separating document state, field/widget views, operations, and serialization. Prototype migration of real documentation examples; compare compatibility adapters and deprecation paths with retaining the current API. Specify object lifetimes, exception types, iteration, and commit behavior.
- **Proceed/stop gate:** Proceed only when examples demonstrate a clear user benefit, existing workflows have migration paths, and maintainers accept the compatibility cost under Semantic Versioning. Otherwise retain the current entry points over the improved internals.
- **Basis and dependencies:** Derived from report §§3.1–3.3 and 7.2. Requires evidence from E4-02 and E5-01/E5-02. The current API's convenience is a strength to preserve, not itself a defect.

### E6-04 — Evaluate a core rewrite as the final fallback

- [ ] **Trigger:** A written assessment shows that incremental graph ownership, transactions, and subsystem replacement cannot satisfy agreed preservation, performance, or support requirements at sustainable cost.
- **Work:** Compare continued refactoring with a replacement core using the same conformance corpus. Inventory compatibility obligations, undocumented but relied-on behavior, staffing, maintenance during coexistence, migration stages, and rollback. Prototype the hardest end-to-end workflow before authorizing full implementation.
- **Proceed/stop gate:** The default is **do not rewrite**. Proceed only with measured evidence, maintainer approval of scope/cost, a migration plan, and a prototype that matches required semantics and improves the identified limits. A replacement must pass the existing and independent semantic suites; fewer modules or cleaner code alone is insufficient.
- **Basis and dependencies:** The source review explicitly says a wholesale rewrite is unnecessary on its evidence. This item describes the most disruptive possible endpoint requested by the effort grouping, not a recommendation that it be undertaken. Reassess only after E5 outcomes and relevant E6 prototypes.

## Recommended execution sequence

Use these tranches to schedule work; use the six groups above to size it. Independent small fixes can proceed alongside urgent larger repairs.

| Tranche | Selected actions | Exit condition |
| --- | --- | --- |
| 1 — Contain immediate harm | E2-01 safe writes; E2-02 annotation preservation; E3-01 selected-page isolation; E1-01/E1-02 reliable checks | Failed output preserves existing files; unrelated annotations survive; extracted output excludes unintended page payloads; check failures cannot report success |
| 2 — Restore form correctness | E3-02 catalog changes; E3-03 dropdown model with E1-05; E2-03 radio selection; E3-04 inheritance; E3-05 appearances; E3-06 state consistency | Independent readers, field graphs, live state, and rendered output agree for supported operations |
| 3 — Make composition and delivery dependable | Remaining E1/E2 repairs; E3-07 through E3-10; E4-01/E4-02 as needed | Invalid input fails clearly; merges behave intentionally; semantic CI and validated artifacts support the release; migration guidance is current |
| 4 — Improve assurance and scale | E4-03 through E4-07 | Tested compatibility boundaries, performance baselines, faster selective extraction, measured cache limits, and stronger boundary types |
| 5 — Consolidate architecture | E5-01 through E5-04 in incremental slices | One authoritative field model, transactional state, shared ownership logic, and isolated backends satisfy the existing contracts |
| 6 — Reassess remaining gaps | Only justified E6 items | A documented proceed/stop decision for each experiment; no automatic rewrite commitment |

E3-07 regression assertions accompany fixes in tranches 1 and 2; they are not postponed until tranche 3. Similarly, use a minimal rendering corpus for E3-05 before the broader E4-03 effort. File-safety containment can ship before the complete maintenance backlog, but release notes must state which findings remain unresolved. Release safeguards should land before the release that relies on them.

## Finding-to-action map

This map makes the primary repair for every numbered finding explicit. Later architecture items generalize those repairs; they must not become a reason to postpone them.

| Source finding | Primary repair | Supporting or longer-term work |
| --- | --- | --- |
| R01 — Excluded page content retained | E3-01 | E2-07, E3-07, E4-05, E5-03 |
| R02 — Failed writes truncate files | E2-01 | E3-04 for inherited appearance, E5-02 for in-memory transactions |
| R03 — Unrelated annotations/signatures removed | E2-02 | E3-06, E5-01, E5-03 |
| R04 — Invalid appearance entries | E3-05 | E4-03; E6-01 only for justified capability expansion |
| R05 — Catalog-only fields dropped | E3-02 | E5-01, E5-03 |
| R06 — Removed fields retained in catalog | E3-02 | E3-07, E5-01 |
| R07 — Dropdown values corrupted | E1-05, E3-03 | E1-04, E4-01, E4-07 |
| R08 — Multiple radio appearances active | E2-03 | E1-04, E3-07 |
| R09 — Full-name merges fail | E1-06 | E4-02, E5-01, E5-03 |
| R10 — Validation/state inconsistencies | E1-03/E1-04, E2-05/E2-06, E3-04/E3-06 | E1-08, E4-01, E4-07, E5-02 |
| R11 — Incorrect local link destinations | E2-07 | E3-01, E5-03 |
| R12 — Font naming/registration problems | E1-07, E2-04 | E4-04, E5-04 |
| R13 — Quality/release safeguards | E1-01/E1-02, E2-08/E2-09, E3-08 | E3-07, E3-09 |

Additional recommendations are covered by E1-08 (migration/support guidance), E3-09 (dependency reproducibility), E3-10 (backlog maintenance), E4-03 (interoperability and processing boundaries), E4-04 through E4-06 (performance/cache lifecycle), E4-07 (typing), and E5-01 through E5-04 (architecture and contributor knowledge).

## Completion and validation rules for future implementation

An action is complete when its stated behavior is independently demonstrated, not when code is merely changed or fixtures are regenerated. For a maintenance release claiming to address the review, use its §7.4 checklist together with the finding map above; all findings claimed as fixed need passing regression evidence.

1. **Reconfirm the baseline.** The source report describes a particular commit. Reproduce the relevant failure or explain intervening changes before implementing a repair. Keep policy decisions and unsupported cases explicit.
2. **Select the runner correctly.** Run `make check-zlib` from the repository root before using a runner. Use `./venv` for standard `zlib`; use the development container for `zlib-ng`, as required by `AGENTS.md`. Cross-platform CI semantic coverage does not override this local runner rule.
3. **Start narrow, then run required gates.** Use focused pytest selections consistent with the Makefile/Developer Guide while developing. For implementation changes, run `make test-all` and `make linting` in the selected environment and meet the existing 100% statement-coverage requirement. Supplement coverage with semantic assertions; it does not establish PDF correctness by itself.
4. **Review output independently.** Check PDF object types/references, reopened values, and preserved content for the affected operation. Use representative rendering when appearances change. Add failure injection for transactional and tool/workflow repairs. Do not substitute expected-byte regeneration for these checks.
5. **Keep documentation and artifacts scoped.** Update relevant user docs/docstrings for changed behavior and Developer Guide pages for changed workflows. Use repository targets for formatting, sample generation, and comparisons when needed; do not run the unsafe comparison path before E2-08 is addressed or isolated. Keep temporary PDFs, coverage outputs, and built docs outside tracked output paths unless explicitly part of the change.
6. **Preserve contribution and release ownership.** Keep contributions incremental. Humans create GitHub issues and pull requests under repository policy, and maintainers authorize release actions. A proposed action in this document does not authorize publication, tags, package upload, or release metadata changes.
7. **Record evidence and limitations.** Record focused/broader checks, environment, compatibility decisions, unresolved cases, and measurements where relevant. For architecture changes, update a concise invariant/ownership guide so the design is maintainable beyond its original author.

Contributor sources of truth: [Developer introduction][dev-intro], [change requirements][dev-changes], [documentation workflow][dev-doc], [testing guide][dev-test], [release process][dev-release], and the repository [Makefile][makefile], as listed in `mkdocs.yml`.

[review]: 2026-10-10-PyPDFForm-Code-Quality-Stability-Roadmap-and-Architecture-Review.md
[dev-intro]: ../docs/dev_intro.md
[dev-changes]: ../docs/dev_changes.md
[dev-doc]: ../docs/dev_doc.md
[dev-test]: ../docs/dev_test.md
[dev-release]: ../docs/dev_release.md
[makefile]: ../Makefile
