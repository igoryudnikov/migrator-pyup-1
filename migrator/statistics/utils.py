import os


def list_python_files(path, ignored_prefixes, extensions=('.py', '.py3', '.pyw')):
    py_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.endswith(e) for e in extensions):
                filename = os.path.abspath(os.path.join(root, file))
                rel_path = os.path.relpath(filename, path)
                if not any(rel_path.startswith(p) for p in ignored_prefixes):
                    py_files.append(filename)
    return py_files
