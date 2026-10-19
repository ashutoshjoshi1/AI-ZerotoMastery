# Companion notebooks

One notebook per lesson, with every code example from the lesson ready to run, plus empty cells for each
hands-on exercise. Worked solutions live in `solutions/`, as complete notebooks you can run top to bottom.
Try each exercise before you open its solution.

## Run them on your computer

From the folder that contains this README (or after copying the notebooks into your own learning-log repository):

```bash
uv init --python 3.12          # once, if this folder is not already a uv project
uv add jupyterlab numpy pandas matplotlib scikit-learn python-dotenv
uv run jupyter lab
```

Or with plain pip: `python3 -m venv .venv`, activate it, `pip install -r requirements.txt`, then `jupyter lab`.
Each notebook starts with a setup cell that installs exactly what that lesson needs, so you can also install as you go.

## Run them on Google Colab

Open colab.research.google.com, choose File > Upload notebook, and pick a notebook. For lessons that need
a GPU (06, 08, 16 and the image-generation part of 19), choose Runtime > Change runtime type > GPU.
For lessons that call a model API, add your key under the key icon (Secrets) as `ANTHROPIC_API_KEY`
and uncomment the two Colab lines in the setup cell.

## API keys

Put keys in a `.env` file next to the notebooks (never in the notebook itself), as described in lesson 00:

```text
ANTHROPIC_API_KEY=sk-ant-...
```

## Reading the cell markers

Most cells run anywhere, offline, on a CPU. A cell whose first line is a comment such as
`# Needs an API key`, `# Needs a GPU runtime`, `# Downloads a model or data on first run`
or `# Uses your own files` needs that resource; everything above it in the notebook still runs without it.
Every cell without such a marker was executed from top to bottom when the course was built.

## The notebooks

| Notebook | Lesson | Runs on |
|---|---|---|
| [00-welcome.ipynb](00-welcome.ipynb) | Welcome and your AI workbench | Any computer (CPU). |
| [01-python-for-ai.ipynb](01-python-for-ai.ipynb) | Python for AI work | Any computer (CPU). |
| [02-math-for-ai.ipynb](02-math-for-ai.ipynb) | The maths behind AI | Any computer (CPU). |
| [03-ml-fundamentals.ipynb](03-ml-fundamentals.ipynb) | Machine learning fundamentals | Any computer (CPU). |
| [04-classical-ml.ipynb](04-classical-ml.ipynb) | Classical machine learning | Any computer (CPU). The cross-validation cells take a minute. |
| [05-neural-networks.ipynb](05-neural-networks.ipynb) | Neural networks from scratch | Any computer (CPU). |
| [06-pytorch.ipynb](06-pytorch.ipynb) | Deep learning with PyTorch | CPU works; a GPU runtime (for example Google Colab) makes the CNN sections much faster. |
| [07-sequences-embeddings.ipynb](07-sequences-embeddings.ipynb) | Text as numbers, sequences and embeddings | Any computer (CPU). The last cells use PyTorch. |
| [08-transformers.ipynb](08-transformers.ipynb) | Attention and the transformer | The NumPy sections run anywhere. Training the tiny GPT takes minutes on a GPU and much longer on a CPU. |
| [09-how-llms-are-built.ipynb](09-how-llms-are-built.ipynb) | How large language models are built | Any computer (CPU). |
| [10-llm-apis.ipynb](10-llm-apis.ipynb) | Working with LLM APIs | Any computer, plus an API key. Cells that call a model are marked. |
| [11-prompt-engineering.ipynb](11-prompt-engineering.ipynb) | Prompt engineering | Any computer, plus an API key. |
| [12-embeddings-vector-search.ipynb](12-embeddings-vector-search.ipynb) | Embeddings and vector search | Any computer (CPU). The first run downloads a small embedding model (about 90 MB). |
| [13-rag.ipynb](13-rag.ipynb) | Retrieval-augmented generation (RAG) | Any computer (CPU). Retrieval downloads two small models; generating answers needs an API key. |
| [14-agents.ipynb](14-agents.ipynb) | Agents, tool use and MCP | Any computer, plus an API key for the agent loop. |
| [15-evaluation.ipynb](15-evaluation.ipynb) | Evaluating LLM systems | Any computer (CPU). Only the LLM-judge cells need an API key. |
| [16-fine-tuning.ipynb](16-fine-tuning.ipynb) | Fine-tuning language models | A GPU runtime (a free Colab T4 is enough for the 0.5B model). The LoRA-from-scratch cell runs on CPU. |
| [17-deployment-llmops.ipynb](17-deployment-llmops.ipynb) | Deployment, serving and LLMOps | Any computer (CPU). Running the service needs an API key and a terminal. |
| [18-safety-security.ipynb](18-safety-security.ipynb) | Safety, security and responsible AI | Any computer (CPU). No API key needed. |
| [19-multimodal.ipynb](19-multimodal.ipynb) | Multimodal AI: vision, documents, speech and image generation | CPU for most cells; an API key for the vision-language model; a GPU for image generation. |
| [20-system-design.ipynb](20-system-design.ipynb) | Designing AI systems | Any computer. This notebook is a design-document workbook. |
| [21-capstones-career.ipynb](21-capstones-career.ipynb) | Capstone projects and your AI engineering career | Any computer. This notebook is a capstone workbook. |
