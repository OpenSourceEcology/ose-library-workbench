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
            root = Path(directory).resolve()
            entries = core.open_library(root)
            state.library_root = root
            state.entries = entries
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
            core.compile_managed_entry(entry, doc, state.schema_override)
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
        try:
            doc = App.ActiveDocument
            schema = core.managed_schema_override(entry, doc)
            dialog = ParameterDialog(entry, Gui.getMainWindow(), schema_override=schema)
            if dialog.exec_() and dialog.applied_schema is not None:
                core.replace_managed_entry(entry, doc, dialog.applied_schema)
                state.schema_override = dialog.applied_schema
                if Gui.ActiveDocument is not None:
                    Gui.SendMsgToActiveView("ViewFit")
        except Exception as exc:
            _error("Edit Parameters Failed", exc)

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
            report = core.validate_managed_entry(entry, doc)
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
