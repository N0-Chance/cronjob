import sys
import os
import traceback
from pathlib import Path

# Ensure src is in sys.path regardless of launch context
try:
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[2]  # /src/gui/ → /project/
    sys.path.insert(0, str(project_root))
except Exception as e:
    # Log any failure to adjust sys.path
    with open("launch_sys_path_fail.log", "w") as f:
        traceback.print_exc(file=f)

# Attempt to run GUI
try:
    from src.gui import run_gui
    run_gui()
except Exception:
    with open("gui_crash.log", "w") as f:
        f.write("Failed to launch GUI:\n\n")
        traceback.print_exc(file=f)
