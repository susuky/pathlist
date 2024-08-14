
import os
import pathlib
import platform
import random
import shutil

from packaging.version import Version


PYTHON_VERSION = Version(platform.python_version())


class CountedList(list):
    def __repr__(self):
        max_lines = 15
        count = len(self)
        indent = ' ' * (5 + len(f'{count}'))
        suffix = f',\n{indent}...' if count > max_lines else ''
        
        r = super().__repr__()
        r = f',\n{indent}'.join(r[1:-1].split(', ')[:max_lines])
        return f'(#{count}) [{r}{suffix}]'

    def __getitem__(self, index):
        if isinstance(index, list):
            return CountedList([self[i] for i in index])
        
        result = super().__getitem__(index)
        if isinstance(index, slice):
            return CountedList(result)
        
        # Like the normal list, it return a component instead of a list object.
        return result
        
    def sample(self, k=1):
        return CountedList(random.sample(self, k=k))
        
def _ls(path, pattern='', purestr=False, depth=1):
    result = CountedList()

    if not os.path.exists(path):
        return result

    for entry in os.scandir(path):
        if entry.name.startswith('.'):
            continue

        _path = entry.path
        if pattern in _path:
            result.append(_path if purestr else Path(_path))
        if entry.is_dir() and depth > 1:
            result.extend(_ls(_path, pattern, purestr, depth - 1))
    return result


def _ensure_path_compatibility(*paths):
    if PYTHON_VERSION < Version('3.8'):
        paths = tuple(str(path) for path in paths)
    return paths[0] if len(paths) == 1 else paths


class Path(pathlib.WindowsPath if os.name == 'nt' else pathlib.PosixPath):
    '''
    A subclass of the built-in `pathlib` module's WindowsPath or PosixPath class.
    This class adds additional methods to the built-in class to allow for 
    easier manipulation and querying of paths.
    '''    
    def __contains__(self, item):
        '''
        Checks if an item exists in the parts of the path.
        '''
        return item in self.parts

    def has(self, item):
        '''
        Checks if a given item exists in the parts of the path

        :param item: string
        :return: bool
        '''
        return item in self.parts

    def has_any(self, items: tuple):
        '''
        Checks if the path has any items from a given tuple
        
        :param items: tuple of strings
        :return: bool
        '''
        return bool(set(items) & set(self.parts))

    def has_all(self, items: tuple):
        '''
        Checks if the path has all items from a given tuple
        
        :param items: tuple of strings
        :return: bool
        '''
        return len((set(items) & set(self.parts))) == len(items)

    def change(self, old, new):
        '''
        Replaces an old item with a new item in the parts of the path 
        and returns the new path

        :param old: string
        :param new: string
        :return: Path object
        '''
        return self.__class__(*(part if part != old else new for part in self.parts))
    
    @property
    def str(self):
        '''
        Return the string representation of the path.

        :return: string
        '''
        return str(self) # self.as_posix()
        
    def __str__(self):
        return super().__str__().replace(os.sep, '/')
        
    def ls(self='.', pattern='', purestr=False):
        '''
        List all the files in the directory specified by the path, 
        excluding hidden files, and filtered based on an optional pattern

        :param pattern: string, optional
            Filter the files returned based on the given pattern.
        :return: list of Path objects
        '''
        return _ls(self, pattern, purestr=purestr, depth=1)

    def rls(self='.', pattern='', purestr=False, depth=-1):
        '''
        List all the files in the directory tree specified by the path, 
        excluding hidden files, and filtered based on an optional pattern.

        The `rls` method can be slow for large directories

        :param pattern: string, optional
            Filter the files returned based on the given pattern.
        :return: list of Path objects
        '''
        depth = int(depth) if depth >= 0 else 1 << 30
        return _ls(self, pattern, purestr=purestr, depth=depth)
    
    def cp(self, dst, recursive=False):
        '''
        Copy the file or directory to the given destination.

        :param dst: The destination path.
        :type dst: str or Path
        :param recursive: If True, copy directories and their contents recursively.
        :type recursive: bool
        :raises IsADirectoryError: If trying to copy a directory without recursive=True.
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
    
    def rm(self, recursive=False):
        '''
        Remove the file or directory.

        :param recursive: If True, remove directories and their contents recursively.
        :type recursive: bool
        :raises OSError: If trying to remove a non-empty directory without recursive=True.
        '''
        if self.is_dir():
            if recursive:
                self = _ensure_path_compatibility(self)
                shutil.rmtree(self)
                self = Path(self)
            else:
                self.rmdir()
        else:
            self.unlink()
        return self

    def mv(self, dst):
        '''
        Move the file or directory to the given destination.

        :param dst: The destination path.
        :type dst: str or Path object
        :return: Path object
        '''
        self, dst = _ensure_path_compatibility(self, dst)
        shutil.move(self, dst)
        return Path(dst)

    def is_folder(self):
        '''
        Check if the path refers to a folder.

        :return: bool
        '''
        return self.is_dir()
    
    def with_stem(self, stem: str):
        '''
        Return a new path with the stem changed.

        To support python version < 3.9
        '''
        return self.with_name(stem + self.suffix)
    

def get_directory_tree(root: Path = '.', indent=0, verbose=False, depth=1<<30):
    if depth == -1:
        return ''

    root = Path(root)
    tree = f'{" " * indent}|--{"[F]" if root.is_file() else "[D]"} {root.name}\n'
    if verbose:
        print(tree, end='')

    if root.is_dir() and depth > 0:
        for child in sorted(root.iterdir(), key=lambda x: x.name):
            tree += get_directory_tree(child,
                                         indent + 6,
                                         verbose=verbose,
                                         depth=depth - 1)
    return tree

