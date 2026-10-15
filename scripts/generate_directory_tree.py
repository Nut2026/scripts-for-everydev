"""
This is a terminal-first folder/file generator. This script is created so
devs can easily create their project/program structure
from an ASCII/text-based directory tree, right in the terminal.

To use, paste a directory tree, like

vscode-discord-rpc/
├── .vscode/
│   ├── launch.json
│   ├── settings.json
│   ├── tasks.json
│   └── extensions.json
├── .vscodeignore
├── .gitignore
├── .eslintrc.json
├── .prettierrc
├── CHANGELOG.md
├── LICENSE
├── README.md
├── package.json
├── tsconfig.json
├── esbuild.js
├── assets/
│   └── icon.png
├── src/
│   ├── extension.ts
│   ├── discord/
│   │   ├── client.ts
│   │   ├── assets.ts
│   │   └── types.ts
│   ├── vscode/
│   │   ├── activity.ts
│   │   └── workspace.ts
│   ├── config/
│   │   ├── settings.ts
│   │   └── defaults.ts
│   ├── commands/
│   │   └── index.ts
│   ├── utils/
│   │   ├── logger.ts
│   │   └── debounce.ts
│   └── test/
│       ├── runTest.ts
│       └── suite/
│           └── index.ts
└── .github/
    └── workflows/
        └── build.yml

into your terminal. 

1. Please point your terminal to the root folder; i.e. please create the root folder
(e.g. vscode-discord-rpc) first, and then point your terminal to it (the root folder).
2. After that, type END on a new line. The root folder contents, as depicted in your pasted
directory tree: its files, subfolders, and more files - are instantly created in the root directory
your terminal is pointing to.
3. The script will print a log of the directories and files created, and write '(exist)' if they
already exist (existing files are not rewritten).

IMPORTANT: The root folder line is IGNORED - only its contents are created in your
current working directory. Please run this from inside the project/program root.
"""

import os
import sys
import re


def parse_directory_tree(text: str):
    """
    Parse an ASCII directory tree into a flat list of paths,
    with the root directory excluded, e.g.
    [
      ('vscode-discord-rpc/.vscode', True),
      ('vscode-discord-rpc/.vscode/launch.json', False),
      ('vscode-discord-rpc/.vscode/settings.json', False),
      ('vscode-discord-rpc/.vscode/tasks.json', False),
      ('vscode-discord-rpc/.vscode/extensions.json', False),
    ]
    """
    lines = text.splitlines()
    paths = []

    stack = []

    first_content_line = True

    for raw in lines:
        line = raw.rstrip("\n\r")
        if not line.strip():
            continue

        if first_content_line:
            first_content_line = False
            if line.endswith("/") and not line[0] in "│├└ ":
                stack = []
                continue

        m = re.match(r"^([\s│├└─]*)(.+)$", line)
        if not m:
            continue

        prefix, name = m.group(1), m.group(2).strip()

        normalized_prefix = prefix.replace("│", " ").replace(
            "├", " ").replace("└", " ").replace("─", " ")
        indent_len = len(normalized_prefix)

        is_dir = name.endswith("/")
        name = name.rstrip("/")

        if not name:
            continue

        while stack and stack[-1][0] >= indent_len:
            stack.pop()

        parent_names = [p[1] for p in stack]
        if parent_names:
            full = "/".join(parent_names + [name])
        else:
            full = name

        if is_dir:
            stack.append((indent_len, name))
            paths.append((full, True))
        else:
            paths.append((full, False))

    return paths


def main():
    """
    Read a directory tree from stdin and create it on disk.

    Prompts users to paste a directory tree, terminated by a line
    containing only 'END'. Parses the tree with `parse_directory_tree` and recreates
    the structure (directories and empty files as they are named) under the current
    working directory.

    IMPORTANT: Existing files and directories are untouched.

    Prints a log line for each entry as it is created, or skipped if it
    already exists.
    """
    print("Paste your directory tree below.")
    print("When done, type a line containing only 'END' and press Enter.")
    print("You will see logs of the folders/files as they are generated.\n")

    buffer = []
    for line in sys.stdin:
        if line.strip() == "END":
            break
        buffer.append(line)

    text = "".join(buffer)
    if not text.strip():
        print("No input received.")
        return

    paths = parse_directory_tree(text)

    for path, is_dir in paths:
        if is_dir:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"[dir]  {path}/")
            else:
                print(f"[skip] {path}/ (exists)")
        else:
            if not os.path.exists(path):
                parent = os.path.dirname(path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                open(path, "w").close()
                print(f"[file] {path}")
            else:
                print(f"[skip] {path} (exists)")


if __name__ == "__main__":
    main()

"""
To-do list / Ideas:
1. Do not terminate the program yet. Instead, allow a command where
users can undo the previous generation/results.
2. Improve the detail/conciseness of logs (including but not limited
to edge cases)
"""
