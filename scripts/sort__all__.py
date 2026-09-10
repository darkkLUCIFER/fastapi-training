"""Sort __all__ in Python files by length."""

import sys
import ast
import pathlib


def _offset(source: str, lineno: int, col_offset: int) -> int:
    """Return the zero-based character offset for an AST source position."""
    return sum(len(line) for line in source.splitlines(keepends=True)[: lineno - 1]) + col_offset


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
                    items = ", ".join(f"'{value}'" for value in sorted_values)
                    if is_tuple:
                        formatted = f"({items},)" if len(sorted_values) == 1 else f"({items})"
                    else:
                        formatted = f"[{items}]"

                    start = _offset(source, node.lineno, node.col_offset)
                    end = _offset(source, node.end_lineno, node.end_col_offset)
                    source = source[:start] + f"__all__ = {formatted}" + source[end:]
                    filepath.write_text(source)
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
