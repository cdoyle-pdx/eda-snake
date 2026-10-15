#!/usr/bin/env python3
"""Unit tests for MicroPython Deep Copy"""

from utils.copy import json_deep_copy as deepcopy
from eda_common import Schema


def check_deep_copy(data_1, data_2) -> bool:
    """Function to validate deep copy of data_1 and data_2"""
    if id(data_1) == id(data_2):
        return False
    key_list = []
    if isinstance(data_1, list) is True and isinstance(data_2, list) is True:
        if len(data_1) != len(data_2):
            raise AssertionError('data_1 and data_2 not equal size lists')
        key_list = range(len(data_1))
    elif isinstance(data_1, dict) is True and isinstance(data_2, dict) is True:
        if sorted(data_1.keys()) != sorted(data_2.keys()):
            raise AssertionError('data_1 and data_2 do not have identical dict keys')
        key_list = data_1.keys()
    else:
        assert TypeError(f'Cannot process data types:\ndata_1: {type(data_1)}\ndata_2: {type(data_2)}')
    for key in key_list:
        if isinstance(data_1[key], list) is True or isinstance(data_1[key], dict) is True or isinstance(data_1[key], Schema) is True:
            if id(data_1[key]) == id(data_2[key]):
                return False
    return True


def test_deep_copy_1():
    """Unit test deep copy sanity test 1"""
    list_1 = [1, 2, 3, 4, 5]
    list_2 = deepcopy(list_1)
    assert check_deep_copy(list_1, list_2) is True


def test_deep_copy_2():
    """Unit test deep copy sanity test 2"""
    list_1 = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    list_2 = deepcopy(list_1)
    assert check_deep_copy(list_1, list_2) is True


def test_deep_copy_3():
    """Unit test deep copy sanity test 3"""
    list_1 = [
        1,
        'test-string',
        [
            2,
            'test-string'
        ],
        {
            'test-key1': 'test-value1',
            'test-key2': 'test-value2'
        }
    ]
    list_2 = deepcopy(list_1)
    assert check_deep_copy(list_1, list_2) is True


def test_deep_copy_4():
    """Unit test deep copy sanity test 4"""
    dict_1 = {
        "test-key1": "test-key2",
        "test-key2": 1,
        "test-key3": [1, 2, 3],
        "test-key4": {
            "test-key5": 1
        }
    }
    dict_2 = deepcopy(dict_1)
    assert check_deep_copy(dict_1, dict_2) is True


def test_deep_copy_5():
    """Unit test deep copy sanity test 5"""
    assert deepcopy(None) is None


def main():
    """Main function"""
    test_deep_copy_1()
    test_deep_copy_2()
    test_deep_copy_3()
    test_deep_copy_4()
    test_deep_copy_5()


if __name__ == '__main__':
    main()
