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
