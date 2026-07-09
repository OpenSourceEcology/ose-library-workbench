from __future__ import annotations

from pathlib import Path

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui


class OSELibraryWorkbench(Gui.Workbench):
    MenuText = "OSE Library"
    ToolTip = "Author and validate OSE Schema Canon libraries"
    Icon = str(Path(__file__).resolve().parents[2] / "resources" / "ose_library_wb.svg")

    def Initialize(self):
        from . import commands

        commands.register()
        command_names = [
            "OSE_OpenLibrary",
            "OSE_CompileEntry",
            "OSE_EditParameters",
            "OSE_ValidateEntry",
        ]
        self.appendToolbar("OSE Library", command_names)
        self.appendMenu("OSE Library", command_names)

    def Activated(self):
        from .entry_tree import ensure_entry_tree
        from .validation_panel import ensure_validation_panel

        if _freecad_major() < 1:
            QtGui.QMessageBox.warning(
                Gui.getMainWindow(),
                "OSE Library",
                "OSE Library Workbench targets FreeCAD 1.x. FreeCAD 0.21 may not support every workflow.",
            )
        ensure_entry_tree()
        ensure_validation_panel()

    def GetClassName(self):
        return "Gui::PythonWorkbench"


def _freecad_major():
    try:
        return int(App.Version()[0])
    except Exception:
        return 0
