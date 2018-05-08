import pytest


from pyroofit.observables import extract_from_list


def test_extract_from_list_no_name():
    name, val, lwb, upb = extract_from_list([0, 1])

    assert name is None, "name is not None"
    assert lwb < upb, "Sorting is wrong"


def test_extract_from_list_sorting():
    name, val, lwb, upb = extract_from_list([0, 1])
    print(val)
    assert lwb < upb, "Sorting is wrong"
    assert val==0.5, "Mean calculation wrong"
    assert val < upb, "Sorting is wrong again"


def test_extract_from_list_name():
    name, val, lwb, upb = extract_from_list(['mbc', 0, 1])
    print(val)
    assert name == 'mbc', "Name is wrong"


def test_extract_from_list_all():
    name, val, lwb, upb = extract_from_list(['mbc', 0, 1, -1000])
    print(val)
    assert lwb < upb, "Sorting is wrong"
    assert val == 0, "Mean assosiation wrong"
    assert val < upb, "Sorting is wrong again"
