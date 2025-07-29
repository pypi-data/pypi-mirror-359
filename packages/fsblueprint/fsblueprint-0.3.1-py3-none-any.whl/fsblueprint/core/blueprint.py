import yaml
from pathlib import Path
from .utils import _read_file, should_ignore
from .ignore_patterns import DEFAULT_IGNORE_PATTERNS

yaml.add_representer(str, lambda dumper, data: dumper.represent_scalar(
    'tag:yaml.org,2002:str', data, style='|' if '\n' in data else None))

def create_yaml_from_structure(source_dir, output_yaml, ignore_patterns=None, include_content=False):
    structure = _scan_structure(Path(source_dir), ignore_patterns, include_content)
    with open(output_yaml, 'w') as f:
        yaml.dump(structure, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def _scan_structure(path, ignore_patterns=None, include_content=False):
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")

    if path.is_file():
        return _read_file(path) if include_content else ""

    result = {}
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))

    for item in items:
        if ignore_patterns is not None and should_ignore(item, ignore_patterns):
            continue

        if item.is_dir():
            sub_structure = _scan_structure(item, ignore_patterns, include_content)
            if sub_structure:
                result[item.name] = sub_structure
        else:
            result[item.name] = _read_file(item) if include_content else ""

    return result


def create_structure_preview(source_dir, ignore_patterns=None):
    path = Path(source_dir)
    lines = _build_tree(path, ignore_patterns)
    return "\n".join(lines)


def _build_tree(path, ignore_patterns=None, prefix=""):
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")

    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
    lines = []
    for idx, item in enumerate(items):
        is_last = idx == len(items) - 1
        branch = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "

        if ignore_patterns and should_ignore(item, ignore_patterns):
            continue

        lines.append(f"{prefix}{branch}{item.name}")

        if item.is_dir():
            lines += _build_tree(item, ignore_patterns, prefix + next_prefix)

    return lines
