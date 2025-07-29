"""Console script for planner."""
import sys
import os

try:
    # print(f"Trying to connect to a remote debugger..")
    sys.path.append(os.path.dirname(__file__))
    from . import wingdbstub
except Exception:
    print("Remote debugging is not found or configured... (waiting 5 secs)")
    # import time
    # time.sleep(5)

# import sys

# sys.exit(1)

# basic mycelium support
from pycelium.tools.cli.main import *

# from pycelium.tools.cli.config import config
# from pycelium.tools.cli.run import run

# import local submodules
# from pycelium.tools.cli.inventory import inventory


# import local submodules

from .inventory import inventory
from .plan import plan
from .run import run
from .workspaces import workspace

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
