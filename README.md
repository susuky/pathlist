# Pathlist

> **PathList**: A Python library that extends `pathlib` with enhanced path manipulation and directory listing capabilities. Easily navigate, query, and manipulate file system paths with added convenience and flexibility.

**Features:**

- Enhanced `Path` class with additional methods for easy path manipulation.
- Customizable and human-readable directory listing with filtering options.
- Support for recursive file and directory exploration.
- Intuitive and Pythonic interface, compatible with existing `pathlib` usage.

**Installation:**

```bash
pip install pathlist
```

**Quick Start:**

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

---

**About the Project:**

PathList is designed to provide developers with a more powerful and flexible way to work with file system paths. By extending Python's built-in `pathlib`, PathList adds new features like directory listing with filtering, easier path manipulation, and more. It's perfect for developers who need more control and convenience when handling file paths in their projects.

---
