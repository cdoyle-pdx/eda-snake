#!/usr/bin/env python3
"""Unit tests for EDA schema"""

import eda_common as eda
from utils import schema as s


def test_component_discovery_schema_sanity():
    """Sanity test for COMPONENT_DISCOVERY_SCHEMA"""
    component_discovery_schema = s.COMPONENT_DISCOVERY_SCHEMA
    assert isinstance(component_discovery_schema, eda.Schema)
    assert component_discovery_schema.group == "components.eda.nokia.com"
    assert component_discovery_schema.version == "v2"
    assert component_discovery_schema.kind == "Discovery"


def test_component_schema_sanity():
    """Sanity test for COMPONENT_SCHEMA"""
    component_schema = s.COMPONENT_SCHEMA
    assert isinstance(component_schema, eda.Schema)
    assert component_schema.group == "components.eda.nokia.com"
    assert component_schema.version == "v2"
    assert component_schema.kind == "Component"


def test_configlet_schema_sanity():
    """Sanity test for CONFIGLET_SCHEMA"""
    configlet_schema = s.CONFIGLET_SCHEMA
    assert isinstance(configlet_schema, eda.Schema)
    assert configlet_schema.group == "config.eda.nokia.com"
    assert configlet_schema.version == "v1"
    assert configlet_schema.kind == "Configlet"


def test_interface_schema_sanity():
    """Sanity test for INTERFACE_SCHEMA"""
    interface_schema = s.INTERFACE_SCHEMA
    assert isinstance(interface_schema, eda.Schema)
    assert interface_schema.group == "interfaces.eda.nokia.com"
    assert interface_schema.version == "v1"
    assert interface_schema.kind == "Interface"


def test_interface_state_schema_sanity():
    """Sanity test for INTERFACE_STATE_SCHEMA"""
    interface_state_schema = s.INTERFACE_STATE_SCHEMA
    assert isinstance(interface_state_schema, eda.Schema)
    assert interface_state_schema.group == "interfaces.eda.nokia.com"
    assert interface_state_schema.version == "v1"
    assert interface_state_schema.kind == "InterfaceState"


def test_routed_interface_schema_sanity():
    """Sanity test for ROUTED_INTERFACE_SCHEMA"""
    routed_interface_schema = s.ROUTED_INTERFACE_SCHEMA
    assert isinstance(routed_interface_schema, eda.Schema)
    assert routed_interface_schema.group == "services.eda.nokia.com"
    assert routed_interface_schema.version == "v2"
    assert routed_interface_schema.kind == "RoutedInterface"


def test_filter_deployment_schema_sanity():
    """Sanity test for FILTER_DEPLOYMENT_SCHEMA"""
    filter_deployment_schema = s.FILTER_DEPLOYMENT_SCHEMA
    assert isinstance(filter_deployment_schema, eda.Schema)
    assert filter_deployment_schema.group == "filters.eda.nokia.com"
    assert filter_deployment_schema.version == "v1"
    assert filter_deployment_schema.kind == "FilterDeployment"


def test_filter_schema_sanity():
    """Sanity test for IP_FILTER_SCHEMA"""
    schema = s.FILTER_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "filters.eda.nokia.com"
    assert schema.version == "v1"
    assert schema.kind == "Filter"
    schema = s.FILTER_DEPLOYMENT_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "filters.eda.nokia.com"
    assert schema.version == "v1"
    assert schema.kind == "FilterDeployment"
    schema = s.CONTROL_PLANE_FILTER_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "filters.eda.nokia.com"
    assert schema.version == "v1"
    assert schema.kind == "ControlPlaneFilter"
    schema = s.MIRROR_FILTER_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "filters.eda.nokia.com"
    assert schema.version == "v1"
    assert schema.kind == "MirrorFilter"
    schema = s.MIRROR_FILTER_DEPLOYMENT_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "filters.eda.nokia.com"
    assert schema.version == "v1"
    assert schema.kind == "MirrorFilterDeployment"


def test_qos_schema_sanity():
    """Sanity test for MAC_FILTER_SCHEMA"""
    schema = s.QOS_INGRESS_POLICY_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "qos.eda.nokia.com"
    assert schema.version == "v2"
    assert schema.kind == "IngressPolicy"
    schema = s.QOS_EGRESS_POLICY_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "qos.eda.nokia.com"
    assert schema.version == "v2"
    assert schema.kind == "EgressPolicy"
    schema = s.QOS_INGRESS_POLICY_DEPLOYER_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "qos.eda.nokia.com"
    assert schema.version == "v2"
    assert schema.kind == "IngressPolicyDeployment"
    schema = s.QOS_EGRESS_POLICY_DEPLOYER_SCHEMA
    assert isinstance(schema, eda.Schema)
    assert schema.group == "qos.eda.nokia.com"
    assert schema.version == "v2"
    assert schema.kind == "EgressPolicyDeployment"


