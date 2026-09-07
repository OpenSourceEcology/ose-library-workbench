# OSE Library Workbench

FreeCAD 1.x workbench for browsing, compiling, editing, and validating OSE
Schema Canon libraries, including housing and machine entries currently stored
in [vcs-library](https://github.com/OpenSourceEcology/vcs-library). The workbench
uses the library root you select; it does not require a VCS/GVCS hierarchy.

## Install

Clone this repository into the `Mod/ose-library-workbench` directory beneath
FreeCAD's user application directory (shown by `App.getUserAppDataDir()` in the
FreeCAD Python console), then restart FreeCAD. This is a manual installation;
Addon Manager registry submission remains future work.

The workbench needs `libtools` from `vcs-library` and its Python dependencies,
including PyYAML, available to **FreeCAD's Python interpreter**. For FreeCAD
installations sharing a normal Python environment, install with that interpreter:

```sh
python -m pip install 'libtools @ git+https://github.com/OpenSourceEcology/vcs-library'
```

Bundled FreeCAD installations may use a different Python environment from your
terminal. Check `import libtools, yaml` in the FreeCAD Python console. A local
`vcs-library` checkout can also supply `libtools` by adding its absolute directory
to `sys.path` in that console; PyYAML must still be available. The selected
collection's compiler helpers are resolved automatically by the workbench.

Clone `vcs-library` separately for editable source files, then select the
**OSE Library** workbench.

## Use

1. **Open Library** and choose a library root: the `vcs-library` checkout for
   housing, or the current `collections/gvcs` directory for the eight machine
   entries. This directory is a storage location, not a separate construction
   set; choose the new root if the files are reorganized later.
2. Select an entry, then **Compile Entry** to create a document.
3. With that entry and its document active, **Edit Parameters** and choose
   **Apply**. A successful compile replaces the previous managed geometry.
   A failed compile rolls back, retaining the previous geometry and parameters.
   Other objects you added to the document are preserved.
4. **Validate Entry** checks that document's managed geometry and the entry's
   source code. Results appear in the panel and in `<library-root>/reports/`.
5. **Export changed schema…** writes `schema.py.new` next to `schema.py` for
   manual review and merging. Exporting alone does not apply changes to geometry.

Saved FCStd documents retain their library location, entry identity, managed
object names, and last successfully applied schema. After reopening, select the
same library entry before editing or validating. A different entry, a different
checkout, or an unrelated active document is rejected. If you move the checkout
or delete its managed geometry, compile a new document from the selected entry.

GVCS source geometry is fixed except where its schema exposes dimensions (for
example, the idler spacer's diameters and thickness). Source-part lists, schema
identity, document name, and units are read-only in the form. Validation results
retain the collection's existing fit/assembly review findings; successful
compilation does not establish fabrication readiness.

## Core API and checks

The headless core imports neither Qt nor FreeCAD. `compile_entry_into` retains
its append-only behavior, and `validate_live` checks all objects in the supplied
document. Integrations using these generic APIs do not need document bindings.
The GUI uses the stricter APIs:

- `compile_managed_entry`: compile and bind a document in a FreeCAD transaction.
- `replace_managed_entry`: replace only recorded objects, with rollback on error.
- `require_managed_entry` / `managed_schema_override`: check document identity and
  retrieve the applied parameters, including after save/reopen.
- `validate_managed_entry`: validate only the bound entry's geometry.

Compiler imports search the entry directory and selected library root during
both module loading and `compile()`. Local helper imports are scoped to that
synchronous call, so switching between collections does not reuse another
collection's identically named helper. Compilers remain ordinary trusted Python
code, and should create their output in the provided document.

Run headless unit tests with `python -m pytest -q` after installing `libtools`
and `pytest`. CI also compiles housing and machine entries in real FreeCAD,
checks replacement, rollback and saved bindings, and exercises GUI commands and
the parameter dialog with Xvfb. Its machine fixture path can be overridden with
`OSE_MACHINE_LIBRARY_SUBDIR` when source storage changes. See
[docs/plan.md](docs/plan.md) for the original scope and remaining authoring work.
