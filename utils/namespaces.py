#!/usr/bin/env python3

import eda_config as ecfg
from utils.schema import NAMESPACE_SCHEMA

INCLUDE_BASE_NAMESPACE = True


def list_crs_all_namespaces(schema, filter=[], label_filter=[]):
    resources = []
    namespaces = []
    if INCLUDE_BASE_NAMESPACE:
        namespaces.append('_base_')
    for namespace in ecfg.list_crs(schema=NAMESPACE_SCHEMA, filter=[]):
        namespaces.append(namespace['metadata']['name'])
    for namespace in namespaces:
        for resource in ecfg.list_crs(ns=namespace,
                                      schema=schema,
                                      filter=filter,
                                      label_filter=label_filter):
            resources.append(resource)
    return resources
