
import fnmatch
import os
import pathlib
import platform
import random
import shutil
from typing import Generator, Iterator, List, Optional, Union

from packaging.version import Version


PYTHON_VERSION = Version(platform.python_version())


class CountedList(list):
    '''
    A custom list with a controlled string representation showing the count and formatted content.

    This class extends the built-in list class, providing additional functionality
    for displaying the list contents in a more readable format, especially for large lists.

    Attributes:
        max_lines (int): Maximum number of lines to display in the string representation.
        max_width (int): Maximum width of a single line in the string representation.
        n (property): Number of items in the list.

    Example:
        >>> cl = CountedList([1, 2, 3, 4, 5])
        >>> print(cl)
        (#5) [1, 2, 3, 4, 5]
        >>> print(cl.n)
        5
    '''
    def __init__(self, iterable=(), /, max_lines: int = 15, max_width: int = 120):
        '''
        Initialize a new CountedList.

        Args:
            iterable: An iterable to initialize the list with.
            max_lines (int): Maximum number of lines to display in string representation.
            max_width (int): Maximum width of a single line in string representation.
        '''
        super().__init__(iterable)
        self.max_lines = max_lines
        self.max_width = max_width

    @property
    def n(self) -> int:
        '''
        Get the number of items in the list.

        Returns:
            int: The number of items in the list.
        '''
        return len(self)

    def __repr__(self) -> str:
        '''
        Return a string representation of the CountedList.

        The representation includes the count of items and a formatted list of the contents.
        For large lists, it truncates the output based on max_lines and max_width.

        Returns:
            str: A formatted string representation of the CountedList.
        '''
        # TODO: handle nested structures (lists, dicts, sets) differently.
        count = self.n
        if count == 0:
            return '(#0) []'

        indent_length = 5 + len(f'{count}')  # for '(#X) ['
        indent = ' ' * indent_length

        # try one-line representation
        one_line = f'{repr(self[0])}'
        for item in self[1:]:
            one_line += f', {repr(item)}'
            if len(one_line) + indent_length + 1 > self.max_width:
                break
        if len(one_line) + indent_length + 1 <= self.max_width:
            return f'(#{count}) [{one_line}]'

        # multi-line representation
        if count <= self.max_lines:
            items = ',\n'.join(f'{indent}{repr(item)}' for item in self)
        else:
            items = ',\n'.join(f'{indent}{repr(item)}' for item in self[:self.max_lines - 1])
            items += f',\n{indent}...\n{indent}{repr(self[-1])}'
        items = items[len(indent):]
        return f'(#{count}) [{items}]'

    def __getitem__(self, index):
        '''
        Get item(s) from the CountedList.

        Supports integer indexing, slicing, and list indexing.
        When slicing or using list indexing, it returns a new CountedList.

        Args:
            index: An integer, slice, or list of indices.

        Returns:
            A single item for integer indexing, or a new CountedList for slicing/list indexing.
        '''
        if isinstance(index, list):
            return CountedList([self[i] for i in index])

        result = super().__getitem__(index)
        if isinstance(index, slice):
            return CountedList(result)

        return result

    def sample(self, k: int = 1) -> 'CountedList':
        '''
        Return a new CountedList with a random sample of items from this list.

        Args:
            k (int): The number of items to sample. Defaults to 1.

        Returns:
            CountedList: A new CountedList containing the sampled items.
        '''
        return CountedList(random.sample(self, k=k))


def _ls(
    path: Union[str, 'Path'],
    pattern: str = '',
    purestr: bool = False,
    show_hidden: bool = False,
    depth: int = 1,
    _result: Optional[CountedList] = None,
) -> CountedList:
    '''
    Internal recursive helper for listing directory contents into a single CountedList.

    Uses an accumulator (`_result`) to avoid redundant list allocations across recursion levels.
    Pattern matching is performed using `fnmatch` against the entry name only.

    Args:
        path: The directory path to scan.
        pattern (str): A glob pattern to filter entries by filename (e.g. `'*.jpg'`).
            An empty string means no filtering.
        purestr (bool): If True, items are plain strings instead of Path objects.
        show_hidden (bool): If True, includes hidden files and directories (those starting with `.`).
        depth (int): Remaining recursion depth. 1 means only the immediate directory.
        _result (CountedList | None): Accumulator list; created on the first call.

    Returns:
        CountedList: A flat list of matched paths.
    '''
    if _result is None:
        _result = CountedList()

    if not os.path.exists(path):
        return _result

    for entry in os.scandir(path):
        if not show_hidden and entry.name.startswith('.'):
            continue

        _path = entry.path
        if not pattern or fnmatch.fnmatch(entry.name, pattern):
            _result.append(_path if purestr else Path(_path))

        if entry.is_dir() and depth > 1:
            _ls(_path, pattern, purestr, show_hidden, depth - 1, _result)

    return _result


