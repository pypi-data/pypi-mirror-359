import yaml
from pathlib import Path

def create_from_yaml(yaml_file, target_dir="."):
    with open(yaml_file, 'r') as f:
        structure = yaml.safe_load(f)

    _create_structure(structure, Path(target_dir))

def _create_structure(structure, base_path):
    for name, content in structure.items():
        path = base_path / name

        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            _create_structure(content, path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content or "")
