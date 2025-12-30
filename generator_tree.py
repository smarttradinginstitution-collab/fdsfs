# python generator_tree.py
#!/usr/bin/env python3
import os
import sys

def generate_tree(startpath):
    # Files and directories to ignore
    ignore_patterns = {
        '__pycache__',
        '.git',
        '.idea',
        '.vscode',
        'node_modules',
        'venv',
        '.venv',
        'dist',
        'build',
        'coverage',
        '.coverage',
        '.pytest_cache',
        '.DS_Store',
        'package-lock.json',
        'yarn.lock',
        'poetry.lock',
    }

    # Specific file extensions to ignore (optional)
    ignore_extensions = {
        '.pyc',
        '.pyo',
        '.pyd',
        '.log',
    }

    tree_str = f"./\n"

    for root, dirs, files in os.walk(startpath):
        # Modify dirs in-place to filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_patterns]

        level = root.replace(startpath, '').count(os.sep)
        indent = '    ' * (level)

        # Don't print the root folder again, it's handled by startpath print
        if root != startpath:
             tree_str += f"{indent}{os.path.basename(root)}/\n"
             sub_indent = '    ' * (level + 1)
        else:
            sub_indent = '    '

        # Filter and sort files
        filtered_files = []
        for f in files:
            if f in ignore_patterns:
                continue
            _, ext = os.path.splitext(f)
            if ext in ignore_extensions:
                continue
            # Special case: ignore test output logs that might not have .log extension or vary
            if 'test_output' in f:
                continue
            filtered_files.append(f)

        filtered_files.sort()

        for f in filtered_files:
            tree_str += f"{sub_indent}{f}\n"

    return tree_str

if __name__ == "__main__":
    current_dir = os.getcwd()
    tree_content = generate_tree(current_dir)

    with open('tree.md', 'w', encoding='utf-8') as f:
        f.write(tree_content)

    print("tree.md generated successfully.")
