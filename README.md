# pathlist

> **pathlist**: A Python library that extends `pathlib` with enhanced path manipulation and directory listing capabilities. Easily navigate, query, and manipulate file system paths with added convenience and flexibility.

## **Features:**

- Enhanced `Path` class with additional methods for easy path manipulation.
- Customizable and human-readable directory listing with filtering options.
- Support for recursive file and directory exploration.
- Intuitive and Pythonic interface, compatible with existing `pathlib` usage.

## **Installation:**

```bash
pip install pathlist
```

## **Quick Start:**

```python
from pathlist import Path

# Create a Path object
path = Path('/some/directory')

# List files in the directory
print(path.ls())

# Recursively list all files in the directory and its subdirectories
print(path.rls())

# Check if a certain part exists in the path
print('folder_name' in path)

# Change parts of the path
new_path = path.change('old_folder', 'new_folder')
```

## Usage Examples
### List Directory Contents
```python
from pathlist import Path

# List all items in the current directory
print(Path().ls())

"""
(#7) [Path('LICENSE'),
      Path('setup.py'),
      Path('src'),
      Path('dist'),
      Path('README.md'),
      Path('test'),
      Path('build')]
"""
```

### List Files with Specific Extension
```python
from pathlist import Path

# List all files with the .py extension in the current directory
print(Path().rls('.py'))

"""
(#7) [Path('setup.py'),
      Path('src/pathlist/__init__.py'),
      Path('src/pathlist/__pycache__/__init__.cpython-310.pyc'),
      Path('src/pathlist/__pycache__/path.cpython-310.pyc'),
      Path('src/pathlist/path.py'),
      Path('build/lib/pathlist/__init__.py'),
      Path('build/lib/pathlist/path.py')]
"""
```

### Get Directory Tree Structure
```python
from pathlist import get_directory_tree

# Print the directory tree structure for the src directory
print(get_directory_tree('src/'))

"""
|--[D] src
      |--[D] pathlist
            |--[F] __init__.py
            |--[D] __pycache__
                  |--[F] __init__.cpython-310.pyc
                  |--[F] path.cpython-310.pyc
            |--[F] path.py
      |--[D] pathlist.egg-info
            |--[F] PKG-INFO
            |--[F] SOURCES.txt
            |--[F] dependency_links.txt
            |--[F] top_level.txt
"""
```

---

**About the Project:**

PathList is designed to provide developers with a more powerful and flexible way to work with file system paths. By extending Python's built-in `pathlib`, PathList adds new features like directory listing with filtering, easier path manipulation, and more. It's perfect for developers who need more control and convenience when handling file paths in their projects.

---
