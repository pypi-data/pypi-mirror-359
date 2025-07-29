import os
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

def load_ignore(root: str, filename: str):
    path = os.path.join(root, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        patterns = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    return PathSpec.from_lines(GitWildMatchPattern, patterns)