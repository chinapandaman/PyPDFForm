# PyPDFForm Test Suite Restructure Plan

**Date:** November 26, 2026, America/Chicago

**Tracking issue:** [PPF-2145](https://github.com/chinapandaman/PyPDFForm/issues/2145)

**Evidence baseline:** Commit `7716d1ae8945767b7065fd53d323b3dffdc554bf`, package version `6.3.0`

**Deliverable:** Four phases, one pull request each. Completed phases record their implementation and validation below.

The issue holds the full design: the target layout, where each of today's tests goes, and the `expect_pdf` fixture. This file tracks the phases, the maintainer's decisions, and the evidence for each phase. The issue body and its acceptance criteria stay as filed. Progress after each merged pull request goes in a "Progress after #N" comment on the issue.

## How to use this file

Each phase's pull request updates that phase's entry in the style of the [action plan](2026-10-10-PyPDFForm-Action-Plan-by-Effort-Level.md). It sets **Completed**, **Confirmed policy and scope**, **Validation**, and **Remaining limitations**, and adds one bullet per maintainer review round. Confirm the decisions a phase needs, one at a time, before it starts, and record the outcome in the decision table.

No phase removes a test or regenerates an expected PDF. Each phase keeps every expected PDF byte for byte and keeps 100% statement coverage.

## Baseline

Measured at the baseline commit on macOS arm64 with 10 cores, `./venv` with Python 3.14.10, and standard zlib:

- 46 test modules, 18,657 lines, 593 test functions, and 1,151 collected tests. `tests/test_functional.py` (4,452 lines, 303 tests) and `tests/test_widget_attr_trigger.py` (3,898 lines, 476 tests) held 45% of the lines and 68% of the tests.
- 263 test functions compared output with an expected PDF in three ways: inline `len` and `==` checks, `assert_same_pdf`, and `skip_regenerate` with a length check. Each recorded its output for regeneration by hand in `request.config.results`. 18 library tests and 19 doc example tests also made semantic assertions on the output they compared.
- 63 helper functions were defined in test modules. `tests/test_generate_appearance_streams.py` imported a helper from `tests/test_need_appearances.py`. `tests/conftest.py` had 729 lines and 38 fixtures.
- `pdf_samples` held 258 tracked files (106 MB): about 193 expected PDFs, 64 inputs, and `fixture_environment.json`. Inputs and expected PDFs shared directories.
- The suite took 57 s serially. In `master` Tests run [45866630502](https://github.com/chinapandaman/PyPDFForm/actions/runs/45866630502), the pytest step took 109–353 s per job across 15 jobs. `make compare-pdf-diffs` and `make generate-new-pdf-samples` ran 1,025 non-CLI tests to write 188 PDFs. No two tests had identical bodies.

## Decisions

| # | Decision | Recommendation | Status | Needed by |
| --- | --- | --- | --- | --- |
| 1 | Parallel runs | Add pytest-xdist as a dev dependency, use `-n auto` in the make targets and CI, and keep plain `pytest` serial | Confirmed November 26, 2026 ("Looks good, let's start with phase 1") | Phase 1 |
| 2 | Snapshot purity | Library snapshot tests contain only the comparison, and the 18 mixed library tests are split. Doc example and scenario tests can still mix. | To confirm | Phase 3 |
| 3 | Directory names | `behavior/`, `snapshots/`, `cli/`, `support/`, `behavior/field_tree/` | To confirm | Phase 3 |
| 4 | Sample layout | Expected PDFs named after their test IDs under `pdf_samples/expected/`, and inputs under `pdf_samples/input/` | To confirm | Phase 4 |
| 5 | Languages | Move `tests/multi_language/` to `tests/scenario/test_languages.py` | To confirm | Phase 3 |
| 6 | New test files | Follow the placement rule, and consult the maintainer before creating a new directory | To confirm | Phase 3 |
| 7 | Delivery | One pull request per phase under PPF-2145, not a feature branch | Followed for Phase 1 ([#2146](https://github.com/chinapandaman/PyPDFForm/pull/2146)), not confirmed explicitly | All phases |
| 8 | Release timing | Release soon after Phase 4, since `nightly-tests` fails until then | To confirm | Phase 4 |

## Phases

### P1 — Parallel runs

- [x] **Work:** Add `pytest-xdist` to the `dev` extra. Measure each worker with coverage and combine the data before the report. Run with `-n auto` in `scripts/test.sh`, `scripts/coverage.sh`, `scripts/new_pdf_samples.sh`, `scripts/pdf_diffs.sh`, the Tests workflow, and the nightly lowest-dependency job. Only the controller writes `pdf_samples/fixture_environment.json`. Plain `pytest` stays serial. CI prints `--durations=20`.
- **Done when:** Every Tests job passes with the coverage gate, and the pull request records each job's pytest step time before and after. A deliberately uncovered line still fails the gate under `-n auto`. A parallel `--regenerate-dir` run writes the same PDFs byte for byte, and in-place regeneration writes the environment record once. `docs/dev_test.md` documents parallel runs.
- **Basis and dependencies:** Decision 1. Independent of the other phases.
- **Baseline:** Reconfirmed at `7716d1ae`. The suite took 57 s serially with or without coverage. With pytest-xdist 3.8.0 in a scratch environment and no test changes, it took 30 s with `-n 2`, 18 s with `-n 4`, and 16.5 s with `-n auto` (10 workers). `-n 4` under coverage with `patch = ["subprocess"]` and `coverage combine` reached 100% of 3,826 statements. A run of only `tests/test_dropdown.py` failed the gate at 50%. In throwaway worktrees with a plugin that logs each write of the environment record, in-place regeneration with `-n 3` on `master` had `gw0`, `gw1`, and `gw2` each write it.
- **Completed:** November 26, 2026, in [#2146](https://github.com/chinapandaman/PyPDFForm/pull/2146). `pyproject.toml` adds `pytest-xdist>=3.8.0,<4.0.0` and sets `patch = ["subprocess"]` under `[tool.coverage.run]`. That option implies `parallel` and relies on the `a1_coverage.pth` file installed with coverage, so nothing is written to site-packages at run time. `scripts/test.sh` and `scripts/coverage.sh` run `coverage erase`, then `coverage run -m pytest -n auto`, then `coverage combine` before `xml`, `report`, or `html`. The regeneration and comparison scripts add `-n auto`. The Tests workflow and the nightly lowest-dependency job run `coverage run -m pytest -n auto --durations=20 && coverage combine && coverage report --fail-under=100`. In `tests/conftest.py`, `pytest_sessionfinish` on a worker stores whether it regenerated in `config.workeroutput` and returns. On the controller, the new `pytest_testnodedown` hook, marked `optionalhook` so pytest also runs without pytest-xdist, sets the stash flag. The controller then writes the record once. `.gitignore` adds `.coverage.*`. `docs/dev_test.md` updates both coverage commands and explains parallel runs.
- **Confirmed policy and scope:** Maintainer-confirmed: pytest-xdist is a dev dependency, `-n auto` is used in the make targets and CI, and plain `pytest` stays serial for single tests and debuggers such as `pudb` and `--pdb`. No pytest-cov. The `nightly-tests` job is unchanged, because it runs the latest tag's tests in an image built from that tag, which has no pytest-xdist until the next release. The slowest test is not changed in this phase.
- **Validation:** `make check-zlib` reported standard zlib. `make test-all` passed all 1,151 tests with 100% of 3,826 statements in 17 s with 10 workers. With an uncovered function temporarily appended to `PyPDFForm/lib/utils.py`, `make test-all` reported 99%, printed `Coverage failure`, and exited 2; the file was restored. `pytest -n auto -m 'not cli_test' --regenerate=1 --regenerate-dir=<scratch>` wrote 188 files, each identical byte for byte to the tracked file. With the logging plugin in throwaway worktrees, in-place regeneration on this branch wrote the record once, from the controller, with `-n 3`, and once with a serial run. A parallel run without `--regenerate` didn't write it, and no tracked file changed. A scratch Python 3.11 environment with `--resolution=lowest-direct` (coverage 7.14.1, pytest 9.0.3, pytest-xdist 3.8.0, pypdf 6.19.0, pikepdf 10.7.2) ran the nightly command from the checkout without `PYTHONPATH`. It passed all 1,151 tests with 100% of 3,849 statements in 45 s. `make linting`, `git diff --check -- . ':(exclude)*.pdf'`, and `mkdocs build --strict` passed. In [run 45884141397](https://github.com/chinapandaman/PyPDFForm/actions/runs/45884141397), all 15 Tests jobs passed with the gate. Ubuntu and Windows jobs started 4 workers and macOS jobs 3. The pytest steps took 1,453 s in total, compared with 3,206 s before (2.2 times faster), and the slowest job took 176 s instead of 353 s. The workflow took 3 min 19 s from start to finish, compared with 10 min 20 s. #2146 has the per-job table.
- **Remaining limitations:** Each timing comes from a single CI run. `test_bulk_create_fields_stress_max` sets the minimum time for the slower jobs: it took 68 s on Ubuntu with Python 3.12, which uses coverage's slower tracer, and 35 s locally on Python 3.11. Ubuntu with 3.12 and 3.13 improved only 1.2 and 1.3 times. Starting slow tests first, or making bulk field creation faster, could help but isn't planned here. If a worker crashes after regenerating, the record isn't updated for that run. The warnings summary repeats anyio's existing `PytestRemovedIn10Warning` once per process. The development container wasn't run; it gets pytest-xdist when rebuilt. `nightly-tests` stays serial.

### P2 — `expect_pdf` and the `snapshot` marker

- [ ] **Work:** Create `tests/support/` and move the shared assertions' implementations there from `tests/conftest.py`. Convert all expected-PDF tests to `expect_pdf`, keeping their current paths, and remove `request.config.results` and `skip_regenerate` from test modules. Register the `snapshot` marker and apply it to every test that requests the fixture. `make generate-new-pdf-samples` and `make compare-pdf-diffs` select `-m "snapshot and not cli_test"`.
- **Done when:** `pytest -m snapshot --collect-only` lists exactly the tests that compare with an expected PDF. A `--regenerate-dir` run writes the same set of files as before, byte for byte, and the diff contains no PDF. No test module refers to `request.config.results`.
- **Basis and dependencies:** Requires P1 for the parallel regeneration it selects from. The fixture compares the way `assert_same_pdf` does: decoded objects on every platform, plus length and bytes with standard zlib. On the zlib-ng Windows jobs, tests that compare bytes inline today would compare decoded objects instead. `same_as=` keeps the CLI doc examples comparing with the library's expected PDFs without regenerating them.

### P3 — Layout and module splits

- [ ] **Work:** Add `__init__.py` packages and move tests according to the issue's mapping, without changing test bodies except for helper imports. Split each of the 18 mixed library tests into a snapshot test and a behavior test. Move every helper function into `tests/support/`, so no test module imports another.
- **Done when:** The pull request lists every old test ID with its new one, and the new count is 1,151 plus the cases of the split-off tests. Coverage stays at 100%, and no test module is longer than about 800 lines. Test modules define only tests and parametrize tables. `docs/dev_test.md` has the placement rule and examples using `expect_pdf`.
- **Basis and dependencies:** Requires P2. Needs decisions 2, 3, 5, and 6. After this phase, the sdist no longer contains test files, so the sdist sentence in `docs/dev_release.md` and the docstring of `scripts/check_dist.py` need rewording.

### P4 — `pdf_samples` layout

- [ ] **Work:** Move inputs to `pdf_samples/input/`, keeping their relative paths. Move expected PDFs to the paths `expect_pdf` derives from test IDs under `pdf_samples/expected/`. Keep explicit paths only for `same_as=` and `docs/pdfs/sample_filled.pdf`. Add an ownership check to full runs: every file under `pdf_samples/expected/` belongs to exactly one test, and every snapshot test's file exists.
- **Done when:** `git diff -M --stat` shows only renames with no content changes. The full suite passes, and a `--regenerate-dir` run produces no differences. The ownership check passes.
- **Basis and dependencies:** Requires P3. Needs decisions 4 and 8. `nightly-tests` runs the latest tag's tests against `master`'s `pdf_samples`, so it fails from this merge until the next release. It failed the same way from November 22 to 25, 2026, when expected PDFs on `master` had changed ahead of the 6.3.0 release.

## Validation rules

- Run `make check-zlib` before using a runner. Use `./venv` with standard zlib, and the development container with zlib-ng.
- In every phase, run `make test-all` and `make linting`, keep 100% statement coverage, and run `git diff --check -- . ':(exclude)*.pdf'`.
- Show that the expected PDFs are unchanged: a `--regenerate-dir` run with no differences, and for P4, only renames.
- Record the collected test count and the timings before and after.
