# Companion notebooks

One notebook per lesson, with every code example from the lesson ready to run and an empty cell for each
hands-on exercise. Worked solutions live in `solutions/`, as complete notebooks you can run top to bottom.
Try each exercise before you open its solution.

The lesson pages tell you when to switch to the notebook: every exercise is labelled **At your computer**
and names the notebook cell, which has the same heading as the exercise.

## Run them on your computer

From this folder:

```bash
uv venv --python 3.12
uv pip install -r requirements.txt     # everything the course uses (PyTorch is the big one)
uv run jupyter lab
```

Or with plain pip: `python -m venv .venv`, activate it, `pip install -r requirements.txt`, then `jupyter lab`.
You do not have to install everything up front: each notebook starts with a setup cell that installs exactly
what that lesson needs.

PyTorch is large. On Colab it is already installed; locally you may prefer the install command from
pytorch.org for your operating system and GPU.

## Run them on Google Colab

Every notebook has an **Open in Colab** badge in its first cell, and every lesson page has the same link.
Or open colab.research.google.com, choose *File, Upload notebook*, and pick a notebook. For notebooks that
need a GPU (see the table), choose *Runtime, Change runtime type, GPU*. For lessons that call a model API,
add your key under the key icon (Secrets) as `ANTHROPIC_API_KEY` and uncomment the two Colab lines in the
setup cell.

## API keys

Put keys in a `.env` file in this folder (never in the notebook itself), as described in lesson 00. The
repository's `.gitignore` keeps `.env` out of Git.

```text
ANTHROPIC_API_KEY=sk-ant-...
```

## Reading the cell markers

Most cells run anywhere, offline, on a CPU. A cell whose first line is one of these comments needs that
resource:

| First line | Needs |
|---|---|
| `# Needs an API key` | a key for a hosted model in `.env` |
| `# Needs a GPU runtime` | an NVIDIA GPU, for example a free Colab T4 |
| `# Downloads a model or data on first run` | an internet connection the first time |
| `# Uses your own files` | files of your own, such as PDFs for the RAG lesson |

Everything else in the notebook still runs without them. Every unmarked cell is checked by running the
notebook top to bottom on a CPU with `python tools/check_notebooks.py`.

## Files the notebooks create

Some cells write files next to the notebook: downloaded datasets, model checkpoints, CSVs, small scripts.
They are yours to inspect and are ignored by Git, so they never end up in your commits.

## The notebooks

<!-- notebook-table:start -->
<!-- notebook-table:end -->
