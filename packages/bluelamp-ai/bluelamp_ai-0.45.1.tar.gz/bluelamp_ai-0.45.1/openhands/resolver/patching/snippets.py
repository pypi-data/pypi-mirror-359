import os
import re
from shutil import rmtree
def remove(path: str) -> None:
    if os.path.exists(path):
        if os.path.isdir(path):
            rmtree(path)
        else:
            os.remove(path)
def findall_regex(items: list[str], regex: re.Pattern[str]) -> list[int]:
    found = list()
    for i in range(0, len(items)):
        k = regex.match(items[i])
        if k:
            found.append(i)
            k = None
    return found
def split_by_regex(items: list[str], regex: re.Pattern[str]) -> list[list[str]]:
    splits = list()
    indices = findall_regex(items, regex)
    if not indices:
        splits.append(items)
        return splits
    splits.append(items[0 : indices[0]])
    for i in range(len(indices) - 1):
        splits.append(items[indices[i] : indices[i + 1]])
    splits.append(items[indices[-1] :])
    return splits
def which(program: str) -> str | None:
    def is_exe(fpath: str) -> bool:
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None