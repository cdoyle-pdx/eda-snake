#!/usr/bin/env python3
import eda_common as eda
from .constants import DB_TOPO_ATTRIBUTES


class DbTopoAttrMetadata:
    def __init__(self,
                 db_value,
                 type: str,):
        self.db_value = db_value
        self.db_value['type'] = type

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


class DbTopoElemMetadata:
    def __init__(self,
                 db_value,):
        self.db_value = db_value

    def set_schema(self,
                   schema: eda.Schema,):
        self.db_value['schema'] = {
            'group': schema.group,
            'version': schema.version,
            'kind': schema.kind,
        }
        return self

    def set_subtitle(self,
                     subtitle: str,):
        self.db_value['subtitle'] = subtitle
        return self

    def set_subtitle_i18n(self,
                          subtitle_key: str,):
        self.db_value['subtitle_key'] = subtitle_key
        return self

    def add_attribute(self,
                      attr: str,
                      type: str,):
        if DB_TOPO_ATTRIBUTES not in self.db_value:
            self.db_value[DB_TOPO_ATTRIBUTES] = {}
        self.db_value[DB_TOPO_ATTRIBUTES][attr] = {}
        return DbTopoAttrMetadata(self.db_value[DB_TOPO_ATTRIBUTES][attr], type)
