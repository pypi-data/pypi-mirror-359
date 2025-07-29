def _read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return f"<binary file: {file_path.name}>"

def should_ignore(path, ignore_patterns):
    name = path.name

    if name in ignore_patterns:
        return True

    for pattern in ignore_patterns:
        if '*' in pattern:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
            if pattern.endswith('*') and name.startswith(pattern[:-1]):
                return True

    return False
