"""Check the GUI receipt even when FreeCAD reports a successful process exit."""
import json
from pathlib import Path
import sys

report = json.loads(Path(sys.argv[1]).read_text())
for name in ['passed', 'parameter_dialog', 'compile_command', 'apply_changes',
             'failed_edit_preserved_geometry', 'export_does_not_recompile',
             'wrong_document_rejected', 'validation_command']:
    assert report.get(name) is True, report
print('Verified FreeCAD GUI integration report')
