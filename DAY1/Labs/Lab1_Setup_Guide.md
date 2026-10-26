# Lab 1: Environment, Git and a Shared Workspace

**Time:** about 75 minutes
**You'll finish with:** a project folder under Git, an isolated Python environment you can rebuild from a
file, and VS Code and Jupyter pointing at that environment.

This lab happens mostly in a terminal on a MacBook. Commands are for macOS (zsh or bash).

---

## Part 1: What Python are you actually running?

Most "it works on my machine" problems come from not knowing which Python is running your code. Start
by finding out.

Open Terminal and run:

```bash
python3 --version
which -a python3
```

If you see more than one path, that's normal. MacBooks often have a system Python, one from Homebrew,
one from Anaconda, and so on. The first one in the list is the one that runs when you type `python3`.

**Check yourself:** write down the version and path you got. You'll compare it with the one inside your
environment in Part 3.

## Part 2: pip or conda?

You'll hear both. Here's how to choose:

- **pip + venv** comes with Python. It installs packages from PyPI. It's light, and it's what you'll find
  on most servers and in most Docker images.
- **conda** (Anaconda, Miniconda, Miniforge) manages Python itself as well as packages, and it's good at
  packages with heavy non-Python dependencies (some geospatial and GPU libraries). It's common on
  analysts' laptops.

Pick one per project and stick with it. Mixing `conda install` and `pip install` in the same environment is
the usual cause of environments nobody can rebuild. If you must mix, install everything you can with
conda first, then pip, and never go back to conda afterwards.

For this course either works. The notebooks don't care, as long as the packages are there.

## Part 3: Create the project and its environment

Make a working folder for the course **inside this Day 1 `Labs` folder**, so everything you build stays next to
the material it came from. Open a terminal in the Day 1 `Labs` folder first (in VS Code: right-click the folder,
then **Open in Integrated Terminal**), then run:

```bash
mkdir -p ./work/fund-ai && cd ./work/fund-ai
```

The environment you create in this folder is the one you'll use for the whole course. From Day 2 onwards, the first
cell of each day's Lab 1 finds it, installs that day's libraries into it, and connects the notebook to it for you.

### Option A: venv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should now start with `(.venv)`. Run the checks from Part 1 again:

```bash
which python         # should be inside .venv
```

The path changed. That's the whole point of an environment: this project now has its own Python and its
own packages, and nothing you install here touches any other project.

### Option B: conda

```bash
conda create -n fund-ai python=3.11 -y
conda activate fund-ai
python --version
```

To leave an environment, run `deactivate` (venv) or `conda deactivate` (conda).

## Part 4: Install packages and pin them

Install the core stack:

```bash
# venv
python -m pip install --upgrade pip
python -m pip install pandas numpy matplotlib scikit-learn pyarrow jupyterlab ipykernel

# conda
conda install -c conda-forge pandas numpy matplotlib scikit-learn pyarrow jupyterlab ipykernel -y
```

Now write down exactly what you installed, so someone else (or you, in six months) can rebuild it:

```bash
# venv
python -m pip freeze > requirements.txt

# conda: only the packages you asked for, which travels better between operating systems
conda env export --from-history > environment.yml
```

Open the file you created and look at it. `pip freeze` lists every package, including dependencies you
never asked for, each with an exact version. That's what makes it reproducible.

Compare yours with the reference `environment.yml` in this folder. The versions won't match exactly, and that's
fine. What matters is that your file describes your environment.

**A rule to keep:** whenever you install something new, update the file in the same sitting.

## Part 5: The reproducibility test

A requirements file you've never rebuilt from is only a hope. Test it:

```bash
# venv
deactivate && rm -rf .venv
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import pandas, sklearn; print(pandas.__version__, sklearn.__version__)"
```

```bash
# conda
conda deactivate
conda env remove -n fund-ai -y
conda env create -f environment.yml
conda activate fund-ai
```

If the last command prints versions without errors, you've passed. You just proved that your project can
be rebuilt from two text files, which is also exactly what a server or a Docker build does on Day 10.

