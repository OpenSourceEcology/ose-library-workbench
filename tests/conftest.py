from __future__ import annotations

import sys
from pathlib import Path


LOCAL_VCS_LIBRARY = Path("/Users/cct/code/vcs-library")
if LOCAL_VCS_LIBRARY.is_dir() and str(LOCAL_VCS_LIBRARY) not in sys.path:
    sys.path.insert(0, str(LOCAL_VCS_LIBRARY))
