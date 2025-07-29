# FSBlueprint

**FSBlueprint** is a Python CLI and API tool for working with directory structures and blueprints. Easily scaffold projects from YAML definitions or generate reusable blueprints from existing directories.

---

## ✨ Features

- ✅ Scaffold full folder structures from a simple YAML blueprint
- ✅ Generate YAML from any existing folder structure
- ✅ Default: Outputs a **tree-style structure preview**
- ✅ Optional: Include **file contents** in the YAML blueprint with `--with-content`
- ✅ Supports nested folders, empty files, and multiline content
- ✅ Simple CLI + importable Python API

---

## 📦 Installation

Install from PyPI:

```bash
pip install fsblueprint
```

---

## 🚀 Usage

### 🔧 Scaffold a directory structure from YAML

```bash
fsblueprint scaffold project.yaml ./my_project
```

This creates folders and files based on your `project.yaml` blueprint.

---

### 🔍 Preview a directory structure

```bash
fsblueprint blueprint ./existing_project
```

This will print a tree-like structure of your folder (ignoring system/development files by default).

#### Example output:

```
📂 Structure Preview:

existing_project/
├── README.md
├── src/
│   ├── main.py
│   └── utils/
│       └── helper.py
└── tests/
    └── test_main.py
```

---

### 🧾 Generate YAML with file contents

```bash
fsblueprint blueprint ./existing_project blueprint.yaml --with-content
```

This saves a `.yaml` file that includes both structure and file content.

---

## 📄 Example YAML Blueprint

```yaml
my_project:
  README.md: |
    # My Project
    Hello world!
  src:
    main.py: |
      def main():
          print("Hello!")
    utils:
      helper.py: ""
  tests:
    test_main.py: ""
```

---

## 🛠 Ignore Patterns

By default, FSBlueprint excludes common directories like `.git`, `node_modules`, `.env`, `__pycache__`, etc.
Use `--no-ignore` to include everything, or `--ignore pattern1 pattern2` to extend ignore behavior.

---

## 📜 License

MIT
