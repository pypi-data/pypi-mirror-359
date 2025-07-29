# repo-to-md

[![PyPI version](https://img.shields.io/pypi/v/repo-to-md.svg)](https://pypi.org/project/repo-to-md/)  
[![Python versions](https://img.shields.io/pypi/pyversions/repo-to-md.svg)](https://pypi.org/project/repo-to-md/)

**repo-to-md** turns any repo or just a part of it into a single **Markdown** with a full file `tree` and the full contents of every source file. Binary files, images, build artifacts, and dependency lock-files are automatically excluded so you get a clean, copy-pastable context for:

* providing context to AI coding assistants such as **Claude Code** (Anthropic), **ChatGPT** (OpenAI), **GitHub Copilot**, or **deep-research** agents;
* code reviews, documentation, or quick sharing on forums and gists;
* pasting snippets while staying under model token limits.

## Table of contents

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Copy to clipboard](#copy-to-clipboard)
* [With Claude Code](#with-claude-code)
* [Contributing & License](#contributing--license)

## Features

* Remote or local - works with `owner/repo`, `/local/path/repo`, full Git URLs and more.
* Selective output - include (`-i`) and exclude (`-e`) any number of paths or globs like `src/`, `tests/*`, `README.md`.
* Smart filtering - skips binary blobs, media, archives, and dozens of lock files automatically.
* Pure-Python - no system-level dependencies, runs everywhere Python does.
* Supports Python 3.10 and newer - published on PyPI.

## Installation

The project is distributed on PyPI, so any modern Python installer will work.  
If you already use the excellent [`uv`](https://github.com/astral-sh/uv) tool, a
single command is enough:

To run `repo-to-md` one time, without installing it, use `uvx`:

```bash
# Run one time using uvx
uvx repo-to-md github/repo > repo.md
```

Or install it globally:

```bash
# Install
uv tool install repo-to-md
# Run it
repo-to-md github/repo > repo.md
```

Of course, you can also use `pip` if you prefer.

```bash
# Install
pip install repo-to-md
# Run it
repo-to-md github/repo > repo.md
```

### Supported platforms

* macOS, Linux, Windows
* Python ≥ 3.10 (see badge above)

## Usage

Entire GitHub repo into a single `hello-world.md` file.

```bash
repo-to-md octocat/Hello-World > hello-world.md
```

Local repo but only files inside the `src/` folder.

```bash
repo-to-md ~/Projects/myapp -i src/ > myapp_src.md
```

Print contents of just the `pyproject.toml` file alone:

```bash
repo-to-md . -i pyproject.toml
```

The first positional argument is either a GitHub repo or a local path.  
Selectively include or exclude files/directories with `-i/--include` and `-e/--exclude`.

## Copy to clipboard

* **macOS**: `repo-to-md . | pbcopy` *(paste with ⌘<kbd>V</kbd>)*
* **Linux / X11**: `repo-to-md . | xclip -selection clipboard`
* **Windows / PowerShell**: `repo-to-md . | clip`

Replace `.` with any path or GitHub repo, and feel free to include `src/` or similar after it.

## With Claude Code

Best way to use it inside Claude Code is to ask it to dump the repo into
a Markdown file and then work with that file.

```shell
Bash(repo-to-md github/repo > repo.md)
```

Alternatively, you can just output the entire repo into current context:

```shell
Bash(repo-to-md github/repo)
```

You can even invoke it without `Bash` and Claude will understand you.

```shell
repo-to-md github/repo
```

## Contributing & License

Issues and pull requests are welcome.  Licensed under the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html).
