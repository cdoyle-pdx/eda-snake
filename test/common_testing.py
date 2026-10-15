#!/usr/bin/env python3
"""Module to support Pytest"""

import os
import json
import eda_common as eda
from utils.log import log_msg
try:
    from copy import deepcopy
except ImportError:
    from utils.copy import json_deep_copy as deepcopy

try:
    class SchemaJSONEncoder(json.JSONEncoder):
        """Schema JSON encoder"""

        def default(self, o):
            if isinstance(o, eda.Schema):
                return o.__dict__
            return super().default(o)
except AttributeError:
    # Running in MicroPython
    pass


def compare_common(value_1, value_2) -> bool:
    """Function to compare 2 values"""
    if isinstance(value_1, str) is True and isinstance(value_2, str) is True:
        if compare_strings(value_1, value_2) is False:
            return False
    elif isinstance(value_1, dict) is True and isinstance(value_2, dict) is True:
        if compare_dicts(value_1, value_2) is False:
            return False
    elif isinstance(value_1, list) is True and isinstance(value_2, list) is True:
        if compare_lists(value_1, value_2) is False:
            return False
    elif value_1 != value_2:
        return False
    return True


def compare_strings(str_1, str_2) -> bool:
    """Function to compare 2 strings checking if string values can be converted to dict using json module"""
    if isinstance(str_1, str) is False:
        raise ValueError('Parameter str_1 is not a string, check function call')
    if isinstance(str_2, str) is False:
        raise ValueError('Parameter str_2 is not a string, check function call')
    if len(str_1) != len(str_2):
        return False
    try:
        json_1 = json.loads(str_1)
        json_2 = json.loads(str_2)
    except:  # noqa
        if str_1 != str_2:
            return False
    else:
        if compare_common(json_1, json_2) is False:
            return False
    return True


def compare_dicts(dict_1, dict_2) -> bool:
    """Function to compare 2 dicts ignoring order and checking if string values can be converted to dict using json module"""
    if isinstance(dict_1, dict) is False:
        raise ValueError('Parameter dict_1 is not a dict, check function call')
    if isinstance(dict_2, dict) is False:
        raise ValueError('Parameter dict_2 is not a dict, check function call')
    if len(dict_1) != len(dict_2):
        return False
    keys_1 = sorted(dict_1.keys())
    keys_2 = sorted(dict_2.keys())
    if keys_1 != keys_2:
        return False
    for key in keys_1:
        if compare_common(dict_1[key], dict_2[key]) is False:
            return False
    return True


def compare_lists(list_1, list_compare) -> bool:
    """Function to compare 2 lists ignoring order of the lists.\n
    list_1 is the result and list_compare is the expected outcome."""
    if isinstance(list_1, list) is False:
        raise ValueError('Parameter list_1 is not a list, check function call')
    if isinstance(list_compare, list) is False:
        raise ValueError('Parameter list_compare is not a list, check function call')
    list_2 = deepcopy(list_compare)
    if len(list_1) != len(list_2):
        return False
    for value_1 in list_1:
        j = 0
        flag = False
        while j < len(list_2):
            value_2 = list_2[j]
            if compare_common(value_1, value_2) is True:
                _ = list_2.pop(j)
                flag = True
                break
            j += 1
        if flag is False:
            return False
    return True


def assert_with_msg(msg, actual_val, expected_val):
    """Function to compare and assert with message"""
    log_msg(f"asserting: {msg}")
    assert compare_common(actual_val, expected_val) is True, f'\nfound   : {actual_val}, \nexpected: {expected_val}'


def assert_any_with_msg(msg, actual_val, *expected_vals):
    """Function to compare and assert with message"""
    if eda.DEBUG:
        print(f"asserting: {msg}")
        print("matching one of the following:")
        for i, exp_val in enumerate(expected_vals):
            print(f"expected value {i} => {exp_val}")
    assert any([compare_common(actual_val, val) for val in expected_vals]), f'\nfound   : {actual_val}'


def assert_raises(exception_type, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except exception_type:
        log_msg(f"Test passed: {exception_type.__name__} was raised as expected")
    else:
        raise AssertionError(f"Test failed: {exception_type.__name__} was not raised")