def _grls(
    path: Union[str, 'Path'],
    pattern: str = '',
    purestr: bool = False,
    show_hidden: bool = False,
    depth: int = 1,
) -> Generator:
    '''
    Internal recursive generator for lazily listing directory contents.

    Yields one entry at a time without building a full list in memory.
    Suitable for large directory trees where full materialisation is expensive.

    Args:
        path: The directory path to scan.
        pattern (str): A glob pattern to filter entries by filename (e.g. `'*.jpg'`).
            An empty string means no filtering.
        purestr (bool): If True, yields plain strings instead of Path objects.
        show_hidden (bool): If True, includes hidden files and directories (those starting with `.`).
        depth (int): Remaining recursion depth. 1 means only the immediate directory.

    Yields:
        str | Path: Matched path entries.
    '''
    if not os.path.exists(path):
        return

    for entry in os.scandir(path):
        if not show_hidden and entry.name.startswith('.'):
            continue

        _path = entry.path
        if not pattern or fnmatch.fnmatch(entry.name, pattern):
            yield _path if purestr else Path(_path)

        if entry.is_dir() and depth > 1:
            yield from _grls(_path, pattern, purestr, show_hidden, depth - 1)


def _ensure_path_compatibility(*paths):
    if PYTHON_VERSION < Version('3.8'):
        paths = tuple(str(path) for path in paths)
    return paths[0] if len(paths) == 1 else paths


