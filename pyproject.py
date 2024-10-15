[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pathlist"
version = "0.0.3"
description = "A Python library that extends pathlib with enhanced path manipulation and directory listing capabilities."
authors = [
    {name = "susuky", email = "hpisj322@gmail.com"},
]
readme = "README.md"
requires-python = ">=3.6"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
Homepage = "https://github.com/susuky/pathlist"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"*" = ["*.txt", "*.rst"]