## Part 6: A project layout everyone can find their way around

Create this structure:

```bash
mkdir -p data/raw data/processed notebooks src reports/figures
touch README.md .gitignore
```

```
fund-ai/
├── data/
│   ├── raw/          # extracts exactly as received. Never edited.
│   └── processed/    # outputs of your pipeline
├── notebooks/        # exploration
├── src/              # code that other code or people depend on
├── reports/
│   └── figures/
├── README.md
├── requirements.txt  (or environment.yml)
└── .gitignore
```

Copy the four CSV files from the Day 1 `Labs` folder (two levels up) into `data/raw/`, and the two notebooks for
Labs 2 and 3 into `notebooks/`:

```bash
cp ../../*.csv data/raw/
cp ../../Lab2_*.ipynb ../../Lab3_*.ipynb notebooks/
```

The notebooks look for the CSV files next to themselves first, then in `../data/raw/`, so either layout works.

Put three or four lines in `README.md`: what the project is, how to create the environment, and how to run
things. You'll add to it through the week.

## Part 7: Git basics, and what must never be committed

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.org"
git config --global init.defaultBranch main
```

Before your first commit, fill in `.gitignore`. Open it and paste:

```gitignore
# Environments
.venv/
env/
__pycache__/
.ipynb_checkpoints/

# Data: member data never goes into Git, not even "just for testing"
data/
*.csv
*.parquet
*.xlsx

# Secrets
.env
*.key
credentials*