class Path(pathlib.WindowsPath if os.name == 'nt' else pathlib.PosixPath):
    '''
    An enhanced subclass of `pathlib.PosixPath` / `pathlib.WindowsPath`.

    Adds shell-like utility methods for listing, copying, moving, and removing
    paths, as well as convenience properties and pattern-based filtering.
    '''
    def __contains__(self, item: str) -> bool:
        '''
        Check if an item exists in the parts of the path.

        Args:
            item (str): A path component to search for.

        Returns:
            bool: True if `item` is one of the path's components.
        '''
        return item in self.parts

    def has(self, item: str) -> bool:
        '''
        Check if a given component exists in the parts of the path.

        Args:
            item (str): A path component to search for.

        Returns:
            bool: True if `item` is one of the path's components.
        '''
        return item in self.parts

    def has_any(self, items: tuple) -> bool:
        '''
        Check if the path contains any of the given components.

        Args:
            items (tuple): Path components to search for.

        Returns:
            bool: True if at least one item from `items` is a path component.
        '''
        return bool(set(items) & set(self.parts))

    def has_all(self, items: tuple) -> bool:
        '''
        Check if the path contains all of the given components.

        Args:
            items (tuple): Path components to search for.

        Returns:
            bool: True if every item in `items` is a path component.
        '''
        return len(set(items) & set(self.parts)) == len(items)

    def change(self, old: str, new: str) -> 'Path':
        '''
        Replace a component in the path and return the resulting new path.

        Args:
            old (str): The component to replace.
            new (str): The replacement component.

        Returns:
            Path: A new Path with `old` replaced by `new`.
        '''
        return self.__class__(*(part if part != old else new for part in self.parts))

    @property
    def str(self) -> str:
        '''
        Return the POSIX string representation of the path.

        Returns:
            str: The path as a string with forward slashes.
        '''
        return str(self)

    def __str__(self) -> str:
        return super().__str__().replace(os.sep, '/')

    def ls(self='.', pattern: str = '', purestr: bool = False, show_hidden: bool = False) -> CountedList:
        '''
        List the immediate children of this directory.

        Hidden entries (names starting with `.`) are excluded by default.
        Pattern matching uses `fnmatch` against the entry name, so glob patterns
        like `'*.jpg'` or `'img_*'` are supported.

        Args:
            pattern (str): A glob pattern to filter results by filename. Defaults to `''` (no filter).
            purestr (bool): If True, returns plain strings instead of Path objects.
            show_hidden (bool): If True, includes hidden files and directories.

        Returns:
            CountedList: Matched entries in the immediate directory.

        Example:
            >>> Path('/data').ls('*.png')
            (#3) [...]
        '''
        return _ls(self, pattern, purestr=purestr, show_hidden=show_hidden, depth=1)

    def rls(self='.', pattern: str = '', purestr: bool = False, show_hidden: bool = False, depth: int = -1) -> CountedList:
        '''
        Recursively list all entries in the directory tree.

        Returns a fully materialised `CountedList`, which is convenient for
        quick inspection in Jupyter Notebooks.  For large trees where lazy
        evaluation is preferred, use `grls` instead.

        Hidden entries (names starting with `.`) are excluded by default.
        Pattern matching uses `fnmatch` against the entry name.

        Args:
            pattern (str): A glob pattern to filter results by filename. Defaults to `''` (no filter).
            purestr (bool): If True, returns plain strings instead of Path objects.
            show_hidden (bool): If True, includes hidden files and directories.
            depth (int): Maximum recursion depth. -1 means unlimited. Defaults to -1.

        Returns:
            CountedList: All matched entries found recursively.

        Example:
            >>> Path('/data').rls('*.jpg')
            (#42) [...]
        '''
        depth = int(depth) if depth >= 0 else 1 << 30
        return _ls(self, pattern, purestr=purestr, show_hidden=show_hidden, depth=depth)

    def grls(self='.', pattern: str = '', purestr: bool = False, show_hidden: bool = False, depth: int = -1) -> Generator:
        '''
        Recursively yield all entries in the directory tree as a generator.

        Unlike `rls`, this method does **not** build a list in memory; it yields
        one entry at a time.  Use this for very large directory trees to avoid
        high memory consumption.

        Hidden entries (names starting with `.`) are excluded by default.
        Pattern matching uses `fnmatch` against the entry name.

        Args:
            pattern (str): A glob pattern to filter results by filename. Defaults to `''` (no filter).
            purestr (bool): If True, yields plain strings instead of Path objects.
            show_hidden (bool): If True, includes hidden files and directories.
            depth (int): Maximum recursion depth. -1 means unlimited. Defaults to -1.

        Yields:
            Path | str: Matched path entries.

        Example:
            >>> for p in Path('/data').grls('*.png'):
            ...     process(p)
        '''
        depth = int(depth) if depth >= 0 else 1 << 30
        yield from _grls(self, pattern, purestr=purestr, show_hidden=show_hidden, depth=depth)

    def cp(self, dst: Union[str, 'Path'], recursive: bool = False) -> 'Path':
        '''
        Copy the file or directory to the given destination.

        Args:
            dst (str | Path): The destination path.
            recursive (bool): If True, copy directories and their contents recursively.

        Returns:
            Path: The destination path as a Path object.

        Raises:
            IsADirectoryError: If trying to copy a directory without `recursive=True`.
        '''
        if self.is_dir():
            if recursive:
                self, dst = _ensure_path_compatibility(self, dst)
                shutil.copytree(self, dst)
            else:
                raise IsADirectoryError('Use recursive=True to copy directories')
        else:
            self, dst = _ensure_path_compatibility(self, dst)
            shutil.copy2(self, dst)

        return Path(dst)

    def rm(self, recursive: bool = False) -> 'Path':
        '''
        Remove the file or directory.

        Args:
            recursive (bool): If True, remove directories and their contents recursively.

        Returns:
            Path: This path object (for chaining).

        Raises:
            OSError: If trying to remove a non-empty directory without `recursive=True`.
        '''
        if self.is_dir():
            if recursive:
                self = _ensure_path_compatibility(self)
                shutil.rmtree(self)
                self = Path(self)
            else:
                try:
                    self.rmdir()
                except OSError as e:
                    raise OSError(
                        f'Directory `{self}` is not empty. Use `recursive=True` to remove non-empty directories'
                    ) from e
        else:
            self.unlink()
        return self

    def mv(self, dst: Union[str, 'Path']) -> 'Path':
        '''
        Move the file or directory to the given destination.

        Args:
            dst (str | Path): The destination path.

        Returns:
            Path: The destination path as a Path object.
        '''
        self, dst = _ensure_path_compatibility(self, dst)
        shutil.move(self, dst)
        return Path(dst)

    def is_folder(self) -> bool:
        '''
        Check if the path refers to a folder.

        Returns:
            bool: True if the path is a directory.
        '''
        return self.is_dir()

    def with_stem(self, stem: str) -> 'Path':
        '''
        Return a new path with the stem changed.

        Provided for compatibility with Python versions earlier than 3.9,
        which lack the built-in `Path.with_stem` method.

        Args:
            stem (str): The new stem (filename without extension).

        Returns:
            Path: A new Path with the stem replaced.
        '''
        return self.with_name(stem + self.suffix)


def get_directory_tree(root: Path = '.', indent: int = 0, verbose: bool = False, depth: int = 1 << 30) -> str:
    '''
    Build a text-based tree representation of a directory structure.

    Args:
        root (Path): The root path to start from.
        indent (int): Number of spaces to indent the current level.
        verbose (bool): If True, prints each line as it is built.
        depth (int): Maximum recursion depth.

    Returns:
        str: The tree as a multi-line string.

    Example:
        >>> print(get_directory_tree(Path('/data'), depth=2))
        |--[D] data
              |--[F] image.png
              |--[D] masks
    '''
    if depth == -1:
        return ''

    root = Path(root)
    tree = f'{" " * indent}|--{"[F]" if root.is_file() else "[D]"} {root.name}\n'
    if verbose:
        print(tree, end='')

    if root.is_dir() and depth > 0:
        for child in sorted(root.iterdir(), key=lambda x: x.name):
            tree += get_directory_tree(child, indent + 6, verbose=verbose, depth=depth - 1)
    return tree
