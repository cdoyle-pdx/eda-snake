#!/usr/bin/env python3

import eda_common as p

# Package objects
NAMESPACE_SCHEMA = p.Schema(group='core.eda.nokia.com',
                            version='v1',
                            kind='Namespace')
NODE_USER_SCHEMA = p.Schema(group='core.eda.nokia.com',
                            version='v1',
                            kind='NodeUser')
NODE_USER_STATE_SCHEMA = p.Schema(group='aaa.eda.nokia.com',
                                  version='v1',
                                  kind='NodeUserState')
NODE_GROUP_SCHEMA = p.Schema(group='aaa.eda.nokia.com',
                             version='v1',
                             kind='NodeGroup')
NODE_GROUP_DEPLOYMENT_SCHEMA = p.Schema(group='aaa.eda.nokia.com',
                                        version='v1',
                                        kind='NodeGroupDeployment')
SYSTEM_MONITOR_SCHEMA = p.Schema(group='system.eda.nokia.com',
                                 version='v1alpha1',
                                 kind='Monitor')
SYSTEM_MONITOR_STATE_SCHEMA = p.Schema(group='system.eda.nokia.com',
                                       version='v1alpha1',
                                       kind='MonitorState')
SYSTEM_MONITOR_AGGREGATE_STATE_SCHEMA = p.Schema(group='system.eda.nokia.com',
                                                 version='v1alpha1',
                                                 kind='MonitorAggregateState')
BANNER_SCHEMA = p.Schema(group='siteinfo.eda.nokia.com',
                         version='v1',
                         kind='Banner')
BANNER_STATE_SCHEMA = p.Schema(group='siteinfo.eda.nokia.com',
                               version='v1',
                               kind='BannerState')
COMPONENT_DISCOVERY_SCHEMA = p.Schema(group='components.eda.nokia.com',
                                      version='v2',
                                      kind='Discovery')
COMPONENT_DISCOVERY_STATE_SCHEMA = p.Schema(group='components.eda.nokia.com',
                                            version='v2',
                                            kind='DiscoveryState')
COMPONENT_DISCOVERY_AGGREGATE_STATE_SCHEMA = p.Schema(group='components.eda.nokia.com',
                                                      version='v2',
                                                      kind='DiscoveryAggregateState')
COMPONENT_SCHEMA = p.Schema(group='components.eda.nokia.com',
                            version='v2',
                            kind='Component')
CONFIGLET_SCHEMA = p.Schema(group='config.eda.nokia.com',
                            version='v1',
                            kind='Configlet')
CONFIGLET_STATE_SCHEMA = p.Schema(group='config.eda.nokia.com',
                                  version='v1',
                                  kind='ConfigletState')
INTERFACE_SCHEMA = p.Schema(group='interfaces.eda.nokia.com',
                            version='v1',
                            kind='Interface')
INTERFACE_STATE_SCHEMA = p.Schema(group='interfaces.eda.nokia.com',
                                  version='v1',
                                  kind='InterfaceState')
ROUTED_INTERFACE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                   version='v2',
                                   kind='RoutedInterface')
FILTER_DEPLOYMENT_SCHEMA = p.Schema(group='filters.eda.nokia.com',
                                    version='v1',
                                    kind='FilterDeployment')
FILTER_SCHEMA = p.Schema(group='filters.eda.nokia.com',
                         version='v1',
                         kind='Filter')
CONTROL_PLANE_FILTER_SCHEMA = p.Schema(group='filters.eda.nokia.com',
                                       version='v1',
                                       kind='ControlPlaneFilter')
MIRROR_FILTER_SCHEMA = p.Schema(group='filters.eda.nokia.com',
                                version='v1',
                                kind='MirrorFilter')
MIRROR_FILTER_DEPLOYMENT_SCHEMA = p.Schema(group='filters.eda.nokia.com',
                                           version='v1',
                                           kind='MirrorFilterDeployment')
QOS_INGRESS_POLICY_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                                     version='v2',
                                     kind='IngressPolicy')
QOS_INGRESS_POLICY_DEPLOYER_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                                              version='v2',
                                              kind='IngressPolicyDeployment')
QOS_EGRESS_POLICY_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                                    version='v2',
                                    kind='EgressPolicy')
QOS_EGRESS_POLICY_DEPLOYER_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                                             version='v2',
                                             kind='EgressPolicyDeployment')
QOS_FORWARDING_CLASS_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                                             version='v2',
                                             kind='ForwardingClass')
QOS_QUEUE_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                            version='v2',
                            kind='Queue')
QOS_POLICY_DEPLOYMENT_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                                        version='v2',
                                        kind='PolicyDeployment')
QOS_POLICY_ATTACHMENT_SCHEMA = p.Schema(group='qos.eda.nokia.com',
                                        version='v2',
                                        kind='PolicyAttachment')
PACKAGE_SCHEMA = p.Schema(group='packages.eda.nokia.com',
                          version='v1alpha1',
                          kind='Package')
VNET_SCHEMA = p.Schema(group='services.eda.nokia.com',
                       version='v2',
                       kind='VirtualNetwork')
