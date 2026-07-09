from __future__ import annotations

import json
import os
import sys
from pathlib import Path


workspace = Path(os.environ["OSE_WB_ROOT"]).resolve()
library_root = Path(os.environ["OSE_LIBRARY_ROOT"]).resolve()
for path in (workspace, library_root):
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)

import FreeCAD as App

from ose_library_wb import core


def main():
    import ose_library_wb
    import ose_library_wb.core

    entries = core.open_library(library_root)
    entry = {candidate.id: candidate for candidate in entries}["extwall_standard"]
    doc = App.newDocument("ExtWallStandard")
    core.compile_entry_into(entry, doc)
    doc.recompute()
    report = core.validate_live(entry, doc)
    assert report.passed is True

    out = Path(os.environ["OSE_REPORT_OUT"])
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "id": report.id,
        "layer": report.layer,
        "status": report.status,
        "tier": report.tier,
        "checks": [
            {"name": check.name, "passed": check.passed, "detail": check.detail}
            for check in report.checks
        ],
        "passed": report.passed,
    }
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if os.environ.get("OSE_LIBRARY_ROOT"):
    main()
