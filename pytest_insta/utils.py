__all__ = [
    "normalize_node_name",
    "node_path_name",
    "hexdump",
    "hexload",
    "is_ci",
    "pluralize",
    "remove_path",
]


import math
import os
import re
import shutil
from pathlib import Path
from typing import Any, Tuple

from _pytest import python


def normalize_node_name(name: str):
    return re.sub(
        r"\W+", "_", re.sub(r"^(tests?[_/])*|([_/]tests?)*(\.\w+)?$", "", name)
    ).strip("_")


def node_path_name(node: Any) -> Tuple[Path, str]:
    hierarchy = [normalize_node_name(node.name)]

    while not isinstance(node, python.Module):
        node = node.parent
        hierarchy.append(normalize_node_name(node.name))

    return (
        Path(node.fspath).relative_to(Path(".").resolve()),
        "__".join(reversed(hierarchy)),
    )


def hexdump(data: bytes, n: int = 16):
    for k, i in enumerate(range((len(data) + n - 1) // n)):
        values = data[i * n : (i + 1) * n]
        line = values.hex(b" ", -2)
        suffix = "".join(chr(i) if chr(i).isprintable() else "." for i in values)
        yield f"{k * n:08x}:  {line:{math.ceil(n * 2.5)}} {suffix}"


def hexload(dump: str):
    return b"".join(bytes.fromhex(line.split("  ")[1]) for line in dump.splitlines())


def is_ci():
    return "CI" in os.environ or "TF_BUILD" in os.environ


def pluralize(word: str, count: int) -> str:
    return f"{count} {word}" + "s" * (count > 1)


def remove_path(path: Path):
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)
