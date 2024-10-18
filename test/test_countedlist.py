
import pytest

from pathlist import CountedList


def test_init():
    cl = CountedList([1, 2, 3])
    assert cl.n == 3
    assert cl == [1, 2, 3]
    assert cl.max_lines == 15
    assert cl.max_width == 120


def test_init_with_custom_values():
    cl = CountedList([1, 2, 3], max_lines=10, max_width=100)
    assert cl.max_lines == 10
    assert cl.max_width == 100


def test_n():
    cl = CountedList([1, 2, 3])
    assert cl.n == 3
    cl.append(4)
    assert cl.n == 4


def test_repr_empty():
    cl = CountedList()
    assert repr(cl) == '(#0) []'
    assert cl.n == 0
    assert len(cl) == 0


def test_repr_small_list():
    cl = CountedList([1, 2, 3])
    assert repr(cl) == '(#3) [1, 2, 3]'


def test_repr_large_list():
    cl = CountedList(range(1000), max_lines=5)
    repr_str = repr(cl)
    assert repr_str == '(#1000) [0,\n         1,\n         2,\n         3,\n         ...\n         999]'  


@pytest.mark.parametrize('max_lines', [5, 10, 15])
def test_repr_with_line_limit(max_lines):
    cl = CountedList([i for i in range(1000)], max_lines=max_lines)
    repr_str = repr(cl)
    assert len(repr_str.split('\n')) <= max_lines+1
    

@pytest.mark.parametrize('max_width', [20, 80, 120])
def test_repr_with_width_limit(max_width):
    cl = CountedList([i for i in range(1000)], max_width=max_width)
    repr_str = repr(cl)
    for line in repr_str.split('\n'):
        assert len(line) < max_width


def test_getitem_single():
    cl = CountedList([1, 2, 3])
    assert cl[0] == 1
    assert cl[2] == 3


def test_getitem_slice():
    cl = CountedList([1, 2, 3, 4, 5])
    sliced_cl = cl[1:4]
    assert isinstance(sliced_cl, CountedList)
    assert sliced_cl == [2, 3, 4]
    assert sliced_cl.n == 3


def test_getitem_list_index():
    cl = CountedList([1, 2, 3, 4, 5])
    indexed_cl = cl[[0, 2, 4]]
    assert isinstance(indexed_cl, CountedList)
    assert indexed_cl == [1, 3, 5]


def test_sample():
    cl = CountedList([1, 2, 3, 4, 5])
    sample_cl = cl.sample(3)
    assert isinstance(sample_cl, CountedList)
    assert sample_cl.n == 3
    assert set(sample_cl).issubset(cl)
