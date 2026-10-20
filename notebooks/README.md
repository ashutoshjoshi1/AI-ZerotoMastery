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
| Notebook | Lesson | Runs on |
|---|---|---|
| [00-welcome.ipynb](00-welcome.ipynb) | Welcome and your AI workbench | Any computer (CPU). No API key needed; the key-loading cell simply reports that none is set. |
| [01-python-for-ai.ipynb](01-python-for-ai.ipynb) | Python for AI work | Any computer (CPU). |
| [02-math-for-ai.ipynb](02-math-for-ai.ipynb) | The maths behind AI | Any computer (CPU). |
| [03-ml-fundamentals.ipynb](03-ml-fundamentals.ipynb) | Machine learning fundamentals | Any computer (CPU). |
| [04-classical-ml.ipynb](04-classical-ml.ipynb) | Classical machine learning | Any computer (CPU). The cross-validation cells take a minute. |
| [05-neural-networks.ipynb](05-neural-networks.ipynb) | Neural networks from scratch | Any computer (CPU). |
| [06-pytorch.ipynb](06-pytorch.ipynb) | Deep learning with PyTorch | CPU works; a GPU runtime (for example Google Colab) makes the CNN sections much faster. |
| [07-sequences-embeddings.ipynb](07-sequences-embeddings.ipynb) | Text as numbers, sequences and embeddings | Any computer (CPU). The last cells use PyTorch. |
| [08-transformers.ipynb](08-transformers.ipynb) | Attention and the transformer | The NumPy sections run anywhere. Training the tiny GPT takes minutes on a GPU and much longer on a CPU. |
| [09-how-llms-are-built.ipynb](09-how-llms-are-built.ipynb) | How large language models are built | Any computer (CPU). |
| [10-llm-apis.ipynb](10-llm-apis.ipynb) | Working with LLM APIs | Any computer. Cells that call a hosted model are marked and need an API key; the helpers and the fake-client exercises run offline. |
| [11-prompt-engineering.ipynb](11-prompt-engineering.ipynb) | Prompt engineering | Any computer. The prompt linter, chaining and voting exercises run offline against a scripted model; cells that call a real model are marked and need an API key. |
| [12-reasoning-models.ipynb](12-reasoning-models.ipynb) | Reasoning models and test-time compute | Any computer (CPU) for the simulations. Cells that call a model need an API key and are marked. |
| [13-embeddings-vector-search.ipynb](13-embeddings-vector-search.ipynb) | Embeddings and vector search | Any computer (CPU). The first run downloads a small embedding model (about 90 MB); the ANN benchmark runs on synthetic data without any download. |
| [14-rag.ipynb](14-rag.ipynb) | Retrieval-augmented generation (RAG) | Any computer (CPU). Retrieval downloads two small models; generating answers needs an API key. |
| [15-agents.ipynb](15-agents.ipynb) | Agents, tool use and MCP | Any computer, plus an API key for the agent loop. |
| [16-context-engineering.ipynb](16-context-engineering.ipynb) | Context engineering and memory | Any computer (CPU). Everything runs offline with fake models; cells that call a real model are marked and need an API key. |
| [17-evaluation.ipynb](17-evaluation.ipynb) | Evaluating LLM systems | Any computer (CPU). Only the LLM-judge cells need an API key; the final exercise also uses your RAG system from the RAG lesson. |
| [18-fine-tuning.ipynb](18-fine-tuning.ipynb) | Fine-tuning language models | A GPU runtime (a free Colab T4 is enough for the 0.5B model) for the training cells. The LoRA-from-scratch code, the data generation, the memory calculator and the baseline exercises run on any CPU. |
| [19-advanced-fine-tuning.ipynb](19-advanced-fine-tuning.ipynb) | Post-training in depth: data, preference tuning, RL fine-tuning, distillation and merging | Any computer (CPU). The full notebook is coming with the full lesson. |
| [20-llm-inference.ipynb](20-llm-inference.ipynb) | LLM inference in depth | Any computer (CPU). The full notebook is coming with the full lesson. |
| [21-deployment-llmops.ipynb](21-deployment-llmops.ipynb) | Deployment, serving and LLMOps | Any computer (CPU). Running the live service needs an API key and a terminal; every notebook exercise runs offline. |
| [22-safety-security.ipynb](22-safety-security.ipynb) | Safety, security and responsible AI | Any computer (CPU). No API key needed. |
| [23-multimodal.ipynb](23-multimodal.ipynb) | Multimodal AI: vision, documents, speech and image generation | CPU for most cells; an API key for the vision-language model; a GPU for image generation. |
| [24-classical-ai.ipynb](24-classical-ai.ipynb) | Search, planning and classical AI | Any computer (CPU), offline. Uses only the Python standard library, NumPy and scikit-learn; every cell finishes in a few seconds. |
| [25-reinforcement-learning.ipynb](25-reinforcement-learning.ipynb) | Reinforcement learning | Any computer (CPU), offline. Needs numpy, matplotlib, torch and gymnasium; the notebook runs in a few minutes. |
| [26-generative-models.ipynb](26-generative-models.ipynb) | Generative models: autoencoders, VAEs, GANs, flows and diffusion | Any computer (CPU), offline. Uses scikit-learn's bundled digits dataset and generated 2-D data; each training cell finishes in under a minute. |
| [27-computer-vision.ipynb](27-computer-vision.ipynb) | Computer vision: detection, segmentation and beyond | Any computer (CPU), offline. The detector and the U-Net each train in about a minute on a laptop CPU; one optional cell downloads a 74 MB pretrained detector. |
| [28-time-series-recsys-graphs.ipynb](28-time-series-recsys-graphs.ipynb) | Time series, recommender systems and graphs | Any computer (CPU), offline: the data ships with statsmodels and networkx or is generated in code. One optional cell downloads MovieLens 100k (5 MB). The whole notebook runs in a few minutes. |
| [29-training-at-scale.ipynb](29-training-at-scale.ipynb) | Training at scale: GPUs, parallelism and efficient architectures | Any computer (CPU). Everything is measured or simulated at small scale; one optional cell uses a GPU if you have one. The notebook runs in a few minutes. |
| [30-interpretability.ipynb](30-interpretability.ipynb) | Interpretability and explainability | Any computer (CPU), offline. The whole notebook runs in about a minute. Two optional cells download the shap library and GPT-2 small. |
| [31-system-design.ipynb](31-system-design.ipynb) | Designing AI systems | Any computer (CPU). This notebook is a design-document workbook with a few small calculations. |
| [32-capstones-career.ipynb](32-capstones-career.ipynb) | Capstone projects and your AI engineering career | Any computer (CPU) for this workbook. The capstones themselves may need an API key or a GPU, as each specification says. |
<!-- notebook-table:end -->
