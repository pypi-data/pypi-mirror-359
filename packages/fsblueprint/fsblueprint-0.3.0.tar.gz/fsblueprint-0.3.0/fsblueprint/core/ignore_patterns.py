DEFAULT_IGNORE_PATTERNS = {
    '.git', '.gitignore', '.gitkeep', '.gitmodules', '.gitattributes',
    '.hg', '.hgignore', '.hgtags',
    '.svn',

    '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.Python',
    'build', 'develop-eggs', 'dist', 'downloads', 'eggs', '.eggs',
    'lib', 'lib64', 'parts', 'sdist', 'var', 'wheels',
    '*.egg-info', '.installed.cfg', '*.egg',
    '.pytest_cache', '.coverage', '.tox', '.cache',
    '.mypy_cache', '.dmypy.json', 'dmypy.json',

    'node_modules', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*',
    '.npm', '.yarn-integrity',

    '.vscode', '.idea', '*.swp', '*.swo', '*~', '.DS_Store',
    'Thumbs.db', '.sublime-project', '.sublime-workspace',

    '.DS_Store', '.DS_Store?', '._*', '.Spotlight-V100', '.Trashes',
    'ehthumbs.db', 'Thumbs.db',

    '*.log', 'logs', 'temp', 'tmp', '.tmp',

    '.env', '.env.local', '.env.*.local',

    '.uv', '.venv', 'venv', 'env', 'ENV',
}
