__all__ = [
    "normalize_node_name",
    "node_path_name",
    "get_snapshots_path",
    "hexdump",
    "hexload",
    "is_ci",
    "pluralize",
    "remove_path",
    "rename_path",
]


import math
import os
import re
import shutil
from pathlib import Path
from typing import Any, Iterator, Tuple

from _pytest import python

_SNAPSHOTS_FOLDER = "snapshots"


def normalize_node_name(name: str) -> str:
    return re.sub(
        r"\W+", "_", re.sub(r"^(tests?[_/])*|([_/]tests?)*(\.\w+)?$", "", name)
    ).strip("_")


def get_snapshots_path(node: Any, use_directories_for_snapshots: bool) -> Path:
    if use_directories_for_snapshots:
        path = Path(node.fspath)
        test_file_name = normalize_node_name(path.stem)
        # When you use pytest.mark.parametrize, test name will be test_name[test_case_name]
        # We need to replace '[', ']' with '/' to create a directory structure: name/test_case_name
        test_name = node.name.replace("[", "/").replace("]", "/")
        return path.with_name(_SNAPSHOTS_FOLDER).joinpath(test_file_name, test_name)
    path, name = node_path_name(node)
    return path.with_name(_SNAPSHOTS_FOLDER) / name


def node_path_name(node: Any) -> Tuple[Path, str]:
    hierarchy = [normalize_node_name(node.name)]

    while not isinstance(node, python.Module):
        node = node.parent
        hierarchy.append(normalize_node_name(node.name))

    path = Path(node.fspath)  # type: ignore

    return (
        path.relative_to(Path(".").resolve()),
        "__".join(reversed(hierarchy)),
    )


def hexdump(data: bytes, n: int = 16) -> Iterator[str]:
    for k, i in enumerate(range((len(data) + n - 1) // n)):
        values = data[i * n : (i + 1) * n]
        line = values.hex(b" ", -2)
        suffix = "".join(chr(i) if 32 <= i < 127 else "." for i in values)
        yield f"{k * n:08x}:  {line:{math.ceil(n * 2.5)}} {suffix}"


def hexload(dump: str) -> bytes:
    return b"".join(bytes.fromhex(line.split("  ")[1]) for line in dump.splitlines())


def is_ci() -> bool:
    return "CI" in os.environ or "TF_BUILD" in os.environ


def pluralize(word: str, count: int) -> str:
    return f"{count} {word}" + "s" * (count > 1)


def remove_path(path: Path):
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def rename_path(src: Path, dst: Path):
    remove_path(dst)
    shutil.move(str(src), dst)