def test_package_schema_sanity():
    """Sanity test for PACKAGE_SCHEMA"""
    package_schema = s.PACKAGE_SCHEMA
    assert isinstance(package_schema, eda.Schema)
    assert package_schema.group == "packages.eda.nokia.com"
    assert package_schema.version == "v1alpha1"
    assert package_schema.kind == "Package"


def test_vnet_schema_sanity():
    """Sanity test for VNET_SCHEMA"""
    vnet_schema = s.VNET_SCHEMA
    assert isinstance(vnet_schema, eda.Schema)
    assert vnet_schema.group == "services.eda.nokia.com"
    assert vnet_schema.version == "v2"
    assert vnet_schema.kind == "VirtualNetwork"


def test_bd_schema_sanity():
    """Sanity test for BRIDGE_DOMAIN_SCHEMA"""
    bd_schema = s.BRIDGE_DOMAIN_SCHEMA
    assert isinstance(bd_schema, eda.Schema)
    assert bd_schema.group == "services.eda.nokia.com"
    assert bd_schema.version == "v2"
    assert bd_schema.kind == "BridgeDomain"


def test_router_schema_sanity():
    """Sanity test for ROUTER_SCHEMA"""
    router_schema = s.ROUTER_SCHEMA
    assert isinstance(router_schema, eda.Schema)
    assert router_schema.group == "services.eda.nokia.com"
    assert router_schema.version == "v2"
    assert router_schema.kind == "Router"


def test_router_attachment_schema_sanity():
    """Sanity test for ROUTER_ATTACHMENT_SCHEMA"""
    router_attachment_schema = s.ROUTER_ATTACHMENT_SCHEMA
    assert isinstance(router_attachment_schema, eda.Schema)
    assert router_attachment_schema.group == "services.eda.nokia.com"
    assert router_attachment_schema.version == "v2"
    assert router_attachment_schema.kind == "RouterAttachment"


def test_config_schema_sanity():
    """Sanity test for CONFIG_SCHEMA"""
    config_schema = s.CONFIG_SCHEMA
    assert isinstance(config_schema, eda.Schema)
    assert config_schema.group == "core.eda.nokia.com"
    assert config_schema.version == "v1"
    assert config_schema.kind == "NodeConfig"


def test_topology_node_schema_sanity():
    """Sanity test for TOPOLOGY_NODE_SCHEMA"""
    topology_node_schema = s.TOPOLOGY_NODE_SCHEMA
    assert isinstance(topology_node_schema, eda.Schema)
    assert topology_node_schema.group == "core.eda.nokia.com"
    assert topology_node_schema.version == "v1"
    assert topology_node_schema.kind == "TopoNode"


def test_target_node_schema_sanity():
    """Sanity test for TARGET_NODE_SCHEMA"""
    target_node_schema = s.TARGET_NODE_SCHEMA
    assert isinstance(target_node_schema, eda.Schema)
    assert target_node_schema.group == "core.eda.nokia.com"
    assert target_node_schema.version == "v1"
    assert target_node_schema.kind == "TargetNode"


def test_pod_schema_sanity():
    """Sanity test for POD_SCHEMA"""
    pod_schema = s.POD_SCHEMA
    assert isinstance(pod_schema, eda.Schema)
    assert pod_schema.group == ""
    assert pod_schema.version == "v1"
    assert pod_schema.kind == "Pod"


def test_deployment_schema_sanity():
    """Sanity test for DEPLOYMENT_SCHEMA"""
    deployment_schema = s.DEPLOYMENT_SCHEMA
    assert isinstance(deployment_schema, eda.Schema)
    assert deployment_schema.group == "apps"
    assert deployment_schema.version == "v1"
    assert deployment_schema.kind == "Deployment"


if __name__ == "__main__":
    test_component_discovery_schema_sanity()
    test_component_schema_sanity()
    test_configlet_schema_sanity()
    test_interface_schema_sanity()
    test_interface_state_schema_sanity()
    test_routed_interface_schema_sanity()
    test_filter_deployment_schema_sanity()
    test_filter_schema_sanity()
    test_qos_schema_sanity()
    test_package_schema_sanity()
    test_vnet_schema_sanity()
    test_bd_schema_sanity()
    test_router_schema_sanity()
    test_router_attachment_schema_sanity()
    test_config_schema_sanity()
    test_topology_node_schema_sanity()
    test_target_node_schema_sanity()
    test_pod_schema_sanity()
    test_deployment_schema_sanity()
