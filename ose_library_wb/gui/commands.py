from __future__ import annotations

from pathlib import Path
import traceback

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from ose_library_wb import core
from . import state
from .entry_tree import refresh_entries
from .parameter_dialog import ParameterDialog
from .validation_panel import show_report


def register():
    Gui.addCommand("OSE_OpenLibrary", OpenLibraryCommand())
    Gui.addCommand("OSE_CompileEntry", CompileEntryCommand())
    Gui.addCommand("OSE_EditParameters", EditParametersCommand())
    Gui.addCommand("OSE_ValidateEntry", ValidateEntryCommand())


class OpenLibraryCommand:
    def GetResources(self):
        return {
            "MenuText": "Open Library",
            "ToolTip": "Open a Schema Canon library checkout",
        }

    def Activated(self):
        directory = QtGui.QFileDialog.getExistingDirectory(
            Gui.getMainWindow(), "Open OSE Library"
        )
        if not directory:
            return
        try:
            state.library_root = Path(directory)
            state.entries = core.open_library(state.library_root)
            state.selected_entry_id = None
            state.schema_override = None
            refresh_entries()
        except Exception as exc:
            _error("Open Library Failed", exc)

    def IsActive(self):
        return True


class CompileEntryCommand:
    def GetResources(self):
        return {
            "MenuText": "Compile Entry",
            "ToolTip": "Compile the selected entry into a new document",
        }

    def Activated(self):
        entry = state.selected_entry()
        if entry is None:
            _message("Select an entry first.")
            return
        try:
            doc = App.newDocument(entry.meta.get("title", entry.id).replace(" ", "_"))
            core.compile_entry_into(entry, doc, state.schema_override)
            doc.recompute()
            if Gui.ActiveDocument is not None:
                Gui.SendMsgToActiveView("ViewFit")
        except Exception as exc:
            _error("Compile Entry Failed", exc)

    def IsActive(self):
        return state.selected_entry() is not None


class EditParametersCommand:
    def GetResources(self):
        return {
            "MenuText": "Edit Parameters",
            "ToolTip": "Edit schema parameters for the selected entry",
        }

    def Activated(self):
        entry = state.selected_entry()
        if entry is None:
            _message("Select an entry first.")
            return
        dialog = ParameterDialog(entry, Gui.getMainWindow())
        if dialog.exec_():
            doc = App.ActiveDocument
            if doc is not None and state.schema_override:
                core.compile_entry_into(entry, doc, state.schema_override)
                doc.recompute()
                if Gui.ActiveDocument is not None:
                    Gui.SendMsgToActiveView("ViewFit")

    def IsActive(self):
        return state.selected_entry() is not None


class ValidateEntryCommand:
    def GetResources(self):
        return {
            "MenuText": "Validate Entry",
            "ToolTip": "Validate code and live output for the selected entry",
        }

    def Activated(self):
        entry = state.selected_entry()
        doc = App.ActiveDocument
        if entry is None:
            _message("Select an entry first.")
            return
        if doc is None:
            _message("Compile the entry into a document first.")
            return
        try:
            report = core.validate_live(entry, doc)
            show_report(report)
            refresh_entries()
        except Exception as exc:
            _error("Validate Entry Failed", exc)

    def IsActive(self):
        return state.selected_entry() is not None


def _message(text):
    QtGui.QMessageBox.information(Gui.getMainWindow(), "OSE Library", text)


def _error(title, exc):
    QtGui.QMessageBox.critical(
        Gui.getMainWindow(), title, f"{exc}\n\n{traceback.format_exc()}"
    )
