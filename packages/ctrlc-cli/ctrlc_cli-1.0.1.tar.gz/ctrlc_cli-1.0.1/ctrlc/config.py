import toml, os

def load_config(root: str):
    cfg = {}
    # load pyproject.toml
    path = os.path.join(root, 'pyproject.toml')
    if os.path.exists(path):
        data = toml.load(path)
        cfg = data.get('tool', {}).get('ctrlc', {})
    return cfg