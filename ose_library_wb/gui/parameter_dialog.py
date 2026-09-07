from __future__ import annotations

from copy import deepcopy

from PySide import QtGui

from libtools.registry import load_schema

from ose_library_wb import core


class ParameterDialog(QtGui.QDialog):
    def __init__(self, entry, parent=None, schema_override=None):
        super().__init__(parent)
        self.entry = entry
        self.schema = load_schema(entry)
        if schema_override:
            self.schema = _deep_merge(self.schema, schema_override)
        self.applied_schema = None
        self.widgets = {}

        self.setWindowTitle(f"Edit Parameters: {entry.id}")
        root = QtGui.QVBoxLayout(self)
        self.form = QtGui.QFormLayout()
        root.addLayout(self.form)
        self._add_fields(self.schema)

        note = QtGui.QLabel(
            "Save writes schema.py.new next to schema.py; merge changes by hand."
        )
        note.setWordWrap(True)
        root.addWidget(note)

        buttons = QtGui.QDialogButtonBox()
        self.apply_button = buttons.addButton("Apply", QtGui.QDialogButtonBox.ApplyRole)
        self.export_button = buttons.addButton(
            "Export changed schema...", QtGui.QDialogButtonBox.AcceptRole
        )
        buttons.addButton(QtGui.QDialogButtonBox.Close)
        root.addWidget(buttons)

        self.apply_button.clicked.connect(self.apply_changes)
        self.export_button.clicked.connect(self.export_changes)
        buttons.rejected.connect(self.reject)

    def edited_schema(self):
        edited = deepcopy(self.schema)
        for path, widget in self.widgets.items():
            _set_path(edited, path, _widget_value(widget))
        return edited

    def apply_changes(self):
        self.applied_schema = self.edited_schema()
        self.accept()

    def export_changes(self):
        core.export_schema_new(self.entry, self.edited_schema())
        self.accept()

    def _add_fields(self, data, prefix=()):
        for key, value in data.items():
            path = (*prefix, key)
            label = ".".join(path)
            if isinstance(value, dict):
                group = QtGui.QGroupBox(label)
                layout = QtGui.QFormLayout(group)
                old_form = self.form
                self.form.addRow(group)
                self.form = layout
                self._add_fields(value, path)
                self.form = old_form
            elif isinstance(value, bool):
                widget = QtGui.QCheckBox()
                widget.setChecked(value)
                self.widgets[path] = widget
                self.form.addRow(label, widget)
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                widget = QtGui.QDoubleSpinBox()
                widget.setDecimals(4)
                widget.setRange(-1000000.0, 1000000.0)
                widget.setValue(float(value))
                self.widgets[path] = widget
                self.form.addRow(label, widget)
            elif isinstance(value, str):
                widget = QtGui.QLineEdit(value)
                if path in {("schema_name",), ("document_name",), ("units",)}:
                    widget.setReadOnly(True)
                else:
                    self.widgets[path] = widget
                self.form.addRow(label, widget)
            elif isinstance(value, list):
                widget = QtGui.QLineEdit(repr(value))
                widget.setReadOnly(True)
                self.form.addRow(label, widget)


def _widget_value(widget):
    if isinstance(widget, QtGui.QCheckBox):
        return widget.isChecked()
    if isinstance(widget, QtGui.QDoubleSpinBox):
        value = widget.value()
        return int(value) if value.is_integer() else value
    if isinstance(widget, QtGui.QLineEdit):
        return widget.text()
    return None


def _set_path(data, path, value):
    cursor = data
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value


def _deep_merge(base, override):
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged
