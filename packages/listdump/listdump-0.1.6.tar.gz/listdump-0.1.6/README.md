# listdump 📂💻→📝

[![PyPI – Version](https://img.shields.io/pypi/v/listdump.svg)](https://pypi.org/project/listdump/#history)

**listdump** is a lightweight CLI tool that recursively (or non-recursively) lists relevant files in a directory and outputs their contents wrapped in Markdown-style code blocks (```), ready for documentation, debugging, or review.

by Tim Abdiukov

---

## 📦 Installation

```bash
pip install listdump
```

Run it from anywhere using:

```bash
listdump [arguments]
```

---

## 🚀 Usage

```bash
listdump [includes] [-x excludes] [-no-sub] [-out=filename] [-dir=path] [-no-gitignore] [-include-hidden]
```

### 🔧 Arguments

| Argument          | Description                                                                   |
| ----------------- | ----------------------------------------------------------------------------- |
| `includes`        | Extensions or glob patterns to include (`py`, `txt`, `log_*_202*.log`, etc.)  |
| `-x`, `--exclude` | Extensions or glob patterns to exclude                                        |
| `-no-sub`         | Exclude subfolders                                                            |
| `-out=FILE`       | Output file name (default: `output.md`)                                       |
| `-dir=DIR`        | Starting directory (default: current)                                         |
| `-no-gitignore`   | Do not respect `.gitignore` rules                                             |
| `-include-hidden` | Include normally excluded files: `.git`, `.gitignore`, and `listdump.md`,  and license files (LICENCE, LICENSE) |
| `-h`, `--help`    | Show help message                                                             |

---

## 🧪 Examples

```bash
listdump txt py -x log tmp
```

> Includes `.txt` and `.py` files, excludes `.log` and `.tmp`

```bash
listdump py -no-sub
```

> Includes `.py` files only in the current directory

```bash
listdump py -no-gitignore -include-hidden
```

> Includes `.py` files, even those ignored by `.gitignore` and including `.git`, `.gitignore`, `listdump.md`, and license files

---

---------------------------------

***Tim Abdiukov***
