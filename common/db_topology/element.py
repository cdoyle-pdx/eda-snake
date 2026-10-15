#!/usr/bin/env python3
import eda_state as estate
import eda_common as eda
from .constants import DB_TOPO_ATTRIBUTES


class DbTopoElemBase:
    def __init__(self,
                 type: str,
                 name: str,
                 namespace: str,
                 topo_path: str,):
        self.db_path = f'{topo_path}.{type}{{.name=="{name}"}}'
        self.db_value = {
            'namespace': namespace,
            'cr_name': name,
            'ui_name': name
        }

    def override_cr_name(self,
                         name: str,):
        self.db_value['cr_name'] = name
        return self

    def override_ui_name(self,
                         name: str,):
        self.db_value['ui_name'] = name
        return self

    def override_schema(self,
                        schema: eda.Schema,):
        self.db_value['schema'] = {
            'group': schema.group,
            'version': schema.version,
            'kind': schema.kind,
        }
        return self

    def set_labels(self,
                   labels: dict,):
        self.db_value['labels'] = labels
        return self

    def set_attribute(self,
                      attr: str,
                      value: any,):
        if DB_TOPO_ATTRIBUTES not in self.db_value:
            self.db_value[DB_TOPO_ATTRIBUTES] = {}
        self.db_value[DB_TOPO_ATTRIBUTES][attr] = value
        return self

    def write_to_db(self):
        estate.update_db(path=self.db_path, value=self.db_value,
                         ns=self.db_value['namespace'])


class DbTopoNode(DbTopoElemBase):
    def __init__(self,
                 name: str,
                 namespace: str,
                 topo_path: str,):
        DbTopoElemBase.__init__(self, 'node', name, namespace, topo_path)


class DbTopoLink(DbTopoElemBase):
    def __init__(self,
                 name: str,
                 namespace: str,
                 topo_path: str,):
        DbTopoElemBase.__init__(self, 'link', name, namespace, topo_path)

    def set_endpoint_a(self,
                       endpoint_name: str,
                       endpoint_namespace: str = None):
        self.db_value['endpoint_a_name'] = endpoint_name
        if endpoint_namespace is not None:
            self.db_value['endpoint_a_namespace'] = endpoint_namespace
        else:
            self.db_value['endpoint_a_namespace'] = self.db_value['namespace']
        return self

    def set_endpoint_b(self,
                       endpoint_name: str,
                       endpoint_namespace: str = None):
        self.db_value['endpoint_b_name'] = endpoint_name
        if endpoint_namespace is not None:
            self.db_value['endpoint_b_namespace'] = endpoint_namespace
        else:
            self.db_value['endpoint_b_namespace'] = self.db_value['namespace']
        return self


class DbTopoEndpoint(DbTopoElemBase):
    def __init__(self,
                 name: str,
                 namespace: str,
                 topo_path: str,):
        DbTopoElemBase.__init__(self, 'endpoint', name, namespace, topo_path)

    def set_node(self,
                 node_name: str,):
        self.db_value['node'] = node_name
