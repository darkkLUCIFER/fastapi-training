"""Sort __all__ in Python files by length."""

import sys
import ast
import pathlib


def sort_all(filepath: pathlib.Path) -> bool:
    source = filepath.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    current = [elt.value for elt in node.value.elts]
                    sorted_values = sorted(current, key=len)
                    if current == sorted_values:
                        return False
                    is_tuple = isinstance(node.value, ast.Tuple)
                    lines = source.splitlines()
                    for i, line in enumerate(lines):
                        if "__all__" in line and "=" in line:
                            indent = len(line) - len(line.lstrip())
                            items = ", ".join(f"'{v}'" for v in sorted_values)
                            if is_tuple:
                                formatted = (
                                    f"({items},)"
                                    if len(sorted_values) == 1
                                    else f"({items})"
                                )
                            else:
                                formatted = f"[{items}]"
                            lines[i] = " " * indent + f"__all__ = {formatted}"
                            j = i + 1
                            while j < len(lines) and lines[j].strip() not in (")", "]"):
                                lines.pop(j)
                            if j < len(lines):
                                lines.pop(j)
                            break
                    filepath.write_text("\n".join(lines) + "\n")
                    return True
    return False


def main():
    files = [pathlib.Path(f) for f in sys.argv[1:]]
    changed = False
    for f in files:
        if sort_all(f):
            print(f"Sorted __all__ in {f}")
            changed = True
    sys.exit(1 if changed else 0)


if __name__ == "__main__":
    main()
