import os
import sys
from importlib.metadata import version, PackageNotFoundError

from dotenv import load_dotenv

load_dotenv()
print(f"Python {sys.version.split()[0]}")
for pkg in ["numpy", "pandas", "scikit-learn", "matplotlib", "jupyterlab"]:
    try:
        print(f"{pkg:<14}{version(pkg)}")
    except PackageNotFoundError:
        print(f"{pkg:<14}MISSING: install it with uv add {pkg}")

for var in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
    status = "present" if os.environ.get(var) else "not set (fine until part VI)"
    print(f"{var:<20}{status}")
