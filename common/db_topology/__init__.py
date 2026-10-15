#!/usr/bin/env python3
import eda_state as estate
import eda_common as eda
from common.metadata import Metadata, Y_METADATA
from .element import DbTopoNode, DbTopoLink, DbTopoEndpoint
from .overlay_state import DbTopoOverlayState, DbTopoOverlayBadge, DbTopoOverlayAttrsQuery
from .element_metadata import DbTopoElemMetadata

Y_SPEC = 'spec'
Y_ENABLED = 'enabled'
Y_UI_NAME = 'uiName'
Y_UI_DESCRIPTION = 'uiDescription'
Y_UI_NAME_KEY = 'uiNameKey'
Y_UI_DESCRIPTION_KEY = 'uiDescriptionKey'
Y_OVERLAYS = 'overlays'
Y_KEY = 'key'
Y_TOPOLOGY = 'topology'
Y_GROUP = 'group'
Y_VERSION = 'version'
Y_NAME = 'name'


class DbTopoOverlay:
    def __init__(self,
                 name: str,
                 group: str,
                 version: str,
                 topo_path: str,
                 enabled: bool,
                 serialized: any = None):
        if serialized is not None:
            self.db_path = serialized['db_path']
            self.db_topo_path = serialized['db_topo_path']
            self.db_value = serialized['db_value']
            self.enabled = serialized['enabled']
            return

        self.name = DbTopoOverlay.db_name(group, version, name)
        self.db_path = f'{topo_path}.overlay{{.name=="{self.name}"}}'
        self.db_topo_path = topo_path
        self.db_value = {
            'group': group,
            'version': version,
            'node_state': [],
            'endpoint_state': [],
            'link_state': [],
            'node_badge': [],
            'node_attr_queries': [],
            'endpoint_attr_queries': [],
            'link_attr_queries': []
        }
        self.enabled = enabled

    @classmethod
    def from_cr(cls,
                schema: any,
                cr_obj,):
        metadata = Metadata.from_input(cr_obj.get(Y_METADATA))
        spec = cr_obj[Y_SPEC]
        topology = spec[Y_TOPOLOGY]
        topology_name = DbTopology.db_name(topology[Y_GROUP], topology[Y_VERSION], topology[Y_NAME])
        db_path = DbTopology.db_path(topology_name)
        enabled = spec.get(Y_ENABLED, False)
        result = cls(metadata.name, schema.group, schema.version, db_path, enabled)

        if Y_UI_NAME in spec:
            result.set_metadata(spec.get(Y_UI_NAME, metadata.name), spec.get(Y_UI_DESCRIPTION, ""))
        if Y_UI_NAME_KEY in spec:
            result.set_metadata_i18n(spec.get(Y_UI_NAME_KEY, ""), spec.get(Y_UI_DESCRIPTION_KEY, ""))
        elif Y_UI_NAME not in spec:
            result.set_metadata(metadata.name, "")

        return result

    @classmethod
    def db_name(cls,
                group: str,
                version: str,
                name: str):
        return f'{group}_{version}_{name}'

    @classmethod
    def deserialize(cls,
                    data,):
        result = cls(data['name'], data['db_value']['group'], data['db_value']['version'], data['db_topo_path'], data['enabled'], data)
        return result

    def serialize(self,):
        return {
            'name': self.name,
            'db_path': self.db_path,
            'db_topo_path': self.db_topo_path,
            'db_value': self.db_value,
            'enabled': self.enabled,
        }

    def is_enabled(self,):
        return self.enabled

    def has_subscribers(self,):
        for row in estate.list_db(path=f'.cluster{self.db_path}.subscriber', fields=[]):
            return True
        return False

    def topo_node_path(self,):
        return f'.namespace{self.db_topo_path}.node'

    def topo_link_path(self,):
        return f'.namespace{self.db_topo_path}.link'

    def topo_endpoint_path(self,):
        return f'.namespace{self.db_topo_path}.endpoint'

    def set_metadata(self,
                     ui_name: str,
                     ui_description: str,):
        self.db_value['ui_name'] = ui_name
        self.db_value['ui_description'] = ui_description
        return self

    def set_metadata_i18n(self,
                          ui_name_key: str,
                          ui_description_key: str,):
        self.db_value['ui_name_key'] = ui_name_key
        self.db_value['ui_description_key'] = ui_description_key
        return self

    def set_node_state_heading(self,
                               heading: str,):
        self.db_value['node_state_heading'] = heading
        return self

    def set_node_state_heading_i18n(self,
                                    heading_key: str,):
        self.db_value['node_state_heading_key'] = heading_key
        return self

    def set_link_state_heading(self,
                               heading: str,):
        self.db_value['link_state_heading'] = heading
        return self

    def set_link_state_heading_i18n(self,
                                    heading_key: str,):
        self.db_value['link_state_heading_key'] = heading_key
        return self

    def set_endpoint_state_heading(self,
                                   heading: str,):
        self.db_value['endpoint_state_heading'] = heading
        return self

    def set_endpoint_state_heading_i18n(self,
                                        heading_key: str,):
        self.db_value['endpoint_state_heading_key'] = heading_key
        return self

    def _add_state(self,
                   value: int,
                   color: str,
                   state_type: str,):
        state = {
            'value': value,
            'color': color,
        }
        self.db_value[state_type].append(state)
        return DbTopoOverlayState(state)

    def add_node_state(self,
                       value: int,
                       color: str,):
        return self._add_state(value, color, 'node_state')

    def add_link_state(self,
                       value: int,
                       color: str,):
        return self._add_state(value, color, 'link_state')

    def add_endpoint_state(self,
                           value: int,
                           color: str,):
        return self._add_state(value, color, 'endpoint_state')

    def add_node_badge(self,
                       value: int,
                       color: str,
                       badge_name: str = None,
                       badge_path: str = None,):
        badge = {
            'value': value,
            'color': color
        }

        if badge_name is None:
            if badge_path is None:
                raise ValueError('Must provide one of badge_name or badge_path')
            else:
                badge['badge_path'] = badge_path
        elif badge_path is None:
            badge['badge_name'] = badge_name
        else:
            raise ValueError('Must only provide one of badge_name or badge_path')
        self.db_value['node_badge'].append(badge)
        return DbTopoOverlayBadge(badge)

    def _add_attributes_query(self,
                              query: str,
                              attr_type,):
        attributes_query = {
            'query': query,
        }
        self.db_value[attr_type].append(attributes_query)
        return DbTopoOverlayAttrsQuery(attributes_query)

    def add_node_attributes_query(self,
                                  query: str,):
        return self._add_attributes_query(query, 'node_attr_queries')

    def add_link_attributes_query(self,
                                  query: str,):
        return self._add_attributes_query(query, 'link_attr_queries')

    def add_endpoint_attributes_query(self,
                                      query: str,):
        return self._add_attributes_query(query, 'endpoint_attr_queries')

    def write_to_db(self):
        estate.update_db(path='.cluster' + self.db_path, value=self.db_value)

    def write_node_state(self,
                         node_name: str,
                         namespace: str,
                         state_value: int,
                         badge_values=[],):
        estate.update_db(f'{self.db_path}.node{{.name=="{node_name}"}}', {
            'namespace': namespace,
            'state': state_value,
            'badges': badge_values,
        }, ns=namespace)

    def write_link_state(self,
                         link_name: str,
                         namespace: str,
                         state_value: int,):
        estate.update_db(f'{self.db_path}.link{{.name=="{link_name}"}}', {
            'namespace': namespace,
            'state': state_value
        }, ns=namespace)

    def write_endpoint_state(self,
                             endpoint_name: str,
                             namespace: str,
                             state_value: int,):
        estate.update_db(f'{self.db_path}.endpoint{{.name=="{endpoint_name}"}}', {
            'namespace': namespace,
            'state': state_value
        }, ns=namespace)

    def _get_db(self,
                path: str,
                namespace: str,):
        result = estate.get_db(path, ns=namespace, fields=['**'])
        if result is None:
            return None
        return result.get('value', None)

    def get_node(self,
                 node_name: str,
                 namespace: str,):
        return self._get_db(f'{self.db_topo_path}.node{{.name=="{node_name}"}}', namespace)

    def get_link(self,
                 link_name: str,
                 namespace: str,):
        return self._get_db(f'{self.db_topo_path}.link{{.name=="{link_name}"}}', namespace)

    def get_endpoint(self,
                     endpoint_name: str,
                     namespace: str,):
        return self._get_db(f'{self.db_topo_path}.endpoint{{.name=="{endpoint_name}"}}', namespace)


