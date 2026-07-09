from __future__ import annotations

from PySide import QtCore, QtGui
import FreeCADGui as Gui

from ose_library_wb import core
from . import state


_dock = None
_tree = None


def ensure_entry_tree():
    global _dock, _tree
    if _dock is not None:
        return _dock

    mw = Gui.getMainWindow()
    _dock = QtGui.QDockWidget("OSE Library Entries", mw)
    _tree = QtGui.QTreeWidget()
    _tree.setColumnCount(6)
    _tree.setHeaderLabels(["Layer", "ID", "Title", "Owner", "Status", "Last"])
    _tree.itemSelectionChanged.connect(_selection_changed)
    _dock.setWidget(_tree)
    mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea, _dock)
    return _dock


def refresh_entries():
    ensure_entry_tree()
    _tree.clear()

    groups = {}
    for entry in state.entries:
        groups.setdefault(entry.layer, []).append(entry)

    for layer, entries in sorted(groups.items()):
        parent = QtGui.QTreeWidgetItem([layer, "", "", "", "", ""])
        _tree.addTopLevelItem(parent)
        for entry in entries:
            last = ""
            if state.library_root is not None:
                report = core.latest_report(state.library_root, entry.id)
                if report is not None:
                    last = "PASS" if report.get("passed") else "FAIL"
            child = QtGui.QTreeWidgetItem(
                [
                    "",
                    entry.id,
                    str(entry.meta.get("title", "")),
                    str(entry.meta.get("owner", "")),
                    entry.status,
                    last,
                ]
            )
            child.setData(0, QtCore.Qt.UserRole, entry.id)
            parent.addChild(child)
        parent.setExpanded(True)

    for column in range(_tree.columnCount()):
        _tree.resizeColumnToContents(column)


def _selection_changed():
    items = _tree.selectedItems() if _tree is not None else []
    if not items:
        state.selected_entry_id = None
        return
    state.selected_entry_id = items[0].data(0, QtCore.Qt.UserRole)
    state.schema_override = None
