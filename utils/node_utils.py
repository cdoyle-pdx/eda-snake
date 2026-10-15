import eda_config as ecfg
from core.pysrc.toponode import TOPONODE_SCHEMA, TopoNode
import utils.schema as s
from utils.log import log_msg

INCLUDE_DEFAULT = True
INCLUDE_BASE = True


def get_node(name: str, ns: str = None):
    return ecfg.get_cr(
        schema=s.TOPOLOGY_NODE_SCHEMA,
        name=name,
        ns=ns)

def get_toponode(name: str, ns: str = None):
    """Get TopoNode object by its name and namespace"""
    return TopoNode.from_input(get_node(name=name, ns=ns))

# def list_nodes_all_namespaces(filter=[], label_filter=[]):
#     namespace_onboarded_nodes = {}
#     for namespace in ecfg.list_crs(schema=s.NAMESPACE_SCHEMA, filter=filter, label_filter=label_filter):
#         namespace_name = namespace['metadata']['name']
#         namespace_onboarded_nodes[namespace_name] = {}
#         for toponode_cr in ecfg.list_crs(ns=namespace_name, schema=s.TOPOLOGY_NODE_SCHEMA, filter=filter, label_filter=label_filter):
#             if toponode_cr['spec'].get('onBoarded', False):
#                 namespace_onboarded_nodes[namespace_name][toponode_cr['metadata']['name']] = toponode_cr
#             node_name = toponode_cr['metadata']['name']
#             log_msg(f'list_nodes_all_namespaces: node "{node_name}" is not onboarded, skipping it')
#     if INCLUDE_BASE:
#         namespace_onboarded_nodes['_base_'] = {}
#         for toponode_cr in ecfg.list_crs(ns='_base_', schema=s.TOPOLOGY_NODE_SCHEMA, filter=[], label_filter=[]):
#             if toponode_cr['spec'].get('onBoarded', False):
#                 namespace_onboarded_nodes['_base_'][toponode_cr['metadata']['name']] = toponode_cr
#     if INCLUDE_DEFAULT:
#         namespace_onboarded_nodes['default'] = {}
#         for toponode_cr in ecfg.list_crs(ns='default', schema=s.TOPOLOGY_NODE_SCHEMA, filter=[], label_filter=[]):
#             if toponode_cr['spec'].get('onBoarded', False):
#                 namespace_onboarded_nodes['default'][toponode_cr['metadata']['name']] = toponode_cr
#     return namespace_onboarded_nodes


def list_nodes(filter=[], label_filter=[], ns=None):
    return ecfg.list_crs(schema=s.TOPOLOGY_NODE_SCHEMA, filter=filter, label_filter=label_filter, ns=ns)

def list_toponodes(filter=[], label_filter=[], ns=None):
    """List TopoNode objects in a given namespace using a filter and/or a label filter."""
    return [TopoNode.from_input(cr) for cr in list_nodes(filter=filter, label_filter=label_filter, ns=ns)]