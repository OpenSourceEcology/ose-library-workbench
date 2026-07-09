from __future__ import annotations

import json
import sys
from pathlib import Path


def main(path: str) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert data["id"] == "extwall_standard"
    assert data["layer"] == "module"
    assert data["status"] in {"active", "wip"}
    assert data["tier"] == "code+output"
    assert data["passed"] is True
    assert isinstance(data["checks"], list) and data["checks"]
    for check in data["checks"]:
        assert isinstance(check["name"], str) and check["name"]
        assert isinstance(check["passed"], bool)
        assert isinstance(check.get("detail", ""), str)
    assert any(check["name"].startswith("code:") for check in data["checks"])
    assert any(check["name"].startswith("output:") for check in data["checks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
