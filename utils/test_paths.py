#!/usr/bin/env python3
"""Unit tests for EDA paths"""

from utils import paths
from common_testing import compare_common

INPUT_PATH_1 = \
    '.node{.name=="dut1"}' \
    '.srl{.version=="22.11.1"}' \
    '.interface{.name=="ethernet-1/3"}'
INPUT_PATH_2 = \
    '.node{.name=="dut2"}' \
    '.sros{.version=="23.12.1"}' \
    '.interface{.name=="ethernet-2/1"}'
INPUT_PATH_3 = \
    '.node{.name=="dut3"}' \
    '.srl{.version=="24.10.2"}' \
    '.ports{.number==20}'


def test_remove_keys_from_path():
    """Sanity test for function remove_keys_from_path"""
    assert paths.remove_keys_from_path(INPUT_PATH_1) == '.node.srl.interface'


def test_path_prefix_match_sanity():
    """Sanity test for function path_prefix_match"""
    assert paths.path_prefix_match(INPUT_PATH_1, ".node") is True


def test_nearest_ancestor_key_value_sanity():
    """Sanity test for function nearest_ancestor_key_value"""
    key, value = paths.nearest_ancestor_key_value(INPUT_PATH_1)
    assert key == "name"
    assert value == "ethernet-1/3"
    key, value = paths.nearest_ancestor_key_value('Error string')
    assert key is None
    assert value is None


# def test_extract_node_from_path_sanity():
#     """Sanity test for function extract_node_from_path"""
#     result_dict_1 = paths.extract_node_from_path(INPUT_PATH_1)
#     assert result_dict_1['node'] == "dut1"
#     assert result_dict_1['srl'] == "22.11.1"
#     assert result_dict_1['interface'] == "ethernet-1/3"
#     assert result_dict_1['path'] == '.node{.name=="dut1"}.srl{.version=="22.11.1"}.interface{.name=="ethernet-1/3"}'
#     result_dict_2 = paths.extract_node_from_path(INPUT_PATH_2)
#     expected_dict_2 = {
#         'node': 'dut2',
#         'sros': '23.12.1',
#         'interface': 'ethernet-2/1',
#         'path': '.node{.name=="dut2"}.sros{.version=="23.12.1"}.interface{.name=="ethernet-2/1"}'
#     }
#     assert compare_common(result_dict_2, expected_dict_2) is True


# def test_path_to_dict_sanity():
#     """Sanity test for function path_to_dict"""
#     assert paths.path_to_dict(INPUT_PATH_1) == {
#         'node': {
#             'name': 'dut1'
#         },
#         'srl': {
#             'version': '22.11.1'
#         },
#         'interface': {
#             'name': 'ethernet-1/3'
#         }
#     }
#     assert paths.path_to_dict(INPUT_PATH_3) == {
#         'node': {
#             'name': 'dut3'
#         },
#         'srl': {
#             'version': '24.10.2'
#         },
#         'ports': {
#             'number': 20
#         }
#     }


if __name__ == "__main__":
    test_remove_keys_from_path()
    test_path_prefix_match_sanity()
    test_nearest_ancestor_key_value_sanity()
    # test_extract_node_from_path_sanity()
    # test_path_to_dict_sanity()
