# AI Engineering: from zero to mastery

A free, self-paced course that takes you from writing your first NumPy array to designing, evaluating and
shipping AI systems. Every lesson is a readable web page with an interactive quiz, and every lesson has a
Jupyter notebook with all of its code and hands-on exercises, plus worked solutions.

**Read it online:** <https://ashutoshjoshi1.github.io/AI-ZerotoMastery/> (see [Publishing the site](#publishing-the-site) to switch this on)

## How to use it

The course is built so you can **read on your phone and practise on your computer**.

| Where | What you do |
|---|---|
| Phone or tablet | Open the site and read a session. Add it to your home screen (Safari: *Share, Add to Home Screen*; Chrome: *Install app*) and lessons you open are kept for offline reading. The **Aa** button sets text size, typeface and theme. |
| Computer | Clone this repository, open the notebook with the lesson's number in JupyterLab or VS Code, and do the exercises marked **At your computer**. Each one names the notebook cell to use. |
| Both | Tick sessions as you finish them. Progress is stored per browser; the **Aa** panel gives you a sync link that carries your ticks to another device. |

Each lesson is split into one-hour sessions with a divider (and a checkbox) where each session ends.
The [daily schedule](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/schedule.html) lays the whole course out day by day.

## The course

<!-- lessons:start -->
33 lessons in 111 sessions of about an hour each: about 23 weeks at five sessions a week.

**Part I: Orientation.** Set up your workbench and see the whole map before you start walking.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 00 | [Welcome and your AI workbench](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/00-welcome.html) | 2 | [00-welcome.ipynb](notebooks/00-welcome.ipynb) |

**Part II: Foundations.** Python, numerical computing and the maths every later lesson leans on.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 01 | [Python for AI work](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/01-python-for-ai.html) | 3 | [01-python-for-ai.ipynb](notebooks/01-python-for-ai.ipynb) |
| 02 | [The maths behind AI](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/02-math-for-ai.html) | 4 | [02-math-for-ai.ipynb](notebooks/02-math-for-ai.ipynb) |

**Part III: Machine learning.** How models learn from data, and how to tell whether they really did.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 03 | [Machine learning fundamentals](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/03-ml-fundamentals.html) | 3 | [03-ml-fundamentals.ipynb](notebooks/03-ml-fundamentals.ipynb) |
| 04 | [Classical machine learning](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/04-classical-ml.html) | 4 | [04-classical-ml.ipynb](notebooks/04-classical-ml.ipynb) |

**Part IV: Deep learning.** Neural networks from first principles, then the same ideas in PyTorch.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 05 | [Neural networks from scratch](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/05-neural-networks.html) | 4 | [05-neural-networks.ipynb](notebooks/05-neural-networks.ipynb) |
| 06 | [Deep learning with PyTorch](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/06-pytorch.html) | 4 | [06-pytorch.ipynb](notebooks/06-pytorch.ipynb) |
| 07 | [Text as numbers, sequences and embeddings](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/07-sequences-embeddings.html) | 2 | [07-sequences-embeddings.ipynb](notebooks/07-sequences-embeddings.ipynb) |

**Part V: Transformers and LLMs.** Attention, the transformer block, and how large language models are made.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 08 | [Attention and the transformer](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/08-transformers.html) | 5 | [08-transformers.ipynb](notebooks/08-transformers.ipynb) |
| 09 | [How large language models are built](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/09-how-llms-are-built.html) | 4 | [09-how-llms-are-built.ipynb](notebooks/09-how-llms-are-built.ipynb) |

**Part VI: Building with LLMs.** The core craft: APIs, prompts, reasoning models, retrieval, agents, context engineering and evaluation.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 10 | [Working with LLM APIs](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/10-llm-apis.html) | 3 | [10-llm-apis.ipynb](notebooks/10-llm-apis.ipynb) |
| 11 | [Prompt engineering](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/11-prompt-engineering.html) | 3 | [11-prompt-engineering.ipynb](notebooks/11-prompt-engineering.ipynb) |
| 12 | [Reasoning models and test-time compute](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/12-reasoning-models.html) | 3 | [12-reasoning-models.ipynb](notebooks/12-reasoning-models.ipynb) |
| 13 | [Embeddings and vector search](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/13-embeddings-vector-search.html) | 3 | [13-embeddings-vector-search.ipynb](notebooks/13-embeddings-vector-search.ipynb) |
| 14 | [Retrieval-augmented generation (RAG)](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/14-rag.html) | 5 | [14-rag.ipynb](notebooks/14-rag.ipynb) |
| 15 | [Agents, tool use and MCP](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/15-agents.html) | 5 | [15-agents.ipynb](notebooks/15-agents.ipynb) |
| 16 | [Context engineering and memory](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/16-context-engineering.html) | 3 | [16-context-engineering.ipynb](notebooks/16-context-engineering.ipynb) |
| 17 | [Evaluating LLM systems](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/17-evaluation.html) | 3 | [17-evaluation.ipynb](notebooks/17-evaluation.ipynb) |

**Part VII: Fine-tuning and inference.** Change what a model knows and how it behaves, then make it fast and cheap to run: supervised fine-tuning, preference tuning and distillation, and the mechanics of LLM inference.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 18 | [Fine-tuning language models](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/18-fine-tuning.html) | 4 | [18-fine-tuning.ipynb](notebooks/18-fine-tuning.ipynb) |
| 19 | [Post-training in depth: data, preference tuning, RL fine-tuning, distillation and merging](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/19-advanced-fine-tuning.html) | 1 | [19-advanced-fine-tuning.ipynb](notebooks/19-advanced-fine-tuning.ipynb) |
| 20 | [LLM inference in depth](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/20-llm-inference.html) | 1 | [20-llm-inference.ipynb](notebooks/20-llm-inference.ipynb) |

