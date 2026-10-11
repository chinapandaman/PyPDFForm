# PyPDFForm Code Quality, Stability, Roadmap, and Architecture Review

**Review date:** October 10, 2026, America/Chicago  
**Project:** [chinapandaman/PyPDFForm](https://github.com/chinapandaman/PyPDFForm)  
**Reviewed commit:** `0b5cc1dc8604b36693864852d76ed7e60f903451`  
**Local branch/tag/version:** `master`, `v6.0.0`, package version `6.0.0`  
**Deliverable:** Evaluation only. No production code, tests, workflows, releases, or version metadata were intentionally changed.

**Navigation:** [Executive evaluation](#1-executive-evaluation) · [Verification](#2-scope-evidence-and-verification) · [Architecture](#3-architecture-assessment) · [Findings](#4-prioritized-findings) · [Quality](#5-additional-quality-and-stability-observations) · [Performance](#6-performance-memory-and-scaling) · [Roadmap](#7-roadmap-and-maintenance-evaluation) · [Test contracts](#8-proposed-test-contracts) · [Reproductions](#9-reproduction-appendix)

## 1. Executive evaluation

PyPDFForm has a useful public API, substantial documentation, an actively maintained regression suite, and broad CI configuration. Its main weakness is **semantic PDF correctness across operations**, particularly where it copies annotations, reconstructs form fields, and reconciles cached Python objects with the PDF object graph.

The most consequential findings are reproducible:

1. **Extracting one page can retain content from excluded pages.** A two-page synthetic form produced a one-page output that still contained the second page's text in a decoded PDF stream. The copied annotation pointed to a different page object whose parent still described the original two-page tree.
2. **A failing write can destroy the destination, including the input PDF used by the CLI.** An ordinary field styling update on a form using an inherited default appearance raised `KeyError('/DA')` after the file had already been truncated to zero bytes.
3. **Filling one signature can remove other signature fields and unrelated annotations.** The implementation removes all page annotations and selectively restores a subset.
4. **Default filling writes a text string into the annotation's appearance-dictionary slot.** This relies on viewer recovery instead of producing a valid appearance structure.
5. **Form-field catalog maintenance can both drop legitimate fields and retain supposedly removed data.** Reading a form dropped a catalog-only field; removing every visible field left the old fields and values accessible through `PdfReader.get_fields()`.

These are significant stability and data-integrity issues. They justify a maintenance release focused on preservation and correctness before further feature expansion. Page extraction and in-place CLI writes deserve the first attention.

The project does **not** need a wholesale rewrite. It needs stronger ownership of the PDF object graph, explicit mutation and validation rules, transactional output, and tests that verify what the resulting PDF means. Existing modules and public entry points can support that work incrementally.

### Overall assessment

| Area | Evaluation | Main reason |
| --- | --- | --- |
| Public API and usability | Useful and approachable, with important inconsistencies | Straightforward wrapper and CLI; silent ignored inputs and side effects complicate composition |
| Code organization | Reasonable module boundaries; weak state boundaries | Logical modules exist, but bytes, middleware objects, hooks, and catalogs can disagree |
| Stability on established fixtures | Strong | All 381 collected tests passed locally |
| Stability on heterogeneous PDFs | Material risk | Several ordinary PDF structures and operation combinations fail independent probes |
| Test quality | Broad execution coverage; insufficient semantic checks | 100% statements did not detect the major defects reproduced here |
| Documentation | Extensive and buildable | Good examples and explicit rendering limitations; current migration and support guidance need work |
| Release engineering | Functional, with missing safeguards | Builds succeed, but publishing does not visibly require validation of the final release commit/artifact |
| Roadmap | Needs a preservation-first phase | Recent work shows maintenance and API evolution; no current consolidated roadmap was found in the tracked tree |
| Production suitability | Conditional on the workflow and validated templates | Do not infer arbitrary-PDF correctness from fixture coverage or the Production/Stable classifier |

No universal emergency/P0 finding is assigned. P1 findings below are urgent because they can disclose excluded content, destroy files, lose form structure, or produce inconsistent form data under concrete conditions.

## 2. Scope, evidence, and verification

### 2.1 Sources and version boundary

The review used the local checkout as the authoritative code snapshot. The working tree was clean at the start. Before producing this report, the repository's `AGENTS.md`, `mkdocs.yml`, `Makefile`, and all five Developer Guide pages were read: introduction, change requirements, documentation, testing, and release process.

Inspection covered the public wrapper, PDF utilities, widget discovery and middleware, fill and style hooks, creation and drawing, annotation handling, font/image management, CLI validation, packaging, test fixtures, developer scripts, CI workflows, release history, security policy, and relevant user documentation.

The public GitHub pages were also consulted. The fetched [releases page](https://github.com/chinapandaman/PyPDFForm/releases) showed 5.6.0, while the local checkout already contained the 6.0.0 tag and version bump. The direct 6.0.0 release-page fetch failed. Public pages can be cached: **this review does not assert that 6.0.0 was unpublished**, nor that the local checkout exactly matched remote HEAD at every point during review. Findings are anchored to the commit above.

The issue pages available during review showed reports about randomized merged field names and Thai font rendering. Those are useful roadmap signals, not proof that every historical symptom remains present in 6.0.0. [Issue #2036](https://github.com/chinapandaman/PyPDFForm/issues/2036), [issue #1153](https://github.com/chinapandaman/PyPDFForm/issues/1153).

### 2.2 Execution environment

`make check-zlib` reported:

~~~json
{
  "python_executable": "/Users/benli/Documents/PyPDFForm/venv/bin/python",
  "zlib_backend": "zlib",
  "zlib_compile_time_version": "1.2.12",
  "zlib_runtime_version": "1.2.12"
}
~~~

The repository-approved local virtual environment was therefore used. A preliminary Docker availability query could not access the Docker socket; a container was not required by the zlib result.

| Component | Observed version |
| --- | --- |
| Python | 3.14.8 |
| pypdf | 6.20.0 |
| pikepdf | 10.16.0 |
| ReportLab | 5.0.1 |
| fonttools | 4.66.1 |
| Pillow | 12.3.0 |
| cryptography | 50.0.2 |
| pytest | 9.1.1 |
| coverage.py | 7.16.2 |
| Typer | 0.27.3 |
| jsonschema | 4.26.0 |
| PyYAML | 6.0.3 |

These dependency versions satisfy the corresponding declared ranges. Results establish behavior for this environment; the complete operating-system/Python/dependency matrix was not rerun locally.

### 2.3 Checks performed

| Check | Result | Interpretation |
| --- | --- | --- |
| `make check-zlib` | Standard zlib | Local runner permitted |
| Focused pytest run: CLI errors, dropdowns, full names, functional tests | 90 passed in 6.50 seconds | Established baseline before targeted probes |
| `make test-all` | 381 passed in 31.93 seconds | Entire existing suite passed |
| Standard coverage gate | 2,514/2,514 statements; 100% | Project's configured gate passed |
| Supplemental branch-instrumented suite | 381 passed in 30.71 seconds | Examined a gap not measured by the standard gate |
| Branch coverage | 612/648 branches; 94.44%; 36 missing branches | Combined line/branch figure is 98.86%, rounded to 99% |
| `make linting` | Pylint 10.00/10; Pyright zero errors/warnings; Ruff passed; doc-example checker completed | Log inspected directly because the shell target can mask earlier failures |
| `mkdocs build --strict` with output in `/tmp` | Passed | Documentation builds successfully |
| `uv build` | Source distribution and wheel built successfully | Initial environment/network impediments were resolved |
| Built-wheel smoke test outside the repository | Import, create/fill/read, CLI version passed | Imported from the wheel itself, not the checkout |
| Independent PDF object probes | Multiple failures reproduced | See findings and appendix |
| Poppler rendering of default vs generated appearances | Both rendered, with visibly different text sizing | Does not establish compatibility with all viewers |
| Page-extraction microbenchmark | Approximately quadratic growth in the measured range | Supports architectural concerns; not a production capacity benchmark |
| Mocked lint failure propagation | Script returned zero after mocked Pylint failure | Confirms the local lint gate defect |
| Git status checks | No tracked implementation changes | Report is the requested new repository artifact |

Coverage data, logs, PDFs, renderings, distributions, and probe scripts were directed to `/tmp/pypdfform-review-2026-10-10` where practical. The standard coverage target used an equivalent temporary configuration to redirect its data and XML output. This report includes the essential evidence and reproduction instructions; it does not require those temporary files to remain available.

Pylint could not write its normal cache under the sandbox, but completed analysis. MkDocs emitted an upstream theme notice about future MkDocs changes; the strict build itself succeeded. An initial non-isolated build lacked setuptools in the existing virtual environment; a standard isolated build subsequently fetched the **already declared** build dependency and succeeded. None of those environment details is counted as a project defect.

### 2.4 Scale and useful existing strengths

The source inventory contained 59 Python modules and 10,497 physical lines, including extensive docstrings. Coverage counted 2,514 executable statements. There were 46 test modules, 380 statically identified test functions, and 381 collected test cases. The sample directory contained 253 files and occupied about 108 MB.

Strengths worth preserving:

- A compact public entry point through `PdfWrapper`, with explicit field, raw-element, and annotation definitions.
- Shared library implementation beneath the CLI, rather than separate PDF-manipulation code for each interface.
- Executable documentation examples for both library and CLI use.
- CLI JSON Schema validation, safe YAML loading, useful path checks, and tests for invalid inputs.
- Tests for real-world PDF scenarios, custom fonts, multiple languages, appearance modes, metadata, and field styles.
- A configured CI matrix spanning three operating systems and five Python versions.
- A nightly minimum-direct-dependency compatibility job and tests against the installed published library.
- Bounded caches and defensive deep copying of cached widget prototypes; earlier unbounded/shared-mutation problems should not be presumed present.
- Dependency maintenance automation, an explicit security-reporting policy, and restricted permissions on several workflows.
- A publish workflow with OIDC permissions rather than a plainly embedded package credential.
- Documentation that already acknowledges important appearance-generation limitations.

### 2.5 Limits

This was a detailed code and behavior review, not an exhaustive fuzzing campaign or vulnerability certification. Acrobat, browser PDF.js, Preview, and PDFium were not all exercised interactively. Encrypted PDFs, pre-existing cryptographic signatures, accessibility/tagging, PDF/A, malformed-object stress cases, and very large documents were not comprehensively validated.

Repository settings such as branch protection, required checks, deployment environments, and private security advisories were not available. Accordingly, release findings describe what is enforced by tracked workflows, not undisclosed repository settings. Milestone/project pages could not be reliably fetched; absence of a public planning artifact is not proof that the maintainer has no private plan.

## 3. Architecture assessment

### 3.1 Current processing model

~~~mermaid
flowchart TD
    A[Python API and Typer CLI] --> B[PdfWrapper]
    B --> C[Stored PDF bytes]
    B --> D[Mutable middleware widgets]
    D --> E[Deferred attribute hooks]
    E --> C
    C --> F[pypdf parsing and rewriting]
    B --> G[Field and raw-element definitions]
    G --> H[ReportLab watermark PDFs]
    H --> I[Page and annotation cloning]
    I --> C
    C --> J[Output processing]
    J --> K[Optional pikepdf appearance generation]
    J --> L[Rebuild AcroForm Fields]
    K --> M[Serialized bytes]
    L --> M
~~~

The dependency choices are defensible. pypdf provides object manipulation, ReportLab generates new drawing content and fields, and pikepdf exposes qpdf appearance generation. Their coexistence is not inherently a flaw.

The problem is that several representations simultaneously behave as authoritative:

- `PdfWrapper._stream` stores serialized PDF state.
- `PdfWrapper.widgets` stores mutable extracted state.
- `hooks_to_trigger` records deferred edits.
- `attr_set_tracker` preserves selected Python-side attributes across rebuilds.
- `_font_register_events` replays resource registration after rewrites.
- Final `read()` processing reconstructs the catalog using the current widget dictionary.

Those representations have different lifetimes and update rules. A successful operation can leave cached properties stale; a read can apply pending mutation; a catalog rewrite can discard information never represented in middleware.

### 3.2 Main architectural weaknesses

**The catalog is reconstructed from an incomplete view.** Widget discovery starts from recognized page annotations, but PDF form fields need not all have visible widgets. Treating the discovery dictionary as the entire document's field set is the cause of R05 and contributes to R06.

**Annotation cloning does not consistently establish destination ownership.** Copying a widget can copy its `/P`, `/Parent`, and related object graph. These references must be deliberately remapped; ordinary cloning is not equivalent to transferring just the intended field. R01 is a concrete consequence.

**Serialization is used as an internal state transition.** Many small operations parse and rewrite the complete document. This simplifies individual helpers but makes resource preservation, performance, exception safety, and cache invalidation harder.

**The public wrapper has orchestration responsibilities across every subsystem.** At 976 physical lines it is not enormous in executable terms—250 covered statements—but changes to egress, fonts, creation, or cloning can affect unrelated methods. Splitting files alone would not repair this coupling.

**Field identity is predominantly a string.** Short names can collide, full names are only partially supported, radio options are aggregated specially, and repeated non-radio widgets collapse into one dictionary entry. A field's PDF identity and its presentation on pages need separate representation.

**Backend internals appear throughout domain code.** Private pypdf methods/root access and ReportLab internals are used in multiple modules. These may be necessary, but an explicit backend boundary would make compatibility changes easier to contain.

### 3.3 Recommended direction

Keep the public wrapper, but progressively introduce:

1. A document-owned field graph that retains root fields, children, widget appearances, and page references, including unrecognized fields.
2. Explicit operations for moving/cloning fields and annotations, with ownership checks and destination-page remapping.
3. A shared validation layer for library and CLI operations.
4. Mutation transactions: validate, stage, update all representations, serialize, then publish the new state.
5. A backend adapter for pypdf/ReportLab/pikepdf details.
6. A preservation contract specifying which document-level structures each operation retains or deliberately excludes.
7. Operation-level dirty state so unchanged reads need not repeatedly reconstruct the document.

Adopt these behind existing entry points. Repair the concrete data-loss defects first; use the new invariants to guide the refactor.

## 4. Prioritized findings

Severity definitions: **P1** = urgent correctness/data-loss/disclosure risk in a concrete supported workflow; **P2** = important functional, maintainability, or assurance problem that should be scheduled; **P3** = lower-impact improvement. Runtime confirmation means the described probe was executed. Static confirmation means the behavior follows directly from inspected code; it does not imply an observed production incident.

| ID | Priority | Finding | Evidence |
| --- | --- | --- | --- |
| R01 | P1 | Extracted PDFs retain content from excluded pages | Runtime and object-reference inspection |
| R02 | P1 | Failed writes truncate existing files | Library and CLI runtime reproductions |
| R03 | P1 | Image/signature fill removes unrelated annotations and unfilled signatures | Runtime |
| R04 | P1 | Default filling produces an invalid appearance entry | Runtime structure inspection and PDF reference |
| R05 | P1 | Reading/serializing can drop legitimate catalog-only fields | Runtime |
| R06 | P1 | Removing every field leaves catalog fields and values behind | Runtime |
| R07 | P1 | Dropdown option representations corrupt selected values | Runtime |
| R08 | P2 | Radio reselection leaves multiple active appearances | Runtime |
| R09 | P2 | Full-name mode prevents even collision-free merges | Runtime |
| R10 | P2 | Validation and cached state disagree with actual PDF behavior | Multiple runtime probes |
| R11 | P2 | Internal links use numeric destinations instead of page references | Runtime structure inspection and PDF reference |
| R12 | P2 | Font handling makes invalid resource assumptions and leaks temporary registrations | Runtime |
| R13 | P2 | Quality and release safeguards have concrete gaps | Static review and mocked failure probe |

### R01 — Extracted PDFs retain content from excluded pages

**Location:** [wrapper.py:274][wrapper-pages-cache], [wrapper.py:429][wrapper-pages], [watermark.py:342][watermark-clone].

**Trigger:** Extract a page containing a form widget from a multipage PDF.

**Observed:** A synthetic two-page PDF contained a text field on page 1 and the text `EXCLUDED_SECRET_SECOND_PAGE` on page 2. After `PdfWrapper(source).pages[0].read()`:

- The visible page tree contained exactly one page.
- A decoded stream still contained the excluded page's marker.
- The output's visible page was object `(3, 0)`.
- The copied widget's `/P` referenced object `(8, 0)`.
- That other page's `/Parent /Count` was still 2.
- The 4,099-byte source became a 4,296-byte one-page output.

**Cause:** Page extraction first removes annotations and splits pages, then clones annotations from the original document. `annot.clone(writer)` follows references beyond the intended annotation. The widget's source-page relationship is not remapped to the actual output page.

**Impact:** A user can distribute what appears to be a selected-page PDF while including content from pages they meant to exclude. This is a concrete information-disclosure condition, not just excess file size. Page-count assertions and ordinary rendering do not detect it.

**Recommended fix:** Construct the destination page/field graph deliberately. Remap widget `/P` references, retain only relevant widget children, and avoid cloning an excluded source page tree through backreferences. Removing unreachable objects is useful only after correcting references; objects reachable through a retained annotation may survive ordinary cleanup.

**Acceptance criteria:** Extracting a page from a document with unique text, images, and form values on excluded pages must not retain those excluded objects or decoded payloads. Check output page count, every retained widget's page ownership, field hierarchy, and all serialized streams. Include shared fields spanning selected and excluded pages and internal links to excluded pages.

**Scope note:** Extraction is not a redaction API. Nevertheless, importing whole excluded page content through an unintended annotation reference violates the basic expectation that an extracted document contains the selected pages.

### R02 — Failed writes truncate existing files

**Location:** [wrapper.py:569][wrapper-write], [hooks.py:184][hooks-font-size], [cli/update.py:281][cli-update].

`write()` opens a path using `wb+` and only then calls `self.read()`. Opening the file truncates it before serialization and deferred hooks have succeeded.

**Observed:** A text field using document-level `/AcroForm /DA` was loaded, its font size was changed, and it was written back to its original path. The font-size hook only looked on the widget or immediate parent, raised `KeyError('/DA')`, and left the original **624,427-byte PDF at zero bytes**. The equivalent CLI command also exited with code 1 and left a zero-byte input:

~~~shell
pypdfform update field inherited-da.pdf --field test --font_size 14
~~~

The test used a temporary copy, never a repository fixture.

**Impact:** Many CLI commands overwrite the input by default. Thus an unsupported PDF structure, invalid deferred style, or output-stage failure can destroy a user's only file.

**Recommended fix:** Finish validation and serialization before touching the destination. For path outputs, write a sibling temporary file, close it successfully, and replace the destination atomically. Handle cleanup and preservation of relevant file permissions. Document that arbitrary caller-owned streams cannot provide the same rollback guarantee.

The inherited-`/DA` error should also be fixed, but addressing that one trigger alone does not make writes safe.

**Acceptance criteria:** For a pre-existing destination, simulated hook failure, appearance-generation failure, and write failure must preserve the old bytes. Test the default CLI overwrite path and distinct output paths. A successful replacement must produce a readable PDF.

### R03 — Filling an image/signature removes unrelated annotations and unfilled signatures

**Location:** [wrapper.py:650][wrapper-fill], [utils.py:32][utils-remove], [watermark.py:342][watermark-clone].

When any image needs drawing, the fill path clears page annotations and copies back only names in a computed list. That list excludes every middleware `Signature`; `Image` inherits from `Signature`. Separately, `remove_all_widgets()` clears the entire annotation array, although its name describes only widgets.

**Observed:**

- A PDF with signature fields `first` and `second` was filled only for `first`. Reopening the result exposed **neither** signature field.
- A PDF containing a signature, a text field, and a text-note annotation went from annotation subtypes `[/Widget, /Widget, /Text]` to `[/Widget]` after filling the signature.
- The original wrapper still reported the removed signature keys, adding a cached-state inconsistency.

**Impact:** Multi-signer workflows lose later signing locations. Notes and, by the same filtering mechanism, other unrelated annotation types can disappear during a routine form-fill operation.

**Additional static concern:** The copy filter resolves short keys unconditionally. Passing fully qualified keys from a wrapper using full-name mode can therefore fail to restore otherwise unrelated fields during this path.

**Recommended fix:** Remove or flatten only the specific image/signature widgets actually consumed by the operation. Preserve other annotations by identity and subtype. Use a consistent identity scheme for full-name mode. Refresh or accurately invalidate affected middleware after mutation.

**Acceptance criteria:** Filling one of two signatures must retain the second. Preserve comments, links, highlights, unfilled image fields, and unrelated full-name fields. Verify both the page annotation graph and the reopened public API.

### R04 — Default filling writes a string into the appearance-dictionary entry

**Location:** [patterns.py:304][patterns-dropdown], [patterns.py:360][patterns-text], [egress.py:32][egress-appearance].

With the default `need_appearances=False`, text and dropdown updates assign `TextStringObject(value)` to `/AP`. An annotation's `/AP` is an appearance dictionary, whose entries refer to streams or appearance-state dictionaries. [Adobe PDF Reference, appearance dictionaries](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.6.pdf).

**Observed:** Filling the repository's standard sample with `REVIEW_VISIBLE_TEXT` produced `/AP` of type `TextStringObject`. With explicit appearance generation it was a `DictionaryObject`. Poppler rendered both outputs, but the text sizes visibly differed.

**Impact:** Successful display in a forgiving viewer does not establish a portable PDF. Appearance, printing, field focus, and form editing may vary by viewer. The malformed structure is confirmed; a universal blank-field failure is not claimed.

**Recommended fix:** Choose and document a coherent default: generate a valid appearance, or request viewer regeneration using valid PDF structure. Never substitute the value string for the appearance dictionary. Preserve compatible existing appearances when appropriate and invalidate them explicitly when necessary.

Enabling the current generator everywhere is not a complete answer: the project's own documentation identifies ASCII, multiline, and alignment limitations. pikepdf also describes the generator as subject to qpdf's capabilities. [pikepdf appearance generation](https://pikepdf.readthedocs.io/en/latest/api/main.html#pikepdf.Pdf.generate_appearance_streams).

**Acceptance criteria:** Assert PDF object types and appearance references, then render representative forms in at least two independent engines. Include printing behavior, Unicode, custom fonts, alignment, multiline text, and pre-existing appearances. Unsupported generation should be explicit rather than silently producing misleading output.

### R05 — Ordinary serialization can drop catalog-only form fields

**Location:** [template.py:380][template-discovery], [egress.py:81][egress-fields], [wrapper.py:490][wrapper-read].

`rebuild_acroform_fields()` replaces `/AcroForm /Fields` using only recognized page annotations whose names appear in the middleware map. Legitimate fields can exist without a widget annotation. This distinction is explicitly described by pypdf's form documentation. [pypdf form-field structure](https://pypdf.readthedocs.io/en/stable/user/forms.html).

**Observed:** A catalog-only text field named `hidden_business_id`, with value `12345`, was added alongside the sample's visible fields. It appeared in `PdfReader.get_fields()` before `PdfWrapper(source).read()` and disappeared from the returned PDF's field catalog afterward.

**Impact:** Document identifiers, hidden workflow fields, or other non-visible form data can be removed even without an explicit remove operation. A read-like serialization method becomes a destructive normalization step.

**Recommended fix:** Preserve the original catalog graph and update only the parts intentionally changed. If a repair function is needed for broken inputs, expose it as an explicit operation or make its behavior conservative. Unknown or unsupported fields should be preserved unless the caller requests removal.

**Acceptance criteria:** A no-op load/serialize cycle preserves catalog-only fields, unsupported widget types, form resources, calculation-order references, and valid parent/child relationships. Repairing a malformed catalog must not redefine the supported subset as the whole document.

### R06 — Removing every field leaves form values in the catalog

**Location:** [template.py:543][template-remove], [egress.py:81][egress-fields], [wrapper.py:833][wrapper-remove].

Removal edits page `/Annots`, but does not itself remove the corresponding catalog fields. The later catalog rebuild immediately returns when the widget-key set is empty.

**Observed:** After filling `test` with `REVIEW_SENTINEL` and calling `remove_fields(list(pdf.widgets))`:

- `pdf.widgets` was empty.
- All page annotation arrays were empty.
- `PdfReader(BytesIO(pdf.read())).get_fields()` still returned all six original field names.
- `test /V` still contained `REVIEW_SENTINEL`.

**Impact:** The public API says the fields are gone, but other consumers can still enumerate them and read their values. Users may also make incorrect privacy assumptions based on the empty widget map.

**Recommended fix:** Update field roots and parent `/Kids` references as part of removal, including the last-field case. Handle dependent structures such as calculation-order entries. Define separately whether removal promises elimination of unreachable serialized objects; do not imply that field deletion is a general redaction facility.

**Acceptance criteria:** Remove one field, one child of a hierarchy, a radio group, and all fields. Independently inspect page annotations and the catalog. Previously removed field values must not remain accessible as active form fields.

### R07 — Dropdown option representations corrupt selected values

**Location:** [middleware/dropdown.py:75][middleware-dropdown], [patterns.py:304][patterns-dropdown], [patterns.py:336][patterns-dropdown-read], [patterns.py:431][patterns-options], [hooks.py:341][hooks-options].

There are incompatible representations across the workflow:

- Extracted choices retain only display strings.
- Public choice updates accept display/export pairs.
- Filling blindly converts the selected choice object to `TextStringObject`.
- Reading treats selected index zero as `None`.

**Observed:** Starting with a simple dropdown, assigning:

~~~python
pdf.widgets["choice"].choices = [("Pear", "P"), ("Grape", "G")]
pdf.fill({"choice": 1})
~~~

produced:

~~~text
/Opt = [["P", "Pear"], ["G", "Grape"]]
/V   = "('Grape', 'G')"
~~~

Reopening the PDF reported `{"choice": None}`. The stringified Python tuple is neither the display label nor the export value. This is an unequivocal defect independent of viewer-specific interpretation of choice values.

Other probes found:

- Creating options `[("Apple", "A"), ("Banana", "B")]` and selecting index 1 wrote `"Banana"`.
- An input carrying `/V = "B"` was read as `None`, because extraction compared only display strings.
- Explicitly selecting index 0 yielded live value `0`, then `None` after reopening.

The distinction between option labels and export values matters to consumers; the exact interoperability contract should be verified against current viewers and the relevant PDF version, rather than inferred from a display-only fixture.

**Impact:** Data inspection, choice editing, subsequent filling, and export workflows can disagree or lose selections.

**Recommended fix:** Represent each option with explicit display and export values. Centralize conversion between the public API and PDF representation. Preserve selected index zero and distinguish no selection from a first-item selection. Specify whether string inputs match labels, exports, or editable custom entries.

**Acceptance criteria:** Exercise create → fill → read → reopen, and update choices → fill → reopen. Include distinct labels/exports, duplicate labels, empty values, selected index zero, unknown strings, and externally generated dropdowns.

### R08 — Changing a radio selection leaves multiple active appearances

**Location:** [filler.py:80][filler-update], [patterns.py:261][patterns-radio].

The fill loop updates the selected radio widget, but does not reset other widgets in the group to `/Off`.

**Observed:** On the repository's radio-button sample:

~~~python
pdf.fill({"radio_1": 0})
pdf.fill({"radio_1": 1})
~~~

left the two widget appearance states as `["/0", "/1"]`, while their shared parent value was `"/1"`.

**Impact:** The form's logical value says one thing while the widget appearances say two options are selected. Some viewers may repair this, but the file itself remains inconsistent. This also matters when filling a form that already has a selected option, not only when repeatedly calling the same object.

**Recommended fix:** Process selection as a group operation. Clear all non-selected widget appearances, set the parent value once, and preserve the relationship between option/export values and appearances.

**Acceptance criteria:** Select A, then B, then A again; reopen between changes; include groups spanning pages and forms from more than one producer. Assert exactly the appropriate appearance states and parent value, then render.

### R09 — Full-name mode prevents collision-free merges

**Location:** [wrapper.py:171][wrapper-add], [wrapper.py:880][wrapper-commit].

`__add__()` unconditionally calls `other.commit_widget_key_updates()`. That method raises `NotImplementedError` whenever full-name mode is enabled, even if there are no queued renames.

**Observed:** Merging one full-name wrapper containing `left` with another containing `right` raised `NotImplementedError`. There were no naming collisions.

**Impact:** Two documented capabilities—merging and full-name lookup—cannot be freely composed. Page slices that merge wrappers can inherit the same failure.

The documentation explicitly limits renaming in full-name mode. That limitation does not explain why a collision-free merge must fail.

**Recommended fix:** Avoid committing an empty rename queue. Define an explicit policy for genuine hierarchical collisions: deterministic namespace, requested renaming, or a descriptive error. Keep collision-free merging available.

**Related design issue:** Addition mutates the right-hand wrapper when resolving collisions and returns an existing operand directly for empty inputs. Those aliasing behaviors complicate reuse. Document them clearly or move toward a non-mutating merge operation. Random suffixes are already documented, so randomness itself is a design tradeoff, not an undisclosed defect.

**Acceptance criteria:** Merge full-name forms with distinct names, true collisions, identical partial names under different parents, and page slices. Verify source wrappers' identities and data after merging. If mutation is retained for compatibility, test and document it explicitly.

### R10 — Validation and cached state disagree with actual PDF behavior

**Locations:** [adapter.py:36][adapter], [middleware/dropdown.py:118][middleware-dropdown-schema], [middleware/radio.py:34][middleware-radio], [hooks.py:382][hooks-geometry], [cli/update.py:281][cli-update], [wrapper.py:650][wrapper-fill].

This is a collection of related boundary problems rather than one crash:

| Probe | Observed behavior | Consequence |
| --- | --- | --- |
| Validate dropdown index `-999` against `pdf.schema` | Accepted; filling raised `IndexError` | Schema allows data the implementation cannot process |
| Validate radio index `-999` | Accepted; fill succeeded without selecting a matching option | Success can conceal invalid input |
| Assign integer `pdf.widgets["test"].x = 123` | Live object says 123; reopened PDF still says 73.3365 | Geometry hooks silently accept only actual floats |
| CLI sets `max_length` on a checkbox | Exit 0; reopened widget has no such property | Schema validates property names without validating widget applicability |
| Construct with a nonexistent path | Empty wrapper and `read() == b""` | Missing input can be mistaken for intentional empty-document construction |
| Fill with `readonly=True` | Live `readonly` remains false; reopened value is true | Inspection depends on whether the wrapper was recreated |
| Use removed `flatten=True` keyword in 6.0.0 | Accepted silently, no warning, output remains editable | Old integrations receive changed behavior without an actionable failure |
| Merge an empty or one-item `PdfArray` | `IndexError` | Variable-size batch workflows need undocumented-at-user-guide-level guards |

The `flatten` parameter was intentionally removed in a major release; removing it is legitimate. Silently absorbing it through `**kwargs` is the avoidable problem.

**Additional structural weakness:** Many property readers and writers inspect only the immediate widget or parent. PDF field inheritance can extend further, with defaults at the AcroForm level. The inherited default-appearance case in R02 demonstrates a real failure. Default-appearance parsing also uses string splitting rather than a PDF-token-aware representation.

**Recommended fix:**

- Validate field values, index ranges, geometry, page bounds, and property applicability in a common library layer.
- Make the CLI reuse those checks and translate predictable errors into concise parameter errors.
- Treat integers as valid numeric geometry where the API accepts real-valued coordinates.
- Reject unknown/removed keyword arguments explicitly.
- Separate intentional empty construction from nonexistent/unsupported inputs.
- Define whether live middleware is authoritative or a snapshot, then update/invalidate it consistently.
- Add a cycle-aware inheritance resolver instead of repeating one-parent checks.
- Define empty and single-item merge behavior deliberately.

**Acceptance criteria:** Validated data must not fail later because of missing basic range/type checks. Invalid values must leave the document unchanged. Live and reopened state must agree for fields modified by public operations.

### R11 — Internal links use numeric destinations instead of page references

**Location:** [annotations/link.py:45][annotation-link], [template.py:500][template-annotations].

`LinkAnnotation(page=2)` builds `/Dest [1 /Fit]`. For a local explicit destination, the first element is a reference to the destination page object; numeric page indices are used for remote destinations. [Adobe PDF Reference, explicit destinations](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.3.pdf).

**Observed:** A link added to a two-page document contained a `NumberObject` as its first destination element. No writer-level step resolved it to the target page's indirect reference.

**Impact:** Internal navigation depends on tolerant viewer behavior and can be wrong after merging or reordering pages.

**Recommended fix:** Resolve page destinations against the writer during annotation insertion. The dataclass can retain a user-facing page number, but serialization needs document context. Validate that the target page exists.

**Acceptance criteria:** Inspect the actual indirect reference, exercise the link in a viewer, then test merges and page reordering. Out-of-range destinations should produce a useful error before output mutation.

### R12 — Font handling assumes resource naming conventions and leaks registrations

**Location:** [font.py:185][font-temporary], [font.py:381][font-name].

**Confirmed resource-name failure:** `_get_new_font_name()` attempts `int(key[2:])` for every font resource starting with `/F`. A valid resource key such as `/FontA` therefore raises `ValueError` when registering a new font. Resource names need not follow the library's `/F1`, `/F2` convention.

**Confirmed cleanup failure:** `temporary_font_registration()` stores one generated registry name per user alias in a dictionary. Registering the same alias twice creates two entries in ReportLab's global registry but retains only the second for cleanup. A probe with two registrations under `same` left one new registry entry after the context exited.

The wrapper's registration-event list permits repeated aliases, so the helper's assumption is not isolated from public workflows. An exception during setup also occurs before the current cleanup `try/finally` begins; partial setup cleanup deserves coverage.

**Impact:** Arbitrary input forms can fail custom-font registration, and long-lived workers can accumulate temporary font objects. Thread-safety is not established merely because generated names use UUIDs; the backend registry remains global.

**Recommended fix:** Match only the exact numeric resource pattern when allocating `/F#` names. Track every inserted registry key separately from the alias-to-current-font mapping, and protect the complete registration sequence with cleanup. Consider a scoped backend abstraction rather than direct registry mutation.

**Acceptance criteria:** Test `/FontA`, `/FCustom`, sparse numeric names, duplicate aliases, partial registration failure, repeated draw operations, and a documented concurrency policy.

### R13 — Quality and release safeguards have concrete gaps

**Locations:** [scripts/linting.sh][script-lint], [scripts/doc_examples_type_check.py][script-doc-check], [scripts/pdf_diffs.sh:16][script-diffs], [bump-version workflow][workflow-bump], [publish workflow][workflow-publish], [release script][script-release].

**Local lint failure can be hidden.** `scripts/linting.sh` invokes four commands without stopping or accumulating failures. A mocked Pylint exit status of 17 followed by three successful checks produced a final script status of 0. This affects the local Makefile gate. The GitHub lint workflow runs separate steps, so the same masking does not automatically apply there.

**The documentation checker can fail open.** If Pyright's output is not valid JSON, `run_pyright()` returns `None`, and `main()` cleans up and returns normally. The subprocess return code is not itself enforced. Tool failure should fail the check.

**The PDF comparison helper can erase contributor work.** After regenerating samples, `scripts/pdf_diffs.sh` executes:

~~~shell
git restore --source=HEAD --staged --worktree -- ./pdf_samples ./docs/pdfs
~~~

That restores both index and working tree for entire directories, including edits that existed before the comparison command. No clean-tree precondition or original-state restoration is present. This dangerous helper was inspected, not executed.

**The final release artifact has no visible validation gate.** The version-bump workflow can run formatting/import fixes and commit with `[skip ci]`. The publish workflow subsequently builds and publishes without rerunning tests or testing the built distribution. The checkout may be correct and a human may manually check it, but the tracked automation does not enforce that evidence for the final commit/artifact.

**Release helper failures may not fail the job.** `create_release.py` prints an error for a non-201 response but does not exit nonzero. It also checks version inequality rather than ordering and omits an explicit commit target for new tags. Those choices make manual workflow context and race conditions more consequential.

**Recommended fix:** Make local checks fail closed, preserve contributor state in comparison tools, and require validation of the exact release revision and built wheel before publishing. Keep release actions human initiated as required by repository policy. Pin the target commit explicitly when creating a tag/release.

**Acceptance criteria:** Inject failures into each quality tool and require nonzero exit status. Run the comparison workflow in an isolated checkout with pre-existing staged and unstaged sample changes and verify byte-for-byte preservation. Make it impossible for the publishing job to proceed after failed validation.

## 5. Additional quality and stability observations

### 5.1 A passing suite measures consistency with fixtures, not all PDF semantics

The existing suite is valuable and fast enough for frequent use. Its heavy use of serialized-byte comparisons catches regressions in established outputs. It also creates a risk: an invalid structure can become the expected fixture and remain permanently green.

The Developer Guide explicitly presents byte equality as the normal testing pattern. `tests/conftest.py` supports regenerating expected outputs from the implementation under test. That is useful tooling, but regenerated expectations need independent review. Coverage cannot distinguish a correct behavior from a consistently wrong one.

Examples from this review:

- R01 passes a visible page-count check while retaining excluded content.
- R06 passes a check of `pdf.widgets` while the catalog retains removed values.
- R07 can preserve expected `/Opt` bytes while emitting a nonsense `/V`.
- R08 can report the correct parent value while several appearances remain active.
- R04 can display successfully in one viewer while its object types violate the PDF structure.

The branch run adds useful information, but its 94.44% branch result is not the central issue. Many failures occurred along already-covered lines. Better assertions and operation combinations matter more than mechanically raising the percentage.

### 5.2 Cross-platform assurance is narrower than the matrix suggests

The test workflow configures 15 OS/Python combinations. On Windows, and whenever zlib-ng is detected, it excludes tests marked `requires_zlib_over_zlib_ng`. There are 71 statically identified test functions carrying that marker, about 19% of the 380 test functions.

This is an understandable response to serializer/compression differences; it is not evidence that the skipped functionality is broken on Windows. However, skipping whole tests loses semantic coverage along with byte equality.

Recommended structure:

| Test layer | Purpose | Where to run |
| --- | --- | --- |
| Semantic assertions | Values, references, field identity, preserved metadata/annotations | Every supported platform/backend |
| Byte-level fixtures | Detect unexpected serialization changes | Controlled canonical environment |
| Rendered output checks | Appearance, alignment, fonts, visibility | Small representative matrix of independent viewers/renderers |
| Operation-sequence tests | Refill, remove, rename, merge, extract, reopen | Every supported platform where practical |
| Malformed/hostile input checks | Bounded failures and exception safety | Isolated resource-limited test workers |
| Package smoke tests | Installed library and CLI behavior | Built artifacts, outside the source tree |

There are already semantic tests in the repository; the recommendation is to expand them around the identified invariants, not to replace the entire suite.

### 5.3 Typing currently provides less protection than its presence implies

Pyright runs, but `pyproject.toml` disables argument-type, attribute-access, index, operator, and general-type issue reporting. Untyped dictionaries and dynamic `getattr/setattr` calls are common at important boundaries. Several properties are annotated as non-null even though `None` is a normal runtime state.

This is particularly relevant to a dropdown that may hold strings or tuples, a coordinate that may be scalar or per-option list, and an optional value represented through inherited base classes. R07 and R10 illustrate the practical cost.

The built wheel also lacked a `py.typed` marker. If supported consumer-facing typing is a project goal, package it explicitly and test a small external consumer project. The absence is a P3 packaging improvement, not a runtime failure.

Recommended sequence: tighten one boundary at a time, introduce typed option and operation records, then restore diagnostic categories for those modules. Avoid an unrelated repository-wide annotation rewrite.

### 5.4 Error behavior lacks a coherent public contract

Some invalid inputs are ignored, some become empty streams, some produce raw backend exceptions, and the CLI catches only selected errors. This makes retry logic and user feedback unpredictable.

A small documented error taxonomy would help: invalid input, unsupported PDF feature, invalid operation, and output failure. Preserve original causes for debugging. Do not hide unexpected programming errors under a blanket exception handler.

Validate the complete operation before committing state. For example, a batch containing several valid fields and one invalid field should not partially mutate cached values while reporting failure.

### 5.5 Field discovery relies on producer-specific patterns

`WIDGET_TYPE_PATTERNS` uses combinations of `/FT`, parent properties, and appearance states to identify fields. This handles known producers, but it is a fragile substitute for a normalized field model. Some checks only consider one inheritance level, and checkbox/radio interpretation depends on patterns beyond the field flags.

An unsupported annotation should remain preserved and diagnosable. It should not disappear merely because the library cannot expose a convenient middleware class for it. R05 makes this a correctness requirement rather than a theoretical extensibility concern.

### 5.6 Image signatures, read-only flags, and flattening need precise capability boundaries

The fill documentation correctly describes a handwritten signature image. That operation is not cryptographic signing. Similarly, a field's read-only flag is not encryption or an integrity guarantee, and it is not equivalent to flattening into page content.

The recent rename from `flatten` to `readonly` improves terminology. The next improvement should be explicit migration errors and a concise capability table covering image placement, signature-field creation, digital signing, read-only fields, and true flattening.

No claim is made here that PyPDFForm advertises full cryptographic signing. The concern is preventing adjacent capabilities from being mistaken for one another in user workflows.

### 5.7 Security posture needs a documented processing boundary

The security policy provides a responsible-disclosure route and limits fixes to the latest version. Those are clear choices. The project also processes complex PDFs, images, and fonts through multiple backends, so applications accepting untrusted uploads need a well-defined resource and feature boundary.

The reviewed code does not implement a global document-size, page-count, elapsed-time, or memory budget. That is often appropriately managed by the hosting application. Document the responsibility and provide examples of isolated worker processing rather than suggesting every library call is safe for arbitrary untrusted data.

No backend CVE inventory or adversarial denial-of-service campaign was performed. The confirmed disclosure condition in R01 is sufficient to warrant prompt attention without speculating about unverified exploits.

## 6. Performance, memory, and scaling

### 6.1 Page extraction is eager and repeatedly handles the full source

The `pages` property builds every page wrapper before returning a sequence. Therefore `pdf.pages[0]` does work for all pages. For each output page, annotation copying reparses the original source; R01 also causes output pages to retain unnecessary source-page content.

A cold-cache microbenchmark generated documents with one text field per page and measured the first access to `pdf.pages[0]`. Input construction was outside the timed interval.

| Input pages | Source size | Access time | First output page size |
| --- | ---: | ---: | ---: |
| 5 | 8,470 bytes | 0.0249 s | 8,672 bytes |
| 10 | 14,532 bytes | 0.0795 s | 14,754 bytes |
| 20 | 26,702 bytes | 0.2758 s | 26,967 bytes |
| 40 | 51,283 bytes | 1.0728 s | 51,564 bytes |

These are single observations on small synthetic files, not statistically rigorous benchmarks or projected service limits. They nevertheless agree with the code's repeated-whole-document work: doubling from 20 to 40 pages took roughly four times as long. The output-size pattern independently reinforces the object-graph problem.

**Recommendation:** Fix ownership first, then provide selective/lazy extraction with one source parse and a deliberate cloning map. Preserve an eager compatibility API if necessary, but avoid making extraction of one page require serialization of all pages.

### 6.2 Cache entry counts are bounded; retained bytes are not

Several `lru_cache(maxsize=8)` instances retain complete PDF, font, or image bytes as keys and often additional results as values. A limit of eight is a meaningful improvement over an unbounded cache. It does not bound memory when documents are large, and separate caches can retain different generations of the same workflow.

The page-stream cache is especially consequential because one result contains all page streams. With R01, those streams can each contain much of the source document.

This is a scaling and data-lifetime risk, not a claim that the caches grow without limit. Add optional cache disabling/clearing and consider a byte budget or document-scoped cache. Measure peak memory before choosing limits. Sensitive document bytes may remain resident after a wrapper is dropped because a module-level cache retains them.

### 6.3 Rewriting and font replay amplify work

Title updates, style hooks, fill, copying annotations, registering fonts, and egress can each parse/write the document. Replaying registered fonts after operations can append resource versions instead of maintaining a stable document-owned resource identity. Sequential `+` merging also has cumulative growth; the pairwise `PdfArray.merge()` is a useful existing mitigation.

Prioritize measurements of common end-to-end workflows:

- Load → style several fields → fill → write.
- Fill one image alongside many ordinary fields.
- Extract one page from a large form.
- Merge 10/100 forms with collisions and fonts.
- Repeated operations in a persistent worker.

Track elapsed time, peak memory, output size, object count, and resource count. Do not optimize isolated helper calls while the output graph is still wrong.

## 7. Roadmap and maintenance evaluation

### 7.1 What the available evidence says

The project is maintained. Recent local history includes dependency/security-related updates, cache-size reductions, annotation/resource fixes, CLI input improvements, terminology changes, removal of deprecated options, and Python support changes.

The tracked news pages explain earlier architectural transitions, including the move away from drawing all filled content as watermarks. That direction makes sense for preserving editable forms. The remaining image/signature paths still use a remove/draw/copy sequence, which is where several present defects arise.

However, no current consolidated roadmap or 6.0 migration guide was found in the tracked documentation. The most recent news entry in the navigation concerns the 4.0 release. The release process promises Semantic Versioning, but users still need an operational explanation of which behaviors changed and how to detect incompatible calls.

The 5.6-to-6.0 diff includes:

- Raising the minimum Python version from 3.10 to 3.11.
- Moving the configured support/test window to Python 3.11–3.15.
- Removing the deprecated CLI `--preserve-metadata` and `--flatten` options.
- Removing the Python implementation's handling of `preserve_metadata` and `flatten`, while leaving general `**kwargs` acceptance.

The major version bump is appropriate for removals. The migration experience is incomplete because Python calls may silently continue with altered behavior.

### 7.2 Product decisions that should be explicit

| Decision | Recommended default | Why it matters |
| --- | --- | --- |
| Preservation of unknown PDF structures | Preserve unless explicitly unsupported and rejected | Silent deletion is more damaging than a clear capability limitation |
| Default appearance strategy | Valid PDF structure with a documented rendering policy | Users should not need to discover an invalid default by comparing viewers |
| Full names and duplicate field names | Stable field identity plus explicit merge-collision policy | Required for reusable schemas, hierarchical forms, and deterministic workflows |
| Library validation | Shared with CLI, before mutation | A library caller should not receive weaker correctness guarantees by default |
| Missing inputs and unknown arguments | Actionable error | Silent no-op/empty output hides integration mistakes |
| Mutation semantics | Explicitly documented; avoid mutating merge operands where feasible | Predictable composition and reuse |
| Signature scope | Image placement and field creation clearly separate from cryptographic signing | Prevents unsupported assumptions |
| Support lifecycle | Publish a Python/release support table and upgrade path | Latest-only security support can force runtime upgrades |
| Viewer support | Small named matrix with tested feature boundaries | A blanket PDF compatibility implication is difficult to sustain |
| Performance target | Publish representative workload measurements before promises | Page count alone is not a sufficient complexity measure |

The reported demand for predictable merged field names is directly relevant to this policy work. The font issue is a reason to define multilingual/rendering support, not evidence that a specific new font engine must be selected immediately. [Merge naming report](https://github.com/chinapandaman/PyPDFForm/issues/2036), [font rendering report](https://github.com/chinapandaman/PyPDFForm/issues/1153).

### 7.3 Recommended implementation order

The sequence below is a proposed maintainer roadmap, not a claim about existing commitments. Estimates are deliberately omitted: implementation effort depends on the preservation contract and supported PDF structures.

| Phase | Work | Completion gate |
| --- | --- | --- |
| 0 — Contain immediate harm | R01 page ownership/excluded-content retention; R02 safe output; protect unrelated annotations/signatures in R03 | Independent reproductions become regression tests and pass; failed operations preserve files |
| 1 — Restore form invariants | R05/R06 catalog maintenance; R07 dropdown values; R08 radio states; fix R04 appearance structure | Reopened values and object graph agree; no-op serialization preserves untouched fields |
| 2 — Make operations composable | R09 full-name merges; R10 shared validation/state refresh; R11 page references; R12 font ownership | Public operation sequences behave consistently with explicit failures for unsupported cases |
| 3 — Improve assurance and delivery | R13 fail-closed tools; artifact tests; semantic checks on skipped platforms; release migration guide | Exact release revision and built wheel validated; tool failures cannot report success |
| 4 — Improve scale | Selective extraction, fewer parses/writes, resource deduplication, cache controls | Benchmarks show improved time/memory without preservation regressions |
| 5 — Expand supported capabilities | Broader Unicode/layout or form features selected from actual demand | Written compatibility contract, representative corpus, and independent rendering evidence |

Phases overlap: write safety and failure-propagation fixes can be small changes, while field-graph work is larger. Do not defer the small protective fixes until a broad architecture refactor is complete.

### 7.4 Concrete release-readiness checklist

A maintenance release addressing this review should demonstrate:

- Extracted files contain no excluded page payloads via unintended references.
- Existing output files survive any failure before successful replacement.
- Filling one field preserves unrelated annotations and unfilled fields.
- Removing fields updates both the page annotations and form catalog.
- Dropdown labels, exports, selection indices, and serialized values have one documented mapping.
- Radio values and widget appearances are mutually consistent.
- `/AP` entries have valid types and supported viewers render representative outputs correctly.
- Full-name collision-free merges work, and collision behavior is explicit.
- Invalid indices/properties/arguments fail before mutation.
- The built distribution, not only the checkout, passes smoke tests.
- Migration documentation names removed options and shows replacements.
- The final release commit and artifact have passed required validation.

These are concrete gates; “100% coverage” alone should not be used as a substitute.

### 7.5 Maintainer capacity and backlog quality

Local commit history is strongly concentrated in the lead maintainer's author identity, with additional similar author labels and automation. This suggests concentration of project knowledge, but commit aliases are not a reliable count of distinct humans.

Reduce that risk with a short architecture/invariant guide, a curated interoperability corpus, and documented ownership for release and compatibility decisions. The goal is to let another contributor understand why a field graph or appearance stream must be handled a particular way.

The nightly stale-issue script closes issues with old comments unless they have `help wanted`. It does not establish that the underlying defect is resolved. Its API handling also lacks pagination, request timeouts, response validation, and an explicit exclusion of pull-request records returned by the issues endpoint. These are secondary maintenance-tool concerns; the script was not run.

Keep confirmed correctness bugs, security-sensitive reports, and roadmap decisions exempt from automatic closure unless a maintainer deliberately resolves them. A small open-issue count is not a stability metric.

### 7.6 Dependency and supply-chain posture

The project has sensible dependency range limits and active update automation. The nightly lowest-direct-dependency job is a positive sign. However:

- Ordinary CI resolves fresh dependency versions, so results can drift independently of source changes.
- The minimum-direct-dependency job uses a single current Python/OS combination.
- Private backend APIs increase the importance of testing version edges.
- The development container and some tooling use moving tags.
- Published wheels are not visibly smoke-tested by the release workflow.

Use a reproducible canonical environment for golden byte fixtures while retaining a separate latest/minimum compatibility matrix. Application developers can pin their environments; the library need not freeze every runtime dependency indefinitely. Consider commit-pinned third-party Actions where practical, with automated updates, and preserve the existing least-privilege/OIDC direction.

No claim is made that a dependency in the reviewed environment has a known vulnerability. This section evaluates process and reproducibility.

## 8. Proposed test contracts

These are the most valuable new regression contracts for this codebase:

| Contract | Representative assertion | Finding addressed |
| --- | --- | --- |
| Selected-page isolation | Excluded text/image streams absent from serialized object graph | R01 |
| Page ownership | Every widget `/P` identifies a retained destination page | R01, R11 |
| Atomic output | Failed operation leaves destination bytes unchanged | R02 |
| Unrelated-content preservation | Unmodified annotations and fields remain after fill/draw/style | R03, R05 |
| Complete removal | Removed field absent from both annotations and catalog | R06 |
| Value round trip | `reopen(fill(data)).data` preserves supported values including zero | R07, R10 |
| Radio consistency | Parent `/V` and every child `/AS` agree | R08 |
| Appearance validity | `/AP` is a dictionary; referenced appearance objects are valid | R04 |
| Schema/runtime agreement | Schema-accepted boundary inputs are supported; invalid ranges rejected | R10 |
| Full-name composition | Extraction and collision-free merge work with hierarchical identity | R09 |
| Resource lifecycle | Font registry/resource counts remain stable across repeated operations | R12 |
| Failure propagation | Any failed check causes a failed gate | R13 |
| Preservation on no-op | Catalog-only fields and unrecognized structures survive serialization | R05 |

Property-based or generated tests would be particularly useful for index bounds, operation ordering, inheritance depth, repeated field names, and mixed annotation types. They should complement a small curated real-world corpus. A new framework is not required to start: straightforward pytest cases for the reproductions below would already add substantial value.

## 9. Reproduction appendix

The snippets below are intentionally independent of the temporary review scripts. Run from the repository root in an environment selected according to `make check-zlib` and the Developer Guide. They create synthetic or temporary data and do not overwrite checked-in fixtures.

### A. Excluded page content retained after extraction

~~~python
from io import BytesIO

import pikepdf
from reportlab.pdfgen.canvas import Canvas

from PyPDFForm import PdfWrapper

buffer = BytesIO()
canvas = Canvas(buffer)
canvas.drawString(30, 700, "KEEP_FIRST_PAGE")
canvas.acroForm.textfield(
    name="field1", x=30, y=600, width=100, height=20
)
canvas.showPage()
canvas.drawString(30, 700, "EXCLUDED_SECRET_SECOND_PAGE")
canvas.showPage()
canvas.save()

source = buffer.getvalue()
output = PdfWrapper(source).pages[0].read()

with pikepdf.Pdf.open(BytesIO(output)) as pdf:
    leaked_streams = [
        obj.objgen
        for obj in pdf.objects
        if isinstance(obj, pikepdf.Stream)
        and b"EXCLUDED_SECRET_SECOND_PAGE" in obj.read_bytes()
    ]
    page = pdf.pages[0].obj
    widget = page["/Annots"][0]
    print("Visible pages:", len(pdf.pages))
    print("Excluded content streams:", leaked_streams)
    print("Output page:", page.objgen)
    print("Widget page:", widget["/P"].objgen)
    print("Widget page parent count:", widget["/P"]["/Parent"]["/Count"])
~~~

Observed: one visible page, a non-empty excluded-content list, different page references, and a widget-page parent count of two. A correct result should have no leaked stream and consistent retained-page references.

### B. CLI failure truncates its input

~~~python
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from pypdf import PdfWriter
from pypdf.generic import NameObject
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

writer = PdfWriter("pdf_samples/sample_template.pdf")
field = next(
    ref.get_object()
    for ref in writer.pages[0]["/Annots"]
    if ref.get_object().get("/T") == "test"
)
writer._root_object["/AcroForm"][NameObject("/DA")] = field["/DA"]
del field["/DA"]
buffer = BytesIO()
writer.write(buffer)
original = buffer.getvalue()

with TemporaryDirectory() as directory:
    path = Path(directory) / "input.pdf"
    path.write_bytes(original)
    result = CliRunner().invoke(
        cli_app,
        ["update", "field", str(path), "--field", "test", "--font_size", "14"],
    )
    print("Exit:", result.exit_code)
    print("Exception:", repr(result.exception))
    print("Before:", len(original), "After:", path.stat().st_size)
~~~

Observed: exit 1, `KeyError('/DA')`, size 624,427 → 0 bytes. The private writer access is only for constructing the controlled input PDF in this reproduction.

### C. Removing all fields retains their values

~~~python
from io import BytesIO

from pypdf import PdfReader

from PyPDFForm import PdfWrapper

pdf = PdfWrapper("pdf_samples/sample_template.pdf")
pdf.fill({"test": "REVIEW_SENTINEL"})
pdf.remove_fields(list(pdf.widgets))
reader = PdfReader(BytesIO(pdf.read()))

print("Wrapper fields:", list(pdf.widgets))
print("Catalog fields:", list(reader.get_fields()))
print("Retained value:", reader.get_fields()["test"]["/V"])
~~~

Observed: empty wrapper fields, six catalog fields, and the sentinel value.

### D. Choice tuples become a literal Python tuple string

~~~python
from io import BytesIO

from pypdf import PdfReader

from PyPDFForm import BlankPage, Fields, PdfWrapper

pdf = PdfWrapper(BlankPage()).bulk_create_fields(
    [Fields.DropdownField("choice", 1, 20, 20, options=["Apple", "Banana"])]
)
pdf.widgets["choice"].choices = [("Pear", "P"), ("Grape", "G")]
pdf.fill({"choice": 1})
output = pdf.read()
field = PdfReader(BytesIO(output)).pages[0]["/Annots"][0].get_object()

print("Options:", field["/Opt"])
print("Value:", field["/V"])
print("Reopened data:", PdfWrapper(output).data)
~~~

Observed: options `[["P", "Pear"], ["G", "Grape"]]`, value `"('Grape', 'G')"`, reopened selection `None`.

### E. Other executed probes and expected regression outcomes

| Probe setup | Current observed result | Desired regression assertion |
| --- | --- | --- |
| Add catalog-only `hidden_business_id` to a sample; call wrapper `read()` | Field disappears from `get_fields()` | Field and value remain |
| Create two signature fields; fill only the first | Both absent on reopen | Unfilled second field remains |
| Add a text note beside a signature/text field; fill signature | Note disappears | Note remains |
| Fill standard text with default wrapper settings | `/AP` is `TextStringObject` | Appearance structure is valid |
| Fill `radio_1` with 0, then 1 | Child states `/0` and `/1` both active | First is `/Off`; second matches parent selection |
| Merge full-name forms named `left` and `right` | `NotImplementedError` | Both fields retained |
| Give dropdown/radio schema index `-999` | Validation accepts it | Validation rejects before mutation |
| Set text x-coordinate to integer 123 | Reopened x remains 73.3365 | Reopened x is 123 |
| Set checkbox `max_length` through CLI | Success with no effect | Descriptive property-applicability error |
| Fill with `readonly=True` and inspect same wrapper | Cached false, reopened true | Consistent state |
| Call 6.0 `fill(..., flatten=True)` | Silently ignored | Explicit removed-argument error/migration guidance |
| Register a font in a document containing `/FontA` | `ValueError` | New font allocated safely |
| Temporary registration repeats one alias | One global entry leaks | Registry returns to baseline |
| Construct local page-2 link | `/Dest [1 /Fit]` | Destination page indirect reference |
| Mock first lint command failing and later commands succeeding | Exit 0 | Nonzero exit |

The temporary probe harness records exceptions per case, so its own zero exit status is not a claim that the behaviors passed. The report's findings are based on the emitted outcomes and independent object inspection.

## 10. Recommended maintainer decisions

The highest-value decision is to treat **preservation and transactional safety as the next release's primary scope**. R01–R03 should lead. R04–R08 then address the core promise that filling, reading, and removing form data produce internally consistent PDFs.

Keep the current API's convenience, the documentation examples, the existing fixture corpus, and the fast test loop. Strengthen their foundations with explicit field identity, graph-preserving operations, valid appearances, shared validation, and semantic assertions.

A credible outcome is not simply another green coverage badge. It is a set of independently checked guarantees: excluded pages stay excluded, failed writes preserve files, untouched content survives, and reopened form data agrees with what the caller requested.

## Source locations for the reviewed snapshot

Code links below resolve to the reviewed commit. The local checkout is the source used for all runtime probes. External documentation links embedded above provide supporting PDF-format/backend context; they are not substitutes for the local reproductions.

[wrapper-pages-cache]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L274
[wrapper-pages]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L429
[wrapper-write]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L569
[wrapper-fill]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L650
[wrapper-read]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L490
[wrapper-remove]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L833
[wrapper-add]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L171
[wrapper-commit]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/wrapper.py#L880
[watermark-clone]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/watermark.py#L342
[utils-remove]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/utils.py#L32
[hooks-font-size]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/hooks.py#L184
[hooks-options]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/hooks.py#L341
[hooks-geometry]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/hooks.py#L382
[cli-update]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/cli/update.py#L281
[patterns-dropdown]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/patterns.py#L304
[patterns-dropdown-read]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/patterns.py#L336
[patterns-options]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/patterns.py#L431
[patterns-text]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/patterns.py#L360
[patterns-radio]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/patterns.py#L261
[egress-appearance]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/egress.py#L32
[egress-fields]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/egress.py#L81
[template-discovery]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/template.py#L380
[template-remove]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/template.py#L543
[template-annotations]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/template.py#L500
[middleware-dropdown]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/middleware/dropdown.py#L75
[middleware-dropdown-schema]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/middleware/dropdown.py#L118
[middleware-radio]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/middleware/radio.py#L34
[filler-update]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/filler.py#L80
[adapter]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/adapter.py#L36
[annotation-link]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/annotations/link.py#L45
[font-temporary]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/font.py#L185
[font-name]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/PyPDFForm/lib/font.py#L381
[script-lint]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/scripts/linting.sh
[script-doc-check]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/scripts/doc_examples_type_check.py
[script-diffs]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/scripts/pdf_diffs.sh#L16
[workflow-bump]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/.github/workflows/bump-version.yml
[workflow-publish]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/.github/workflows/python-publish.yml
[script-release]: https://github.com/chinapandaman/PyPDFForm/blob/0b5cc1dc8604b36693864852d76ed7e60f903451/scripts/create_release.py
