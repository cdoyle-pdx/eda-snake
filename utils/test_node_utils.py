#!/usr/bin/env python3

import eda_config as ecfg
from utils import schema
from utils.node_utils import get_node, get_toponode, list_toponodes
from common.constants import PLATFORM_SRL
from core.pysrc.toponode import TopoNode


def _make_node_cr(name: str, version: str = "23.3.1", on_boarded: bool = False):
    return {
        "metadata": {
            "name": name
        },
        "spec": {
            "operatingSystem": PLATFORM_SRL,
            "version": version,
            "onBoarded": on_boarded
        }
    }


def test_get_node_sanity():
    val_dut1 = 'dut1'
    ecfg.test_addcr(schema.TOPOLOGY_NODE_SCHEMA, _make_node_cr(val_dut1))
    assert get_node(val_dut1) is not None
    ecfg.test_clear_all()


def test_get_toponode_sanity():
    val_dut1 = 'dut1'
    ecfg.test_addcr(schema.TOPOLOGY_NODE_SCHEMA, _make_node_cr(val_dut1))
    node = get_toponode(val_dut1)
    assert isinstance(node, TopoNode)
    assert node.metadata.name == val_dut1
    assert node.spec.version == "23.3.1"
    assert get_toponode('does-not-exist') is None
    ecfg.test_clear_all()

def test_list_toponodes_sanity():
    assert list_toponodes() == []
    ecfg.test_addcr(schema.TOPOLOGY_NODE_SCHEMA, _make_node_cr('dut1'))
    ecfg.test_addcr(schema.TOPOLOGY_NODE_SCHEMA, _make_node_cr('dut2'))
    nodes = list_toponodes()
    assert len(nodes) == 2
    assert all(isinstance(n, TopoNode) for n in nodes)
    assert {n.metadata.name for n in nodes} == {'dut1', 'dut2'}
    ecfg.test_clear_all()


if __name__ == '__main__':
    test_get_node_sanity()
    test_get_toponode_sanity()
    test_list_toponodes_sanity()
