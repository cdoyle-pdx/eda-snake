#!/usr/bin/env python3
from .constants import *

COLOR_WEIGHT = {
    DB_TOPO_COLOR_KPI_CRITICAL: 22,
    DB_TOPO_COLOR_KPI_MAJOR: 21,
    DB_TOPO_COLOR_KPI_MINOR: 20,
    DB_TOPO_COLOR_KPI_WARNING: 19,
    DB_TOPO_COLOR_KPI_INFO: 18,
    DB_TOPO_COLOR_KPI_MAINTENANCE: 17,
    DB_TOPO_COLOR_KPI_DISABLED: 16,
    DB_TOPO_COLOR_KPI_INDETERMINATE: 15,
    DB_TOPO_COLOR_KPI_INSTALLED: 14,
    DB_TOPO_COLOR_KPI_CLEARED: 13,
    DB_TOPO_COLOR_KPI_SUCCESS: 12,
    DB_TOPO_COLOR_KPI_NEUTRAL: 11,
    DB_TOPO_COLOR_SEQUENTIAL_90: 10,
    DB_TOPO_COLOR_SEQUENTIAL_80: 9,
    DB_TOPO_COLOR_SEQUENTIAL_70: 8,
    DB_TOPO_COLOR_SEQUENTIAL_60: 7,
    DB_TOPO_COLOR_SEQUENTIAL_50: 6,
    DB_TOPO_COLOR_SEQUENTIAL_40: 5,
    DB_TOPO_COLOR_SEQUENTIAL_30: 4,
    DB_TOPO_COLOR_SEQUENTIAL_20: 3,
    DB_TOPO_COLOR_SEQUENTIAL_10: 2,
    DB_TOPO_COLOR_SEQUENTIAL_00: 1,
}


class DbTopoOverlayState:
    def __init__(self,
                 db_value,):
        color = db_value['color']
        if color in COLOR_WEIGHT:
            db_value['weight'] = COLOR_WEIGHT[color]
        else:
            raise ValueError('Invalid color specified for overlay state')
        self.db_value = db_value

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

    def set_weight(self,
                   weight: int,):
        self.db_value['weight'] = weight
        return self


class DbTopoOverlayBadge(DbTopoOverlayState):
    def __init__(self,
                 db_value,):
        DbTopoOverlayState.__init__(self, db_value)

    def set_nav_target(self,
                       nav_target,):
        self.db_value['nav_target'] = nav_target
        return self


class DbTopoOverlayAttrMetadata:
    def __init__(self,
                 db_value,):
        self.db_value = db_value

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


class DbTopoOverlayAttrsQuery:
    def __init__(self,
                 db_value,):
        self.db_value = db_value

    def add_attribute(self,
                      attr: str,):
        if DB_TOPO_ATTRIBUTES not in self.db_value:
            self.db_value[DB_TOPO_ATTRIBUTES] = {}
        self.db_value[DB_TOPO_ATTRIBUTES][attr] = {}
        return DbTopoOverlayAttrMetadata(self.db_value[DB_TOPO_ATTRIBUTES][attr])