class DbTopology:
    def __init__(self,
                 schema: eda.Schema,
                 cr_obj: str,
                 serialized: any = None):
        if serialized is not None:
            self.db_path = serialized['db_path']
            self.db_value = serialized['db_value']
            self.enabled = serialized['enabled']
            self.overlays_enabled = serialized['overlays_enabled']
            return

        group = schema.group
        version = schema.version
        metadata = Metadata.from_input(cr_obj.get(Y_METADATA))
        name = DbTopology.db_name(group, version, metadata.name)
        self.db_path = DbTopology.db_path(name)
        self.db_value = {
            'group': group,
            'version': version,
        }

        spec = cr_obj[Y_SPEC]
        self.enabled = spec.get(Y_ENABLED, False)

        if Y_UI_NAME in spec:
            self.set_metadata(spec.get(Y_UI_NAME, metadata.name), spec.get(Y_UI_DESCRIPTION, ""))
        if Y_UI_NAME_KEY in spec:
            self.set_metadata_i18n(spec.get(Y_UI_NAME_KEY, ""), spec.get(Y_UI_DESCRIPTION_KEY, ""))
        elif Y_UI_NAME not in spec:
            self.set_metadata(metadata.name, "")

        self.overlays_enabled = {}
        for overlay in spec.get(Y_OVERLAYS, []):
            self.overlays_enabled[overlay[Y_KEY]] = overlay.get(Y_ENABLED, False)

    @classmethod
    def db_name(cls,
                group: str,
                version: str,
                name: str):
        return f'{group}_{version}_{name}'

    @classmethod
    def db_path(cls,
                db_name: str,):
        return f'.topologies.v1.topology{{.name=="{db_name}"}}'

    @classmethod
    def deserialize(cls,
                    data,):
        result = cls(None, "", data)
        return result

    def serialize(self,):
        return {
            'db_path': self.db_path,
            'db_value': self.db_value,
            'enabled': self.enabled,
            'overlays_enabled': self.overlays_enabled,
        }

    def is_enabled(self,):
        return self.enabled

    def set_metadata(self,
                     ui_name: str,
                     ui_description: str,):
        self.db_value['ui_name'] = ui_name
        self.db_value['ui_description'] = ui_description
        return self

    def set_metadata_i18n(self,
                          ui_name_key: str,
                          ui_description_key: str,):
        self.db_value['ui_name_key'] = ui_name_key
        self.db_value['ui_description_key'] = ui_description_key
        return self

    def set_grouping_schema(self,
                            schema: eda.Schema,):
        self.db_value['grouping'] = {
            'group': schema.group,
            'version': schema.version,
            'kind': schema.kind,
        }
        return self

    def _elem_metadata(self,
                       type: str,):
        self.db_value[type] = {}
        return DbTopoElemMetadata(self.db_value[type])

    def node_metadata(self,):
        return self._elem_metadata('nodes')

    def link_metadata(self,):
        return self._elem_metadata('links')

    def endpoint_metadata(self,):
        return self._elem_metadata('endpoints')

    def node(self,
             node_name: str,
             namespace: str,):
        return DbTopoNode(node_name, namespace, self.db_path)

    def link(self,
             link_name: str,
             namespace: str,):
        return DbTopoLink(link_name, namespace, self.db_path)

    def endpoint(self,
                 endpoint_name: str,
                 namespace: str,):
        return DbTopoEndpoint(endpoint_name, namespace, self.db_path)

    def overlay(self,
                overlay_name: str,):
        return DbTopoOverlay(overlay_name, self.db_value['group'], self.db_value['version'], self.db_path, self.overlays_enabled.get(overlay_name, False))

    def write_to_db(self):
        estate.update_db(path='.cluster' + self.db_path, value=self.db_value)
