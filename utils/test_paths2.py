#!/usr/bin/env python3
"""Unit tests for EDA paths 2"""

from utils.paths2 import JPathParser
from common_testing import compare_common
from common.constants import PLATFORM_SRL, PLATFORM_SROS

INPUT_PATH_1 = \
    '.node{.name=="dut1"}' \
    '.' + PLATFORM_SRL + '{.version=="22.11.1"}' \
    '.interface{.name=="ethernet-1/3"}'
INPUT_PATH_2 = \
    '.node{.name=="dut2"}' \
    '.' + PLATFORM_SROS + '{.version=="23.12.1"}' \
    '.interface{.name=="ethernet-2/1"}'
INPUT_PATH_3 = \
    '.node{.name=="dut3"}' \
    '.srl{.version=="24.10.2"}' \
    '.ports{.number==20}'


def test_jpathparser_sanity():
    """Sanity test for class JPathParser"""
    jpathparser_obj = JPathParser(INPUT_PATH_1)
    assert jpathparser_obj.jpath == INPUT_PATH_1
    assert compare_common(jpathparser_obj.nodes, ['node', PLATFORM_SRL, 'interface']) is True
    assert compare_common(jpathparser_obj.keys, ['name', 'version', 'name']) is True
    assert compare_common(jpathparser_obj.values, ['dut1', '22.11.1', 'ethernet-1/3']) is True
    expected_dict = {
        'node': {
            'key': 'name',
            'value': 'dut1'
        },
        'srl': {
            'key': 'version',
            'value': '22.11.1'
        },
        'interface': {
            'key': 'name',
            'value': 'ethernet-1/3'
        }
    }
    assert compare_common(jpathparser_obj.nodes_with_keys, expected_dict) is True
    assert compare_common(jpathparser_obj.get_nodes(), ['node', PLATFORM_SRL, 'interface']) is True
    assert compare_common(jpathparser_obj.get_nodes_with_keys(), expected_dict) is True
    assert compare_common(jpathparser_obj.get_keys(), ['name', 'version', 'name']) is True
    assert compare_common(jpathparser_obj.get_values(), ['dut1', '22.11.1', 'ethernet-1/3']) is True
    expected_dict = {
        'node': 'dut1',
        'srl': '22.11.1',
        'interface': 'ethernet-1/3'
    }
    assert compare_common(jpathparser_obj.get_nodes_with_values(), expected_dict) is True
    assert jpathparser_obj.get_last_node() == 'interface'
    assert jpathparser_obj.get_last_key() == 'name'
    assert jpathparser_obj.get_last_value() == 'ethernet-1/3'


if __name__ == "__main__":
    test_jpathparser_sanity()
