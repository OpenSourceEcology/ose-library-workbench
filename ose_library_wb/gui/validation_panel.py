from __future__ import annotations

from PySide import QtCore, QtGui
import FreeCADGui as Gui


_dock = None
_table = None


def ensure_validation_panel():
    global _dock, _table
    if _dock is not None:
        return _dock

    mw = Gui.getMainWindow()
    _dock = QtGui.QDockWidget("OSE Validation", mw)
    _table = QtGui.QTableWidget(0, 3)
    _table.setHorizontalHeaderLabels(["Check", "Result", "Detail"])
    _table.horizontalHeader().setStretchLastSection(True)
    _dock.setWidget(_table)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, _dock)
    return _dock


def show_report(report):
    ensure_validation_panel()
    _table.setRowCount(len(report.checks))
    for row, check in enumerate(report.checks):
        _table.setItem(row, 0, QtGui.QTableWidgetItem(check.name))
        _table.setItem(row, 1, QtGui.QTableWidgetItem("PASS" if check.passed else "FAIL"))
        _table.setItem(row, 2, QtGui.QTableWidgetItem(check.detail))
    _dock.show()
    _dock.raise_()
