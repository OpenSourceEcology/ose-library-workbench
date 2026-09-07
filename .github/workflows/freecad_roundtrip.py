"""Real FreeCAD checks for housing, GVCS, replacement and persistence."""
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
from types import SimpleNamespace

sys.path.insert(0, str(Path(os.environ['OSE_WB_ROOT']).resolve()))
if os.environ.get('OSE_WB_LIBTOOLS_PATH'):
    sys.path.insert(0, os.environ['OSE_WB_LIBTOOLS_PATH'])
# Do not inject library/collection paths: production code must resolve helpers.
import FreeCAD as App
import Part
from ose_library_wb import core


def snapshot(doc):
    return [(obj.Name, obj.Shape.Volume) for obj in doc.Objects
            if getattr(obj, 'Shape', None) is not None]


def assert_rejected(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError('Mismatched or unbound document was accepted')


def exercise(root, out):
    gvcs_root = root / os.environ.get('OSE_MACHINE_LIBRARY_SUBDIR', 'collections/gvcs')
    entries = core.open_library(gvcs_root)
    assert len(entries) == 8 and str(gvcs_root) not in sys.path
    results = []
    housing = {entry.id: entry for entry in core.open_library(root)}['extwall_standard']
    for entry in [housing, *entries]:
        doc = App.newDocument('OSEIntegration')
        try:
            created = core.compile_managed_entry(entry, doc)
            assert created and all(obj.Shape.isValid() for obj in created)
            report = core.validate_managed_entry(entry, doc)
            failures = [check.name for check in report.checks if not check.passed]
            expected = ['output:overlap'] if entry.id in {'ceb_drawer_guide', 'power_cube_1708'} else []
            assert failures == expected, (entry.id, failures)
            results.append({'id': entry.id, 'objects': len(created), 'failed_checks': failures})
        finally:
            App.closeDocument(doc.Name)

    spacer = {entry.id: entry for entry in entries}['axis_idler_spacer']
    other = next(entry for entry in entries if entry.id != spacer.id)
    doc = App.newDocument('OSEEditIntegration')
    original_undo_mode = doc.UndoMode
    unrelated = doc.addObject('Part::Feature', 'UserGeometry')
    unrelated.Shape = Part.makeBox(10, 10, 10, App.Vector(10000, 10000, 10000))
    doc.recompute()
    created = core.compile_managed_entry(spacer, doc)
    assert core.validate_managed_entry(spacer, doc).passed
    old_volume = created[0].Shape.Volume
    for thickness in [0.08, 0.12, 0.08]:
        replaced = core.replace_managed_entry(spacer, doc, {'thickness_in': thickness})
        assert len(replaced) == 1 and len(snapshot(doc)) == 2
        assert doc.UndoMode == original_undo_mode
        assert replaced[0].Label == 'Idler spacer'
        assert math.isclose(doc.getObject('UserGeometry').Shape.Volume, 1000, rel_tol=1e-9)
        assert math.isclose(replaced[0].Shape.Volume, old_volume * thickness / 0.04, rel_tol=1e-9)
    changed = core.validate_managed_entry(spacer, doc)
    assert [c.name for c in changed.checks if not c.passed] == ['output:fit'], [(c.name, c.detail) for c in changed.checks if not c.passed]
    assert_rejected(lambda: core.require_managed_entry(other, doc))
    assert_rejected(lambda: core.validate_managed_entry(other, doc))
    assert_rejected(lambda: core.replace_managed_entry(other, doc))
    unbound = App.newDocument('Unbound')
    assert_rejected(lambda: core.require_managed_entry(spacer, unbound))
    App.closeDocument(unbound.Name)

    before = snapshot(doc)
    schema_before = core.managed_schema_override(spacer, doc)
    original_loader = core._load_compiler
    def fail_after_creation(schema, target):
        obj = target.addObject('Part::Feature', 'PartialCompile')
        obj.Shape = Part.makeBox(1, 1, 1)
        raise RuntimeError('Injected failure after creating geometry')
    core._load_compiler = lambda path: SimpleNamespace(compile=fail_after_creation)
    try:
        try:
            core.replace_managed_entry(spacer, doc, {'thickness_in': 0.2})
        except RuntimeError as error:
            assert 'Injected failure' in str(error)
        else:
            raise AssertionError('Failure injection did not raise')
    finally:
        core._load_compiler = original_loader
    assert snapshot(doc) == before, 'Failed replacement changed the document'
    assert core.managed_schema_override(spacer, doc) == schema_before
    assert doc.getObject('PartialCompile') is None
    assert doc.UndoMode == original_undo_mode

    saved = out / 'managed-spacer.FCStd'
    doc.saveAs(str(saved))
    App.closeDocument(doc.Name)
    reopened = App.openDocument(str(saved))
    try:
        assert core.managed_schema_override(spacer, reopened)['thickness_in'] == 0.08
        assert snapshot(reopened) == before
        core.replace_managed_entry(spacer, reopened, {'thickness_in': 0.04})
        assert core.validate_managed_entry(spacer, reopened).passed
        assert len(snapshot(reopened)) == 2
    finally:
        App.closeDocument(reopened.Name)
    return {'passed': True, 'freecad_version': App.Version(), 'entries': results,
            'replacement_no_duplicates': True, 'unrelated_geometry_preserved': True,
            'failed_replacement_rolled_back': True, 'wrong_document_rejected': True,
            'edited_geometry_checked_against_expectations': True,
            'saved_document_binding_restored': True}


def main():
    output = Path(os.environ['OSE_REPORT_OUT']).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix='ose-wb-integration-') as tmp:
        root = Path(tmp) / 'vcs-library'
        # Validators write reports; keep the source checkout untouched.
        shutil.copytree(Path(os.environ['OSE_LIBRARY_ROOT']), root,
                        ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__',
                                                     'reports', 'out', 'web-dist', '.pytest_cache'))
        report = exercise(root, output.parent)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('OSE_WORKBENCH_INTEGRATION_PASSED', len(report['entries']), 'entries')


if os.environ.get('OSE_LIBRARY_ROOT'):
    try:
        main()
    except Exception:
        traceback.print_exc()
        Path(os.environ['OSE_REPORT_OUT']).write_text(json.dumps(
            {'passed': False, 'error': traceback.format_exc()}, indent=2) + '\n')
        raise
