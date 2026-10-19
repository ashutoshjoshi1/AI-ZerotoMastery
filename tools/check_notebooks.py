"""Run course notebooks top to bottom and report any cell that fails.

Cells whose first line is one of the resource markers below are skipped unless you opt in,
because they need something a plain laptop may not have:

    # Needs an API key                          --run-api
    # Needs a GPU runtime                       --run-gpu
    # Downloads a model or data on first run    --run-downloads
    # Uses your own files                       (always skipped)

`%pip install` lines are skipped with --no-install, for an environment that already has the packages.

Usage:
    python tools/check_notebooks.py notebooks/03-ml-fundamentals.ipynb
    python tools/check_notebooks.py --no-install --run-downloads notebooks/*.ipynb notebooks/solutions/*.ipynb

Needs: pip install nbclient nbformat ipykernel
"""
import argparse
import asyncio
import copy
import glob
import os
import sys
import time

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError, CellTimeoutError

MARKERS = {
    "# needs an api key": "api",
    "# needs a gpu runtime": "gpu",
    "# downloads a model or data on first run": "downloads",
    "# uses your own files": "files",
}


def marker_of(source):
    first = source.lstrip().split("\n", 1)[0].strip().lower()
    for prefix, kind in MARKERS.items():
        if first.startswith(prefix):
            return kind
    return None


def check(path, args):
    nb = nbformat.read(path, as_version=4)
    run = copy.deepcopy(nb)
    skipped = []
    for i, cell in enumerate(run.cells):
        if cell.cell_type != "code":
            continue
        kind = marker_of(cell.source)
        if kind and not getattr(args, "run_" + kind, False):
            skipped.append(i)
            cell.source = "pass  # skipped by check_notebooks: " + kind
        elif args.no_install:
            cell.source = "\n".join(
                "pass  # skipped install" if line.lstrip().startswith(("%pip", "!pip")) else line
                for line in cell.source.split("\n")
            )
    workdir = args.cwd or os.path.dirname(path) or "."
    client = NotebookClient(run, timeout=args.timeout, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": workdir}})
    start = time.time()
    try:
        client.execute()
    except (CellExecutionError, CellTimeoutError) as e:
        print(f"  ! {path}: {type(e).__name__}: {str(e)[:300]}")
    failures = []
    for i, cell in enumerate(run.cells):
        if cell.cell_type != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                after_skip = any(s < i for s in skipped)
                failures.append((i, out.get("ename"), out.get("evalue", "")[:200], after_skip))
                break
    took = time.time() - start
    status = "ok" if not failures else f"{len(failures)} failing cell(s)"
    print(f"{path}: {status} in {took:.0f}s, {len(skipped)} marked cell(s) skipped")
    for i, ename, evalue, after_skip in failures:
        hint = "  (after a skipped cell: may depend on it)" if after_skip else ""
        print(f"    cell {i}: {ename}: {evalue}{hint}")
    return not failures


def main():
    if sys.platform == "win32":  # zmq needs a selector event loop on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("paths", nargs="+")
    p.add_argument("--run-api", action="store_true")
    p.add_argument("--run-gpu", action="store_true")
    p.add_argument("--run-downloads", action="store_true")
    p.add_argument("--no-install", action="store_true")
    p.add_argument("--timeout", type=int, default=600, help="seconds allowed per cell")
    p.add_argument("--cwd", help="working directory for the kernel (default: the notebook's folder)")
    args = p.parse_args()
    paths = sorted({f for pattern in args.paths for f in glob.glob(pattern)})
    ok = all([check(path.replace("\\", "/"), args) for path in paths])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
