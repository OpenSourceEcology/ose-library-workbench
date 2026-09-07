# OSE Library Workbench — Plan

A FreeCAD workbench that makes part-library authoring a first-class FreeCAD
workflow. Libraries built on the
[Schema Canon](https://wiki.opensourceecology.org/wiki/Schema_Canon) structure
(reference implementation:
[vcs-library](https://github.com/OpenSourceEcology/vcs-library)) are today
authored with a text editor and judged in CI. Library authors work in
FreeCAD; this workbench brings the loop to them: browse entries, compile
into the open document, edit schema parameters, and run the validators —
without leaving FreeCAD.

Consumer relationship: this addon depends on `libtools` (from vcs-library)
for discovery, schema loading, validation, and reports. Anything generic
that this workbench needs and libtools lacks gets contributed upstream to
libtools, keeping this repo GUI-only.

## Current compatibility behavior

The workbench now accepts independent collection roots, including
`vcs-library/collections/gvcs`. GUI documents persist their library/entry
identity and applied schema. Parameter Apply transactionally replaces managed
objects; validation rejects mismatched documents and ignores unrelated objects.
The generic headless append/validate helpers remain available to integrations.
See the README for installation and the current workflow.

## v0 scope

1. **Addon skeleton** installable via FreeCAD's Addon Manager layout
   conventions: `package.xml`, `InitGui.py`, workbench class, icon (simple
   original SVG), `ose_library_wb/` Python package. Targets FreeCAD 1.x;
   degrade gracefully (clear message) on 0.21.
2. **Open Library** command: pick a library checkout directory; the
   workbench lists entries in a dockable tree grouped by layer, showing id,
   title, owner, status, and last validation result if a `reports/` dir
   exists.
3. **Compile Entry** command: run the selected entry's
   `compile(schema, doc)` into a new document, recompute, fit view.
4. **Edit Parameters** dialog: form generated from the SCHEMA dict (numbers,
   strings, booleans; nested dicts as sections; lists read-only in v0).
   Apply = recompile into the document with the edited schema (in-memory).
   **Save** = rewrite `schema.py` preserving comments is NOT attempted in
   v0 (comment-preserving rewrite is hard to do honestly); instead "Export
   changed schema…" writes a `schema.py.new` next to the original with a
   banner comment, and the author merges by hand. State this limitation in
   the UI.
5. **Validate Entry** command: run tier-1 (code) validation in-process via
   libtools and tier-2 (output) checks against the just-compiled document
   (reuse `libtools.output_validator.validate_output` with shapes extracted
   from the live document — same extraction as libtools' driver). Results in
   a panel: check name, pass/fail, detail; write the standard report JSON to
   the library's `reports/` dir.
6. **Headless-testable core**: every command's logic lives in
   `ose_library_wb/core.py` functions taking (library_root, entry_id, doc)
   with no Qt imports; the GUI layer is thin. CI (ubuntu, FreeCAD PPA,
   system python — see vcs-library's output-validate.yml for the known
   setup-python pitfall) runs: import smoke of all non-GUI modules under
   freecadcmd, plus core tests: open vcs-library as a fixture (pip-install
   pulls it; use its library/ dir), compile one entry, validate it, assert
   the report matches CI's.

## Later (not v0)

Comment-preserving schema save; new-entry scaffolding from a template;
side-by-side diff of schema edits; slot previews (fab drawing/BOM) once
vcs-library's slot generation lands; Addon Manager registry submission.

Done when: CI green (import smoke + core round-trip on a vcs-library entry);
a FreeCAD user can install by cloning into Mod/, open vcs-library, compile
and validate `extwall_standard`, and read the same PASS report CI produces.
