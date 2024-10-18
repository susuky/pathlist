
import os
import pytest
import shutil

from pathlist import Path, get_directory_tree


@pytest.fixture
def tmp_path(tmp_path_factory):
    path = tmp_path_factory.mktemp('data')
    yield Path(path)
    shutil.rmtree(str(path))


def test_contains(tmp_path):
    p = tmp_path / 'some_folder' / 'file.txt'
    p.parent.mkdir()
    p.touch()
    assert 'some_folder' in p


def test_has(tmp_path):
    p = tmp_path / 'some_folder' / 'file.txt'
    p.parent.mkdir()
    p.touch()
    assert p.has('some_folder')
    assert not p.has('missing_folder')


def test_has_any(tmp_path):
    p = tmp_path / 'some_folder' / 'file.txt'
    p.parent.mkdir()
    p.touch()
    assert p.has_any(('some_folder', 'another_folder'))
    assert not p.has_any(('missing_folder', 'other_missing'))


def test_has_all(tmp_path):
    p = tmp_path / 'some_folder' / 'file.txt'
    p.parent.mkdir()
    p.touch()
    assert p.has_all(('some_folder', 'file.txt'))
    assert not p.has_all(('some_folder', 'missing_file'))


def test_change(tmp_path):
    p = tmp_path / 'old_folder' / 'file.txt'
    p.parent.mkdir()
    p.touch()
    new_p = p.change('old_folder', 'new_folder')
    assert str(new_p) == str(tmp_path / 'new_folder' / 'file.txt')


def test_str(tmp_path):
    p = tmp_path / 'file.txt'
    p.touch()
    assert p.str == str(p).replace(os.sep, '/')


def test_ls(tmp_path):
    (tmp_path / 'file1.txt').touch()
    (tmp_path / 'file2.txt').touch()
    files = tmp_path.ls()
    assert len(files) == 2
    assert all(isinstance(f, Path) for f in files)


def test_rls(tmp_path):
    sub_dir = tmp_path / 'subdir'
    sub_dir.mkdir()
    for i in range(10):
        (sub_dir / f'file{i}.txt').touch()
    files = tmp_path.rls()
    assert len(files) == 10+1
    assert all(isinstance(f, Path) for f in files)
    assert len(tmp_path.rls('.txt')) == 10


def test_cp(tmp_path):
    src = tmp_path / 'file.txt'
    dst = tmp_path / 'copy.txt'
    src.touch()
    new_path = src.cp(dst)
    assert new_path.exists()
    assert new_path == dst


def test_rm(tmp_path):
    p = tmp_path / 'file.txt'
    p.touch()
    assert p.exists()
    p.rm()
    assert not p.exists()


def test_mv(tmp_path):
    src = tmp_path / 'file.txt'
    dst = tmp_path / 'moved_file.txt'
    src.touch()
    new_path = src.mv(dst)
    assert not src.exists()
    assert new_path.exists()
    assert new_path == dst


def test_is_folder(tmp_path):
    p = tmp_path / 'folder'
    p.mkdir()
    assert p.is_folder()


def test_with_stem(tmp_path):
    p = tmp_path / 'file.txt'
    p.touch()
    new_p = p.with_stem('new_file')
    assert new_p.name == 'new_file.txt'
    assert new_p.parent == p.parent


def test_get_directory_tree(tmp_path):
    root = tmp_path / 'root'
    root.mkdir()
    (root / 'file1.txt').touch()
    sub_dir = root / 'subdir'
    sub_dir.mkdir()
    (sub_dir / 'file2.txt').touch()

    expected_output = (
        '|--[D] root\n'
        '      |--[F] file1.txt\n'
        '      |--[D] subdir\n'
        '            |--[F] file2.txt\n'
    )
    assert get_directory_tree(root, indent=0, verbose=False, depth=2) == expected_output

