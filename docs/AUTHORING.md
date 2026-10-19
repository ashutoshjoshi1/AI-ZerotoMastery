# Writing and editing lessons

The website is generated. You edit the sources in `content/`, run the build, and it writes every page
(`index.html`, `lessons/*.html`, `schedule.html`, `glossary.html`, `resources.html`), the search index,
the offline cache list and the header cell of every notebook.

```bash
python tools/build.py            # rebuild the whole site
python tools/build.py --check    # rebuild into a temporary folder and fail if the committed site is stale
```

The build needs Python 3.10+ with `pygments`, and Node.js 18+ with KaTeX installed once in `tools/`
(`cd tools && npm install`). See the README for details.

## Where things live

| Path | What it is |
|---|---|
| `content/course.json` | Site settings, the parts, and the order of lessons. Lesson numbers come from this order. |
| `content/lessons/<slug>.html` | One lesson: a metadata block, then the lesson body. |
| `content/pages/*.html` | Bodies of the home, resources and other standalone pages. |
| `notebooks/NN-<slug>.ipynb` | The companion notebook. `NN` must match the lesson number. |
| `notebooks/solutions/NN-<slug>-solutions.ipynb` | The same notebook with every exercise solved. |
| `assets/` | Styles, scripts and fonts. Hand-written, not generated. |

## A lesson file

A lesson file starts with a JSON metadata block inside an HTML comment, followed by the body:

```html
<!--
{
  "title": "Reinforcement learning",
  "short": "Reinforcement learning",
  "summary": "One or two sentences that say what the learner will be able to do after this lesson.",
  "sessions": [
    "Agents, rewards and the exploration problem: multi-armed bandits",
    "Markov decision processes, value iteration and Q-learning",
    "Deep RL: DQN, policy gradients and PPO"
  ],
  "objectives": [
    "Explain the agent-environment loop and why exploration is necessary",
    "Implement tabular Q-learning and tune it on a gridworld"
  ],
  "prerequisites": ["neural-networks", "pytorch"],
  "runs_on": "Any computer (CPU). Every cell finishes in under a minute.",
  "glossary": [
    {"term": "Policy", "def": "The rule an agent uses to choose an action in each state."}
  ]
}
-->
<h2>The idea in one paragraph</h2>
<p>...</p>
```

| Key | Meaning |
|---|---|
| `title` | Full lesson title, shown as the page heading. |
| `short` | Short label for the sidebar (about 25 characters at most). |
| `summary` | Shown under the title, on the home page and in the notebook header. |
| `sessions` | One title per sitting of about an hour. The count drives progress tracking and the schedule. |
| `objectives` | Three to six things the learner will be able to do, each starting with a verb. |
| `prerequisites` | Slugs of earlier lessons the reader should have done. |
| `runs_on` | What the notebook needs (CPU, GPU, API key, downloads). |
| `glossary` | Terms this lesson introduces. They are merged into the course glossary, linked back here. |

## The body

Write plain HTML. The build adds heading ids, anchor links, syntax highlighting, maths, the table of
contents, session dividers and quiz behaviour, so the source stays short and readable.

### Headings and sessions

Use `<h2>` for sections and `<h3>` for subsections. Never `<h1>` (the title comes from the metadata).

Mark where each session after the first begins with `<hr data-session="2">`, `<hr data-session="3">` and
so on, just before the heading that starts it. The build turns each marker into a divider with a
checkbox for the session that just ended, so a reader always has a clear place to stop.

### Prose

Short paragraphs. One idea per paragraph. Define a term in **bold** the first time it appears. Prefer a
concrete example to an abstract sentence. British spelling (the rest of the course uses it): "optimise",
"behaviour", "modelling". Avoid em dashes; use commas, colons or full stops.

### Code

```html
<pre><code class="language-python">import numpy as np
x = np.arange(5)
print(x * 2)</code></pre>
<pre><code class="language-text">[0 2 4 6 8]</code></pre>
```

* Escape `<`, `>` and `&` inside code as `&lt;`, `&gt;`, `&amp;`.
* Languages: `python`, `bash`, `console`, `text`, `json`, `toml`, `yaml`, `html`, `javascript`, `sql`,
  `dockerfile`, `ini`, `diff`. Use `text` for program output, placed right after the code that printed it.