**Part VIII: Production.** Serving, scaling, securing and extending AI systems in the real world.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 21 | [Deployment, serving and LLMOps](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/21-deployment-llmops.html) | 4 | [21-deployment-llmops.ipynb](notebooks/21-deployment-llmops.ipynb) |
| 22 | [Safety, security and responsible AI](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/22-safety-security.html) | 3 | [22-safety-security.ipynb](notebooks/22-safety-security.ipynb) |
| 23 | [Multimodal AI: vision, documents, speech and image generation](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/23-multimodal.html) | 3 | [23-multimodal.ipynb](notebooks/23-multimodal.ipynb) |

**Part IX: The wider field.** The rest of AI beyond language models: search and planning, reinforcement learning, generative models, vision, time series and graphs, training at scale, and interpretability. Each lesson stands on its own, so take them in order or pick the ones your work needs.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 24 | [Search, planning and classical AI](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/24-classical-ai.html) | 3 | [24-classical-ai.ipynb](notebooks/24-classical-ai.ipynb) |
| 25 | [Reinforcement learning](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/25-reinforcement-learning.html) | 4 | [25-reinforcement-learning.ipynb](notebooks/25-reinforcement-learning.ipynb) |
| 26 | [Generative models: autoencoders, VAEs, GANs, flows and diffusion](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/26-generative-models.html) | 3 | [26-generative-models.ipynb](notebooks/26-generative-models.ipynb) |
| 27 | [Computer vision: detection, segmentation and beyond](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/27-computer-vision.html) | 3 | [27-computer-vision.ipynb](notebooks/27-computer-vision.ipynb) |
| 28 | [Time series, recommender systems and graphs](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/28-time-series-recsys-graphs.html) | 4 | [28-time-series-recsys-graphs.ipynb](notebooks/28-time-series-recsys-graphs.ipynb) |
| 29 | [Training at scale: GPUs, parallelism and efficient architectures](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/29-training-at-scale.html) | 3 | [29-training-at-scale.ipynb](notebooks/29-training-at-scale.ipynb) |
| 30 | [Interpretability and explainability](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/30-interpretability.html) | 3 | [30-interpretability.ipynb](notebooks/30-interpretability.ipynb) |

**Part X: Mastery.** System design, capstone projects, and turning skill into a career.

| # | Lesson | Sessions | Notebook |
|---|---|---|---|
| 31 | [Designing AI systems](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/31-system-design.html) | 3 | [31-system-design.ipynb](notebooks/31-system-design.ipynb) |
| 32 | [Capstone projects and your AI engineering career](https://ashutoshjoshi1.github.io/AI-ZerotoMastery/lessons/32-capstones-career.html) | 6 | [32-capstones-career.ipynb](notebooks/32-capstones-career.ipynb) |
<!-- lessons:end -->

## Set up your computer for the notebooks

You need Python 3.11 or newer. With [uv](https://docs.astral.sh/uv/) (recommended):

```bash
git clone https://github.com/ashutoshjoshi1/AI-ZerotoMastery.git
cd AI-ZerotoMastery/notebooks
uv venv --python 3.12
uv pip install -r requirements.txt     # everything; or let each notebook's first cell install what it needs
uv run jupyter lab
```

Or with plain pip:

```bash
cd AI-ZerotoMastery/notebooks
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install jupyterlab numpy pandas matplotlib scikit-learn
jupyter lab
```

Lessons that call a hosted model need an API key in `notebooks/.env` (never in a notebook):

```text
ANTHROPIC_API_KEY=sk-ant-...
```

No setup, or no GPU? Every lesson page has an **Open in Colab** link. [notebooks/README.md](notebooks/README.md)
lists what each notebook needs (CPU, GPU, API key or a download).

## Publishing the site

The website is plain static HTML in this repository, so GitHub Pages can serve it as it is:

1. Push the repository to GitHub.
2. In the repository, open **Settings, Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, then **main** and **/ (root)**, and save.
4. After a minute the site is live at `https://<your-user>.github.io/AI-ZerotoMastery/`.

If you fork the course, change `repo` and `site_url` in `content/course.json` and rebuild, so the Colab and
sync links point at your copy.

You can also read it without any server: open `index.html` in a browser. Everything (fonts, maths, search)
is bundled; only offline caching and installing as an app need the hosted version.

## Editing the course

The pages are generated from sources in `content/`. Edit a lesson in `content/lessons/<slug>.html`, then rebuild:

```bash
pip install pygments                    # once
cd tools && npm install && cd ..        # once: installs KaTeX for the maths
python tools/build.py                   # regenerates every page, the search index and the notebook headers
python tools/check_notebooks.py --no-install notebooks/03-ml-fundamentals.ipynb   # runs a notebook top to bottom
```

[docs/AUTHORING.md](docs/AUTHORING.md) describes the source format: metadata, sessions, code, maths,
exercises, quizzes, figures and cross-references. Lesson numbers come from the order in
`content/course.json`, so you can insert or reorder lessons and every link and number updates.

## Repository layout

```text
index.html, lessons/, schedule.html,     the generated website (do not edit by hand)
glossary.html, resources.html, sw.js
content/                                 lesson and page sources, and the course structure
notebooks/                               one notebook per lesson
notebooks/solutions/                     the same notebooks with every exercise solved
assets/                                  styles, scripts, fonts, icons
tools/                                   the site builder and the notebook checker
docs/AUTHORING.md                        how to write and edit lessons
```
