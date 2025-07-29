# 📦 Ctrl+C

[![PyPI version](https://img.shields.io/pypi/v/ctrlc-cli?color=blue&style=flat-square)](https://pypi.org/project/ctrlc-cli/)
[![License](https://img.shields.io/github/license/askadvaith/ctrl-c?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/ctrlc-cli?style=flat-square)](https://pypi.org/project/ctrlc-cli/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)](https://pypi.org/project/ctrlc-cli/)


Because sometimes you really just want to Ctrl+C your whole project context for an LLM without manually sifting through a minefield of `.git`, `__pycache__`, and a million CSVs.

---

## What is Ctrl+C?

Ctrl+C is a lightweight Python CLI tool that bundles up your entire codebase into a single context file. It uses ignore files, size filters, and compression options to make the output just right. No more manual copy-pasting code context over and over; one simple command and you're set :)
<br/>
## Installation

```bash
pip install ctrlc-cli
```
## Usage
Run this in your project root directory:
```bash
ctrlc run
```
This will walk through your codebase and save the formatted context to a `context.txt` in the project's root directory.

### Flags and Options

| Flag             | Description                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `--ignore-files`        | Use ignore rules from `.gitignore`, `.contextignore`, or both. Options: `none`, `all`, `git` (only from `.gitignore`), `context` (only from `.contextignore`). Default: `all`. |
| `--threshold`           | Skip files larger than this many bytes. Ideal for keeping massive files out of the bundle.                               |
| `--compress`            | Compress the output file. Options: `none`, `gzip`, `zip`, `tar.gz`. Default: `none`.                                     |
| `--output`              | Name of the output file (without extension for compressed options). Default: `context.txt`.                              |

## Default Skips
Ctrl+C comes with built-in ignore rules for common non-codebase related folders:

- `.git`, `.svn`, `.hg`, `__pycache__`
- `node_modules`, `.DS_Store`, `.vscode`, `.env`, `.venv`
- `context.txt`, `.gitignore`, `.contextignore`

You can layer on your own `.gitignore` and `.contextignore` filters too.

## The `.contextignore` File
The `.contextignore` file essentially works the same way a `.gitignore` file does. Simply create one in your project's root directory and add the file/folder names you want to exclude. Those files will not be written to your final context file. An example `.contextignore` file is given below:
```
*/subfolder1
*/subfolder2
file1.py
folder1
```

## License
This project is licensed under the [MIT License](https://github.com/askadvaith/Ctrl-C/blob/main/LICENSE).