# Editor clutter
.vscode/
.DS_Store
```

Pay attention to the data lines. Git keeps every version of every file forever, and on a shared server that
means anyone with read access can reach it years later, even after you "delete" it. Member records,
NIDA numbers and phone numbers are personal data under the Personal Data Protection Act. They don't
belong in a repository. On Day 3 you'll use DVC for versioning data properly.

Now make the first commit:

```bash
git init
git status                    # read this: what is Git going to track?
git add README.md .gitignore requirements.txt src notebooks
git commit -m "Set up project structure and environment file"
git log --oneline
```

Run `git status` once more and confirm that nothing under `data/` or `.venv/` shows up. If it does, fix
`.gitignore` before you go any further.

**About commit messages:** write them so a colleague can understand them without opening the code.
"Fix bug" doesn't help anyone. "Treat negative contribution amounts as reversals, not errors" does.

## Part 8: Working the way a team does, on your own

In the Fund, other people will change the same code you do. You'll practise that here by playing both
parts yourself: **you**, in the `fund-ai` folder, and **a colleague**, in a second copy of the project.
Along the way you'll use branches, a remote repository, a merge conflict and a review.

### The remote repository

Normally the remote lives on a Git server: the Fund's internal GitLab or Gitea, or GitHub or Azure DevOps if
you're allowed to use them for training material. If you have access to one, create an empty repository
there and use its URL below.

This choice connects to the morning session. A self-hosted Git server keeps code (and anything
accidentally committed with it) inside your own network, and the Fund's ICT team patches and backs it up. A
cloud service is less work to run, but your code sits on someone else's infrastructure. For code that
touches member data pipelines, many public institutions choose self-hosted. Neither is wrong. Know which
one you're using and why.

If you don't have a Git server today, a folder next to your project can play its part. From inside `fund-ai`:

```bash
git init --bare --initial-branch=main ../git-server/fund-ai.git
```

Use `../git-server/fund-ai.git` wherever the steps below say `<repository URL>`. Your `work` folder will end up
holding three things side by side: `fund-ai` (you), `fund-ai-colleague` (the colleague) and `git-server`.

### The exercise

1. **You** push the project (you're still inside `work/fund-ai`):
   ```bash
   git remote add origin <repository URL>
   git push -u origin main
   ```
2. **The colleague** clones it into a second folder, gives themselves a name, and starts a branch:
   ```bash
   cd ..                         # now in the work folder
   git clone git-server/fund-ai.git fund-ai-colleague
   cd fund-ai-colleague
   git config user.name "A. Colleague"
   git switch -c add-data-notes
   ```
3. **The colleague** edits the one-sentence project description in `README.md`, then commits and pushes the
   branch:
   ```bash
   git commit -am "Describe the data sources in the README"
   git push -u origin add-data-notes
   ```
4. **You** (back in `fund-ai`) edit **the same line** of `README.md` differently, commit on `main`, and push.
5. **The colleague** brings in your change before asking for a merge:
   ```bash
   cd ../fund-ai-colleague
   git pull origin main          # brings in your change and shows the conflict
   ```
   Open `README.md`. You'll see markers like these:
   ```
   <<<<<<< HEAD
   the colleague's version
   =======
   your version
   >>>>>>> ...
   ```
   Decide what the line should say. Usually that means combining the two versions. Delete the markers,
   save the file, then:
   ```bash
   git add README.md
   git commit -m "Merge main into add-data-notes and combine project descriptions"
   git push
   ```
6. **You** review the branch before merging it. On a Git server, open a pull request (merge request) and read
   the diff there. With a local folder as the remote, read it in the terminal:
   ```bash
   cd ../fund-ai
   git fetch
   git log --oneline --graph --all          # see both lines of work and the merge
   git diff main origin/add-data-notes      # exactly what would change
   ```
7. If you're happy with it, **you** merge and push:
   ```bash
   git merge origin/add-data-notes
   git push
   ```
8. **The colleague** runs `git switch main` and `git pull`. The two folders should now be identical, and
   `git log` shows commits from two different authors.

Conflicts are normal. They just mean two people changed the same thing, and Git won't guess who's right.

## Part 9: VS Code and Jupyter pointing at the right Python

Make sure the **Python** and **Jupyter** extensions are installed in VS Code. Then:

1. In the terminal where your environment is active (the prompt starts with `(.venv)`), run:
   ```bash
   python -c "import sys; print(sys.executable)"
   ```
2. It prints the full path of your environment's Python. Something like
   `.../DAY1/Labs/work/fund-ai/.venv/bin/python`.
3. Copy that path.
4. Press `Cmd+Shift+P`, run **Python: Select Interpreter**, choose **Enter interpreter
   path...**, and paste the path you copied.
5. Open `notebooks/Lab2_Exploring_the_Fund_Data.ipynb`. In the top right, pick the kernel from the same
   environment.

**Test it:** in the first cell of the notebook, run

```python
import sys; print(sys.executable)
```

It must print the same path as step 2. If it doesn't, you've found the bug that would otherwise have cost you an hour
this afternoon.

You only do this by hand today. From Day 2 onwards, the first cell of each day's Lab 1 prepares this same environment
and prints the path to paste if VS Code isn't already using it.

## Part 10: Habits for a shared workspace

Write these into your README. They're the conventions a shared workspace at the Fund would need:

- **Notebooks are for exploring and explaining. Scripts in `src/` are for anything that has to run again.**
  If you copy a cell into a second notebook, it's time to move it into `src/`.
- **Before you commit a notebook**, run **Restart and Run All**. If it doesn't run top to bottom, it isn't
  finished. Then clear the outputs (**Clear All Outputs**), because outputs can contain member data and they
  make diffs unreadable.
- **File names** use lowercase and underscores, and notebooks carry a number that shows their order:
  `01_explore_claims.ipynb`, `02_clean_contributions.ipynb`.
- **Never edit anything in `data/raw/`.** Your code reads it and writes somewhere else.
- **No passwords, tokens or connection strings in code.** Put them in a `.env` file that Git ignores.

## Before you move on

Tick these off:

- [ ] `python -c "import sys; print(sys.executable)"` shows your project environment
- [ ] You rebuilt the environment from your requirements/environment file and it worked
- [ ] `git status` doesn't list anything under `data/` or `.venv/`
- [ ] You've resolved a merge conflict between the two copies, reviewed the branch and merged it
- [ ] The Lab 2 notebook opens with the right kernel
