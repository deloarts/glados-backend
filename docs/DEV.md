# developing

- [developing](#developing)
  - [1 repository](#1-repository)
    - [1.1 cloning](#11-cloning)
    - [1.2 main branch protection](#12-main-branch-protection)
    - [1.3 branch naming convention](#13-branch-naming-convention)
    - [1.4 issues](#14-issues)
  - [2 poetry](#2-poetry)
    - [2.1 setup](#21-setup)
    - [2.2 install](#22-install)
    - [2.3 tests](#23-tests)
  - [3 pre-commit hooks](#3-pre-commit-hooks)
  - [4 api docs](#4-api-docs)
  - [5 new revision checklist](#5-new-revision-checklist)
  - [6 to do](#6-to-do)

## 1 repository

### 1.1 cloning

Clone the repo to your local machine:

```bash
git clone git@github.com:deloarts/glados-backend.git
```

### 1.2 main branch protection

> ❗️ Never develop new features and fixes in the main branch!

The main branch is protected: it's not allowed to make changes directly to it. Create a new branch in order work on issues. The new branch should follow the naming convention from below.

### 1.3 branch naming convention

1. Use grouping tokens at the beginning of your branch names, such as:
   - feature: A new feature that will be added to the project
   - fix: For bugfixes
   - tests: Adding or updating tests
   - docs: For updating the docs
   - wip: Work in progress, won't be finished soon
   - junk: Just for experimenting
2. Use slashes `/` as delimiter in branch names (`feature/docket-export`)
3. Avoid long descriptive names, rather refer to an issue
4. Do not use bare numbers as leading parts (`fix/108` is bad, `fix/issue108` is good)

### 1.4 issues

Use the issue templates for creating an issue. Please don't open a new issue if you haven't met the requirements and add as much information as possible. Further:

- Format your code in an issue correctly with three backticks, see the [markdown guide](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
- Add the full error trace.
- Do not add screenshots for code or traces.

## 2 poetry

Dependency management is done with [Poetry](https://python-poetry.org/).

### 2.1 setup

If you prefer the environment inside the projects root, use:

```powershell
poetry config virtualenvs.in-project true
```

> ⚠️ Make sure not to commit the virtual environment to GitHub. See [.gitignore](.gitignore) to find out which folders are ignored.

### 2.2 install

Install all dependencies (assuming you are inside the projects root folder):

```powershell
poetry install
```

Check your active environment with:

```powershell
poetry env list
poetry env info
```

Update packages with:

```powershell
poetry update
```

### 2.3 tests

Tests are done with pytest. For testing with poetry run:

```powershell
poetry run pytest
```

## 3 pre-commit hooks

Don't forget to install the pre-commit hooks:

```powershell
pre-commit install
```

## 4 api docs

The API docs are available only when the app runs in debug mode (see config.yml for details).
The docs can be viewed at `localhost:port/docs`, where the port is the port you've defined in the config file.

## 5 new revision checklist

1. Update **dependencies**: `poetry update`
2. Update the **version** in
   - [pyproject.toml](pyproject.toml)
   - [const.py](app/const.py)
   - [README.md](README.md)
3. Run all **tests**: `poetry run pytest`
4. Check **pylint** output: `poetry run pylint app/`
5. Update the **lockfile**: `poetry lock`
6. Update the **requirements.txt**: `poetry export -f requirements.txt -o requirements.txt`

## 6 to do

Using VS Code [Comment Anchors](https://marketplace.visualstudio.com/items?itemName=ExodiusStudios.comment-anchors) to keep track of to-dos.