* Add `data-file="app.py"` to `<pre>` to label a block with a file name.
* Keep lines under about 80 characters where you can; long lines scroll on phones.
* Every code block in a lesson must also appear, in the same order and under the same headings, in the
  lesson's notebook.

### Maths

Inline maths is `\( ... \)` and display maths is `\[ ... \]`, written in TeX and rendered by KaTeX at build
time. Do not put maths inside code blocks. Inside an HTML file you may write `<` in TeX as `&lt;`.

### Cross-references to other lessons

`<a data-ref="transformers"></a>` renders as the linked lesson number, for example "08". Write the
surrounding words yourself: `as you saw in lesson <a data-ref="transformers"></a>`. Lesson numbers are
assigned by the build, so references stay correct when lessons are reordered.

### Callouts

```html
<div class="admonition tip">
<p class="admonition-title">Keep the model name in one place</p>
<p>...</p>
</div>
```

Kinds: `note`, `tip`, `warning`, `danger`. Use them sparingly, for things a reader must not miss.

### Hands-on exercises and solutions

```html
<div class="admonition exercise">
<p class="admonition-title">Hands-on: train a Q-learning agent</p>
<p>What to build, in numbered steps, with the expected result so the learner knows when they are done.</p>
</div>
<details class="solution">
<summary>Show a solution</summary>
<p>...</p>
</details>
```

Each exercise needs a matching markdown cell (with the same title) and an empty `# Your code here` cell in
the notebook, and a worked solution in the solutions notebook.

### Tabs

For alternatives such as two providers or two operating systems:

```html
<div class="tabs">
<section data-tab="macOS and Linux">...</section>
<section data-tab="Windows">...</section>
</div>
```

### Figures

```html
<figure>
<svg class="diagram" viewBox="0 0 560 220" role="img" aria-label="What the diagram shows, in one sentence">
<rect class="box" x="10" y="20" width="120" height="40" rx="6"/>
<text x="70" y="45" text-anchor="middle">input</text>
<path class="wire" d="M130 40 H200"/>
</svg>
<figcaption>One sentence that says what to notice.</figcaption>
</figure>
```

Classes: `box` (a node), `wire` (a connector), `accent` (filled with the lesson colour), `accent-stroke`,
`muted` (secondary text). Text is 13px. Keep the `viewBox` at most 560 units wide and stack things
vertically when you can, so the diagram stays legible on a phone. Never hard-code colours: the classes
follow light and dark mode.

### Tables

Plain `<table>` with `<thead>` and `<tbody>`. Keep them to four columns or fewer for phones.

### End of every lesson

1. `<h2>Check yourself</h2>`, then a quiz of five questions:

   ```html
   <div class="quiz">
   <div class="q">
   <p>Question text?</p>
   <ul>
   <li>A wrong answer</li>
   <li class="correct">The right answer</li>
   <li>Another wrong answer</li>
   <li>Another wrong answer</li>
   </ul>
   <p class="why">Why the right answer is right, in one or two sentences.</p>
   </div>
   </div>
   ```

2. Key takeaways: `<div class="admonition takeaways"><p class="admonition-title">Key takeaways</p><ul>...</ul></div>`
3. `<h3>Go deeper</h3>` with three to six books, papers, courses or documentation pages.

## Notebooks

* Cell 0 is a markdown header. The build rewrites it from the lesson metadata, so do not edit it by hand.
* Cell 1 is `## Setup` and cell 2 installs what the lesson needs: `%pip install -q numpy torch`.
* Then the lesson's sections, as markdown headings, with every code block from the lesson.
* A cell that needs something special starts with one of these comment lines, exactly:
  `# Needs an API key`, `# Needs a GPU runtime`, `# Downloads a model or data on first run`,
  `# Uses your own files`. Everything else must run on a laptop CPU, offline, in a few minutes in total.
  Prefer datasets that ship with scikit-learn, statsmodels or networkx, or generate data in code.
* Clear all outputs before committing.
* Check a notebook with:

  ```bash
  python tools/check_notebooks.py --no-install notebooks/21-reinforcement-learning.ipynb
  ```
