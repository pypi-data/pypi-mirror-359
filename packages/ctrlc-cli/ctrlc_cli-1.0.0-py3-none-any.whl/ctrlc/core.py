import os, gzip, zipfile, tarfile
from .ignore import load_ignore

BUILTIN_IGNORES = {
    '.git', '.svn', '.hg', '__pycache__', '.DS_Store', 'context.txt',
    'node_modules', '.vscode', '.idea', '.env', '.venv', '.contextignore', '.gitignore'
}

def collect_files(root, ignore_mode, threshold):
    git_path = os.path.join(root, '.gitignore')
    ctx_path = os.path.join(root, '.contextignore')
    git_exists = os.path.exists(git_path)
    ctx_exists = os.path.exists(ctx_path)

    git = load_ignore(root, '.gitignore') if ignore_mode in ('all', 'git') and git_exists else None
    ctx = load_ignore(root, '.contextignore') if ignore_mode in ('all', 'context') and ctx_exists else None

    included = []
    git_ignored = 0
    ctx_ignored = 0
    size_skipped = 0
    builtin_ignored = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in BUILTIN_IGNORES]

        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)

            if any(part in BUILTIN_IGNORES for part in rel.split(os.sep)):
                builtin_ignored += 1
                continue

            if git and git.match_file(rel):
                git_ignored += 1
                continue
            if ctx and ctx.match_file(rel):
                ctx_ignored += 1
                continue

            if threshold and os.path.getsize(full) > threshold:
                size_skipped += 1
                continue

            included.append((full, rel))

    return included, git_ignored, ctx_ignored, size_skipped, builtin_ignored, git_exists, ctx_exists

def write_bundle(root, out_name, files, compress):
    if compress == 'gzip':
        with gzip.open(out_name + '.gz', 'wb') as out:
            for full, rel in files:
                header = f'\n--- {rel} ---\n'.encode('utf-8')
                out.write(header)
                with open(full, 'rb') as infile:
                    while True:
                        chunk = infile.read(8192)
                        if not chunk:
                            break
                        out.write(chunk)

    elif compress == 'zip':
        with zipfile.ZipFile(out_name + '.zip', 'w') as z:
            for full, rel in files:
                z.write(full, rel)

    elif compress == 'tar.gz':
        with tarfile.open(out_name + '.tar.gz', 'w:gz') as tar:
            for full, rel in files:
                tar.add(full, arcname=rel)

    else:
        with open(out_name, 'w', encoding='utf-8') as out:
            for full, rel in files:
                out.write(f'\n--- {rel} ---\n')
                try:
                    with open(full, 'r', encoding='utf-8') as infile:
                        out.write(infile.read())
                except UnicodeDecodeError:
                    out.write("[[Skipped: Binary or non-UTF8 content]]\n")


# def write_bundle(root, out_name, files, compress):
#     if compress == 'gzip':
#         with gzip.open(out_name + '.gz', 'wb') as out:
#             for full, rel in files:
#                 header = f'\n--- {rel} ---\n'.encode('utf-8')
#                 out.write(header)
#                 with open(full, 'rb') as infile:
#                     while True:
#                         chunk = infile.read(8192)
#                         if not chunk:
#                             break
#                         out.write(chunk)

#     elif compress == 'zip':
#         with zipfile.ZipFile(out_name + '.zip', 'w') as z:
#             for full, rel in files:
#                 z.write(full, rel)

#     elif compress == 'tar.gz':
#         with tarfile.open(out_name + '.tar.gz', 'w:gz') as tar:
#             for full, rel in files:
#                 tar.add(full, arcname=rel)
#     else:
#         with open(out_name, 'w') as out:
#             for full, rel in files:
#                 out.write(f'\n--- {rel} ---\n')
#                 out.write(open(full).read())