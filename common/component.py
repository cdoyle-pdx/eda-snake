import utils.paths as path_utils
import utils.paths2 as path_utils2
import eda_state as estate
import common.constants as constants
import utils.timestamp as timestamp
from utils.log import log_msg

SCHEMA_VERSION = "v2"
SCHEMA_GROUP = "components_eda_nokia_com"
SCHEMA_KIND = "component"
COMPONENTS = {
    constants.PLATFORM_SRL: {
        'fields': [
            'admin-state',  # enabled
            'oper-state',  # up
            'part-number',
            'serial-number',
            'manufactured-date',  # 09/19/2002 00:00:00
            'last-change',  # 02/06/2023 00:00:00
            'type'  # 7220 IXR-D3L
        ],
        'paths': {
            'fanTray': '.platform.fan-tray',
            'powerSupply': '.platform.power-supply',
            'lineCard': '.platform.linecard',
            'control': '.platform.control',
            'fabric': '.platform.fabric',
            'chassis': '.platform.chassis'
        }
    },
    constants.PLATFORM_SROS: {
        'fields': [
            'oper-state',  # in-service
            'state',  # ok
            'part-number',
            'serial-number',
            'manufacturing-date',  # 01012003
            'software-last-boot-time',  # 2023-03-09T20:51:38.0+00:00
            'equipped-platform-type',  # 7750 SR-12
            'failure-reason'  # 'none'
        ],
        'paths': {
            'fanTray': '.state.chassis.fan.hardware-data',  # fan-slot
            'powerModule': '.state.chassis.power-shelf.power-module.hardware-data',  # power-shelf-id, power-module-id
            'powerSupply': '.state.chassis.power-supply.hardware-data',  # power-supply-id
            'powerShelf': '.state.chassis.power-shelf.hardware-data',  # power-shelf-id
            'lineCard': '.state.card.hardware-data',  # slot-number
            'control': '.state.cpm.hardware-data',  # cpm-slot
            'fabric': '.state.sfm.hardware-data',  # sfm-slot ?
            'chassis': '.state.chassis.hardware-data'
        }
    }
}

COMPONENT_FAN = 'Fan'
COMPONENT_POWER_SUPPLY = 'PowerSupply'
COMPONENT_POWER_SHELF = 'PowerShelf'
COMPONENT_POWER_MODULE = 'PowerModule'
COMPONENT_LINECARD = 'InterfaceModule'
COMPONENT_CONTROL = 'ControlModule'
COMPONENT_FABRIC = 'FabricModule'
COMPONENT_CHASSIS = 'Chassis'


def get_list_request(platform):
    requests = []
    for _, path in COMPONENTS[platform]['paths'].items():
        requests.append({
            'path': f'.node.{platform}.{path}',
            'fields': COMPONENTS[platform]['fields'],
            'coalesce': False
        })
    return requests

# '^Chassis'
# '^Fabric[0-9]'
# '^FabricChip'
# '^Fan[0-9]'
# '^Linecard[0-9]'
# '^SwitchChip'
# '^PowerSupply[0-9]'
# '^Control[A-B]'
# '^TempSensor[*]'
# 'transceiver$'