VNET_STATE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                             version='v2',
                             kind='VirtualNetworkState')
BRIDGE_DOMAIN_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                version='v2',
                                kind='BridgeDomain')
BRIDGE_DOMAIN_STATE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                      version='v2',
                                      kind='BridgeDomainState')
BRIDGE_DOMAIN_DEPLOYMENT_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                           version='v2',
                                           kind='BridgeDomainDeployment')
ROUTER_DEPLOYMENT_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                    version='v2',
                                    kind='RouterDeployment')
ROUTED_INTERFACE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                   version='v2',
                                   kind='RoutedInterface')
ROUTED_INTERFACE_STATE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                         version='v2',
                                         kind='RoutedInterfaceState')
IRB_INTERFACE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                version='v1',
                                kind='IRBInterface')
IRB_INTERFACE_STATE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                      version='v2',
                                      kind='IRBInterfaceState')
VLAN_SCHEMA = p.Schema(group='services.eda.nokia.com',
                       version='v2',
                       kind='VLAN')
VLAN_STATE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                             version='v2',
                             kind='VLANState')
ROUTER_SCHEMA = p.Schema(group='services.eda.nokia.com',
                         version='v2',
                         kind='Router')
ROUTER_STATE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                               version='v2',
                               kind='RouterState')
STATE_CONFIG_SCHEMA = p.Schema(group='services.eda.nokia.com',
                               version='v2',
                               kind='StateConfig')
BRIDGE_INTERFACE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                   version='v2',
                                   kind='BridgeInterface')
BRIDGE_INTERFACE_STATE_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                         version='v2',
                                         kind='BridgeInterfaceState')
ROUTER_ATTACHMENT_SCHEMA = p.Schema(group='services.eda.nokia.com',
                                    version='v2',
                                    kind='RouterAttachment')
ANOMALY_MTU_SCHEMA = p.Schema(group='anomalies.eda.nokia.com',
                              version='v1alpha1',
                              kind='MTU')
ANOMALY_MTU_STATE_SCHEMA = p.Schema(group='anomalies.eda.nokia.com',
                                    version='v1alpha1',
                                    kind='MTUState')
LOG_DEPLOYMENT_SCHEMA = p.Schema(group='logs.eda.nokia.com',
                                 version='v1alpha1',
                                 kind='LogDeployment')
LOG_SCHEMA = p.Schema(group='logs.eda.nokia.com',
                      version='v1alpha1',
                      kind='Log')
LOG_FILTER_DEPLOYMENT_SCHEMA = p.Schema(group='logs.eda.nokia.com',
                                        version='v1alpha1',
                                        kind='FilterDeployment')
LOG_FILTER_SCHEMA = p.Schema(group='logs.eda.nokia.com',
                             version='v1alpha1',
                             kind='Filter')
TOPOLOGY_LINK_STATE_SCHEMA = p.Schema(group='topologies.eda.nokia.com',
                                      version='v1',
                                      kind='TopoLinkState')
# Engine objects
CONFIG_SCHEMA = p.Schema(group='core.eda.nokia.com',
                         version='v1',
                         kind='NodeConfig')
TOPOLOGY_NODE_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                version='v1',
                                kind='TopoNode')
TOPOLOGY_LINK_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                version='v1',
                                kind='TopoLink')
TARGET_NODE_SCHEMA = p.Schema(group='core.eda.nokia.com',
                              version='v1',
                              kind='TargetNode')
NODE_PROFILE_SCHEMA = p.Schema(group='core.eda.nokia.com',
                               version='v1',
                               kind='NodeProfile')
SATELLITE_PROFILE_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                    version='v1',
                                    kind='SatelliteProfile')
ARTIFACT_SCHEMA = p.Schema(group='artifacts.eda.nokia.com',
                           version='v1',
                           kind='Artifact')
GLOBAL_CONFIG_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                version='v1',
                                kind='GlobalConfig')
EDGE_INTERFACE_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                 version='v1',
                                 kind='EdgeInterface')
IP_ALLOCATION_POOL_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                     version='v1',
                                     kind='IPAllocationPool')
SUBNET_ALLOCATION_POOL_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                         version='v1',
                                         kind='SubnetAllocationPool')
NODE_SECURITY_PROFILE_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                        version='v1',
                                        kind='NodeSecurityProfile')

ALARM_DEFINITION_SCHEMA = p.Schema(group='core.eda.nokia.com',
                                   version='v1',
                                   kind='AlarmDefinition')

# Kubernetes core objects
POD_SCHEMA = p.Schema(group='',
                            version='v1',
                            kind='Pod')
DEPLOYMENT_SCHEMA = p.Schema(group='apps',
                             version='v1',
                             kind='Deployment')
DEPLOYMENT_SCHEMA = p.Schema(group='apps',
                             version='v1',
                             kind='Deployment')
CONFIG_MAP_SCHEMA = p.Schema(group='',
                             version='v1',
                             kind='ConfigMap')
SECRET_SCHEMA = p.Schema(group='',
                         version='v1',
                         kind='Secret')
