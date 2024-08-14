
from setuptools import setup, find_packages

setup(
    name='pathlist',
    version='0.0.2',
    description='A Python library that extends pathlib with enhanced path manipulation and directory listing capabilities.',
    author='susuky',
    author_email='hpisj322@gmail.com',
    url='https://github.com/susuky/pathlist',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[],
    test_suite='test',
)