class Component:
    def get_path(self):
        return self.path

    def get_node(self):
        return self.node

    def get_normalized_value(self):
        return {
            'enabled': self.enabled,
            'operationalState': self.oper_state,
            'partNumber': self.part_number,
            'serialNumber': self.serial_number,
            'manufacturedDate': self.manufactured_date,
            'lastChangeTime': self.last_change,
            'type': self.cr_type,
            'slot': self.slot
        }

    def get_normalized_path(self):
        return self.normalized_path

    def get_normalized_name(self):
        return self.normalized_name

    def get_cr_name(self):
        return f'{self.node}-{self.normalized_name}'

    def get_cr_type(self):
        if 'fan' in self.path:
            return 'FanTray'
        elif 'power-module' in self.path:
            return 'PowerModule'
        elif 'power-shelf' in self.path:
            return 'PowerShelf'
        elif 'power-supply' in self.path:
            return 'PowerSupply'
        elif 'linecard' in self.path or 'card' in self.path:
            return 'InterfaceModule'
        elif 'control' in self.path or 'cpm' in self.path:
            return 'ControlModule'
        elif 'fabric' in self.path or 'sfm' in self.path:
            return 'FabricModule'
        elif 'chassis' in self.path:
            return 'Chassis'

    def get_cr_spec(self):
        return {
            'type': self.cr_type,
            'node': self.node,
            'slot': self.slot,
        }

    def get_cr_status(self):
        return {
            'enabled': self.enabled,
            'operationalState': self.oper_state,
            'type': self.type,
            'partNumber': self.part_number,
            'serialNumber': self.serial_number,
            'manufacturedDate': self.manufactured_date,
            'lastChangeTime': self.last_change
        }

    def normalize_name(self, path):
        if 'fan' in path:
            return f'{COMPONENT_FAN}{self.slot}'
        if 'power-module' in path:
            return f'{COMPONENT_POWER_MODULE}{self.slot}'
        if 'power-shelf' in path:
            return f'{COMPONENT_POWER_SHELF}{self.slot}'
        if 'power-supply' in path:
            return f'{COMPONENT_POWER_SUPPLY}{self.slot}'
        if 'linecard' in path or 'card' in path:
            return f'{COMPONENT_LINECARD}{self.slot}'
        if 'control' in path or 'cpm' in path:
            return f'{COMPONENT_CONTROL}{self.slot}'
        if 'fabric' in path or 'sfm' in path:
            return f'{COMPONENT_FABRIC}{self.slot}'
        if 'chassis' in path:
            return f'{COMPONENT_CHASSIS}'

    def normalize_path(self, path):
        return f'.node{{.name=="{self.node}"}}.apps.{SCHEMA_GROUP}.{SCHEMA_VERSION}.{SCHEMA_KIND}{{.name=="{self.normalize_name(path)}"}}'

    def normalize_oper_state(self, oper_state):
        if oper_state == 'up' or oper_state == 'synchronizing' or oper_state == 'in-service':
            return 'Up'
        if oper_state == 'failed' or oper_state == 'down' or oper_state == 'out-of-service' or oper_state == 'waiting' or oper_state == 'low-power':
            return 'Down'
        if oper_state == 'empty':
            return 'Empty'
        if oper_state == 'warm-reboot' or oper_state == 'upgrading':
            return 'Rebooting'
        if oper_state == 'downloading' or oper_state == 'starting':
            return 'Starting'
        else:
            return 'Unknown'

    def normalize_admin_state(self, admin_state):
        if admin_state == 'enable' or admin_state == 'up':
            return True
        if admin_state == 'disable' or admin_state == 'down':
            return False
        else:
            return True

    def __init__(
            self,
            path,
            value):
        self.path = path
        self.value = value
        self.slot = None
        parser = path_utils2.JPathParser(path)
        self.path_node_values = parser.get_nodes_with_values()
        self.node = self.path_node_values.get('node', None)
        self.type = None
        self.manufactured_date = None
        self.enabled = None

        oper_state_raw = self.value.get('oper-state', "")
        self.oper_state = self.normalize_oper_state(oper_state_raw)
        if constants.PLATFORM_SRL in self.path:
            self.platform = constants.PLATFORM_SRL
            self.slot = self.path_node_values.get(parser.get_last_node(), None)
            self.manufactured_date = self.value.get('manufactured-date', "")
            self.last_change = self.value.get('last-change', "")
            self.type = self.value.get('type', "")
            self.enabled = self.normalize_admin_state(self.value.get('admin-state', "enable"))
            if self.last_change == '':
                try:
                    chassis = next(estate.list_db(path=f'.node{{.name=="{self.node}"}}.{constants.PLATFORM_SRL}.platform.chassis', fields=['last-booted']))
                    chassis_last_booted = chassis.get('value', {}).get('last-booted', "")
                except Exception:
                    chassis_last_booted = ''
                if chassis_last_booted:
                    self.last_change = timestamp.get_normalized_timestamp(chassis_last_booted)
        elif constants.PLATFORM_SROS in self.path:
            self.platform = constants.PLATFORM_SROS
            self.slot_keyname, self.slot = path_utils.nearest_ancestor_key_value(self.path)
            if 'Control' in self.get_cr_type():
                suffix = '.hardware-data'
                if self.path.endswith(suffix):
                    control_path = self.path[:-len(suffix)]
                    control_type = None
                    try:
                        control_data_raw = next(estate.list_db(path=control_path, fields=['equipped-type']))
                        control_type = control_data_raw.get('value', {}).get('equipped-type', "")
                    except Exception:
                        self.type = ''
                    if control_type:
                        # print(f"control_type: {control_type}")
                        self.type = control_type
                    self.enabled = True  # control components are always enabled
            elif 'PowerSupply' in self.get_cr_type():
                suffix = '.hardware-data'
                if self.path.endswith(suffix):
                    psu_path = self.path[:-len(suffix)]
                    psu_type = None
                    try:
                        psu_data_raw = next(estate.list_db(path=psu_path, fields=['equipped-type']))
                        psu_type = psu_data_raw.get('value', {}).get('equipped-type', "")
                    except Exception:
                        self.type = ''
                    if psu_type:
                        self.type = psu_type
                    self.enabled = True  # psu components are always enabled
            elif 'InterfaceModule' in self.get_cr_type():
                suffix = '.hardware-data'
                if self.path.endswith(suffix):
                    card_path = self.path[:-len(suffix)]
                    card_type = None
                    try:
                        card_data_raw = next(estate.list_db(path=card_path, fields=['equipped-type']))
                        card_type = card_data_raw.get('value', {}).get('equipped-type', "")
                    except Exception:
                        self.type = ''
                    if card_type:
                        self.type = card_type
                    configure_path = card_path.replace('state.card', 'configure.card', 1)
                    log_msg(f"configure_path: {configure_path}")
                    try:
                        linecard_config_data_raw = next(estate.list_db(path=configure_path, fields=['admin-state']))
                        self.enabled = self.normalize_admin_state(linecard_config_data_raw.get('value', {}).get('admin-state', "enable"))
                        # print(f"admin_state: {self.enabled}")
                    except Exception:
                        self.enabled = True
            elif 'Chassis' in self.get_cr_type():
                self.enabled = True
                try:
                    chassis_data_raw = next(estate.list_db(path=f'.node{{.name=="{self.node}"}}.{constants.PLATFORM_SROS}.state.system', fields=['platform']))
                    chassis_type = chassis_data_raw.get('value', {}).get('platform', "")
                except Exception:
                    chassis_type = ''
                if chassis_type:
                    self.type = chassis_type
            else:
                self.type = ""
                self.enabled = True
            manufactured_date_raw = self.value.get('manufacturing-date', "")
            if manufactured_date_raw == '        ':
                # SR OS returns an 8 character string of spaces for manufactured-date when the value is not available
                self.manufactured_date = ''
            elif manufactured_date_raw:
                self.manufactured_date = timestamp.get_timestamp_from_mmddyyyy(manufactured_date_raw)
            else:
                self.manufactured_date = ''
                # print(f"manufactured-date is empty for path: {path}")
            log_msg(f'Attempting to process ancestor keys for path: {path}')
            software_last_boot_time_raw = self.value.get('software-last-boot-time', "")
            if software_last_boot_time_raw:
                self.last_change = timestamp.get_normalized_timestamp(self.value.get('software-last-boot-time', ""))
            else:
                self.last_change = ''
            if self.last_change == '':
                # print(f"last-change is empty for path: {path}")
                chassis = next(estate.list_db(path=f'.node{{.name=="{self.node}"}}.{constants.PLATFORM_SROS}.state.chassis.hardware-data', fields=['software-last-boot-time']))
                # print(f"chassis: {chassis}")
                chassis_last_booted = chassis.get('value', {}).get('software-last-boot-time', "")
                # print(f"chassis_last_booted: {chassis_last_booted}")
                if chassis_last_booted:
                    self.last_change = timestamp.get_normalized_timestamp(chassis_last_booted)
        # if self.slot is None:
        #     raise e.InvalidTelemetry(path=self.path, message='unable to infer slot id - no "slot" or "id" present')

        self.part_number = self.value.get('part-number', "")
        self.serial_number = self.value.get('serial-number', "")
        self.normalized_path = self.normalize_path(self.path)
        self.normalized_name = self.normalize_name(self.path)
        self.cr_type = self.get_cr_type()
