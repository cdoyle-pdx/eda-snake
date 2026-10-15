#!/usr/bin/env python3
from common import component
from common import constants

INPUT_PATH_1 = \
    '.node{.name=="dut1"}' \
    '.' + constants.PLATFORM_SRL + '{.version=="24.7.1"}' \
    '.fan-tray{.id==1}'
INPUT_VALUE_1 = {
    "slot": '1',
    "oper-state": "up",
    "part-number": "12345",
    "serial-number": "54321",
    "manufactured-date": "09/19/2002 00:00:00",
    "last-change": "02/06/2023 00:00:00",
    "type": 'fanTray'
}
INPUT_PATH_2 = \
    '.node{.name=="dut1"}' \
    '.' + constants.PLATFORM_SRL + '{.version=="24.7.1"}' \
    '.power-supply{.id==1}'
INPUT_VALUE_2 = {
    "slot": '1',
    "oper-state": "up",
    "part-number": "12345",
    "serial-number": "54321",
    "manufactured-date": "09/19/2002 00:00:00",
    "last-change": "02/06/2023 00:00:00",
    "type": 'powerSupply'
}
INPUT_PATH_3 = \
    '.node{.name=="dut1"}' \
    '.' + constants.PLATFORM_SRL + '{.version=="24.7.1"}' \
    '.linecard{.slot=="1"}'
INPUT_VALUE_3 = {
    "slot": '1',
    "oper-state": "up",
    "part-number": "12345",
    "serial-number": "54321",
    "manufactured-date": "09/19/2002 00:00:00",
    "last-change": "02/06/2023 00:00:00",
    "type": 'lineCard'
}
INPUT_PATH_4 = \
    '.node{.name=="dut1"}' \
    '.' + constants.PLATFORM_SRL + '{.version=="24.7.1"}' \
    '.fabric{.slot==1}'
INPUT_VALUE_4 = {
    "slot": '1',
    "oper-state": "up",
    "part-number": "12345",
    "serial-number": "54321",
    "manufactured-date": "09/19/2002 00:00:00",
    "last-change": "02/06/2023 00:00:00",
    "type": 'fabric'
}
INPUT_PATH_5 = \
    '.node{.name=="dut1"}' \
    '.' + constants.PLATFORM_SRL + '{.version=="24.7.1"}' \
    '.chassis'
INPUT_VALUE_5 = {
    "oper-state": "up",
    "part-number": "12345",
    "serial-number": "54321",
    "manufactured-date": "09/19/2002 00:00:00",
    "last-change": "02/06/2023 00:00:00",
    "type": 'chassis'
}


# def test_get_list_request_sanity():
#     """Sanity test for function get_list_request"""
#     requests_list = component.get_list_request(constants.PLATFORM_SRL)
#     assert isinstance(requests_list, list)


# def test_component_sanity_1():
#     """Sanity test for class Component"""
#     component_component = component.Component(INPUT_PATH_1, INPUT_VALUE_1)
#     assert isinstance(component_component, component.Component)
#     assert component_component.node == "dut1"
#     assert component_component.platform == constants.PLATFORM_SRL
#     assert component_component.slot == INPUT_VALUE_1["slot"]
#     assert component_component.manufactured_date == INPUT_VALUE_1["manufactured-date"]
#     assert component_component.last_change == INPUT_VALUE_1["last-change"]
#     assert component_component.oper_state == "Up"
#     assert component_component.part_number == INPUT_VALUE_1["part-number"]
#     assert component_component.serial_number == INPUT_VALUE_1["serial-number"]
#     assert component_component.normalized_path == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Fan1"}'
#     assert component_component.normalized_name == 'Fan1'
#     assert component_component.cr_type == "FanTray"
#     assert component_component.get_path() == INPUT_PATH_1
#     assert component_component.get_normalized_value() == {
#         "enabled": True,
#         "slot": '1',
#         "operationalState": "Up",
#         "partNumber": "12345",
#         "serialNumber": "54321",
#         "manufacturedDate": "09/19/2002 00:00:00",
#         "lastChange": "02/06/2023 00:00:00",
#         "type": 'FanTray'
#     }
#     assert component_component.get_normalized_path() == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Fan1"}'
#     assert component_component.get_normalized_name() == 'Fan1'
#     assert component_component.get_cr_name() == 'dut1-Fan1'
#     assert component_component.get_cr_type() == 'FanTray'
#     assert component_component.get_cr_spec() == {"type": "FanTray", "node": "dut1", "slot": '1'}
#     assert component_component.get_cr_status() == {'enabled': True, 'operationalState': 'Up', 'type': 'fanTray', 'partNumber': '12345', 'serialNumber': '54321', 'manufacturedDate': '09/19/2002 00:00:00', 'lastChange': '02/06/2023 00:00:00'}
#     assert component_component.normalize_name(INPUT_PATH_1) == "Fan1"
#     assert component_component.normalize_path(INPUT_PATH_1) == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Fan1"}'


# def test_component_sanity_2():
#     """Sanity test for class Component"""
#     component_component = component.Component(INPUT_PATH_2, INPUT_VALUE_2)
#     assert isinstance(component_component, component.Component)
#     assert component_component.node == "dut1"
#     assert component_component.platform == constants.PLATFORM_SRL
#     assert component_component.slot == INPUT_VALUE_2["slot"]
#     assert component_component.manufactured_date == INPUT_VALUE_2["manufactured-date"]
#     assert component_component.last_change == INPUT_VALUE_2["last-change"]
#     assert component_component.oper_state == "Up"
#     assert component_component.part_number == INPUT_VALUE_2["part-number"]
#     assert component_component.serial_number == INPUT_VALUE_2["serial-number"]
#     assert component_component.normalized_path == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="PowerSupply1"}'
#     assert component_component.normalized_name == 'PowerSupply1'
#     assert component_component.cr_type == "PowerSupply"
#     assert component_component.get_path() == INPUT_PATH_2
#     assert component_component.get_normalized_value() == {
#         "enabled": True,
#         "slot": '1',
#         "operationalState": "Up",
#         "partNumber": "12345",
#         "serialNumber": "54321",
#         "manufacturedDate": "09/19/2002 00:00:00",
#         "lastChange": "02/06/2023 00:00:00",
#         "type": 'PowerSupply'
#     }
#     assert component_component.get_normalized_path() == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="PowerSupply1"}'
#     assert component_component.get_normalized_name() == 'PowerSupply1'
#     assert component_component.get_cr_name() == 'dut1-PowerSupply1'
#     assert component_component.get_cr_type() == 'PowerSupply'
#     assert component_component.get_cr_spec() == {"type": "PowerSupply", "node": "dut1", "slot": '1'}
#     assert component_component.get_cr_status() == {'enabled': True, 'operationalState': 'Up', 'type': 'powerSupply', 'partNumber': '12345', 'serialNumber': '54321', 'manufacturedDate': '09/19/2002 00:00:00', 'lastChange': '02/06/2023 00:00:00'}
#     assert component_component.normalize_name(INPUT_PATH_2) == "PowerSupply1"
#     assert component_component.normalize_path(INPUT_PATH_2) == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="PowerSupply1"}'


# def test_component_sanity_3():
#     """Sanity test for class Component"""
#     component_component = component.Component(INPUT_PATH_3, INPUT_VALUE_3)
#     assert isinstance(component_component, component.Component)
#     assert component_component.node == "dut1"
#     assert component_component.platform == constants.PLATFORM_SRL
#     assert component_component.slot == INPUT_VALUE_3["slot"]
#     assert component_component.manufactured_date == INPUT_VALUE_3["manufactured-date"]
#     assert component_component.last_change == INPUT_VALUE_3["last-change"]
#     assert component_component.oper_state == "Up"
#     assert component_component.part_number == INPUT_VALUE_3["part-number"]
#     assert component_component.serial_number == INPUT_VALUE_3["serial-number"]
#     assert component_component.normalized_path == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Linecard1"}'
#     assert component_component.normalized_name == 'Linecard1'
#     assert component_component.cr_type == "LineCard"
#     assert component_component.get_path() == INPUT_PATH_3
#     assert component_component.get_normalized_value() == {
#         "enabled": True,
#         "slot": '1',
#         "operationalState": "Up",
#         "partNumber": "12345",
#         "serialNumber": "54321",
#         "manufacturedDate": "09/19/2002 00:00:00",
#         "lastChange": "02/06/2023 00:00:00",
#         "type": 'LineCard'
#     }
#     assert component_component.get_normalized_path() == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Linecard1"}'
#     assert component_component.get_normalized_name() == 'Linecard1'
#     assert component_component.get_cr_name() == 'dut1-Linecard1'
#     assert component_component.get_cr_type() == 'LineCard'
#     assert component_component.get_cr_spec() == {"type": "LineCard", "node": "dut1", "slot": '1'}
#     assert component_component.get_cr_status() == {'enabled': True, 'operationalState': 'Up', 'type': 'lineCard', 'partNumber': '12345', 'serialNumber': '54321', 'manufacturedDate': '09/19/2002 00:00:00', 'lastChange': '02/06/2023 00:00:00'}
#     assert component_component.normalize_name(INPUT_PATH_3) == "Linecard1"
#     assert component_component.normalize_path(INPUT_PATH_3) == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Linecard1"}'


# def test_component_sanity_4():
#     """Sanity test for class Component"""
#     component_component = component.Component(INPUT_PATH_4, INPUT_VALUE_4)
#     assert isinstance(component_component, component.Component)
#     assert component_component.node == "dut1"
#     assert component_component.platform == constants.PLATFORM_SRL
#     assert component_component.slot == INPUT_VALUE_4["slot"]
#     assert component_component.manufactured_date == INPUT_VALUE_4["manufactured-date"]
#     assert component_component.last_change == INPUT_VALUE_4["last-change"]
#     assert component_component.oper_state == "Up"
#     assert component_component.part_number == INPUT_VALUE_4["part-number"]
#     assert component_component.serial_number == INPUT_VALUE_4["serial-number"]
#     assert component_component.normalized_path == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Fabric1"}'
#     assert component_component.normalized_name == 'Fabric1'
#     assert component_component.cr_type == "Fabric"
#     assert component_component.get_path() == INPUT_PATH_4
#     assert component_component.get_normalized_value() == {
#         "enabled": True,
#         "slot": '1',
#         "operationalState": "Up",
#         "partNumber": "12345",
#         "serialNumber": "54321",
#         "manufacturedDate": "09/19/2002 00:00:00",
#         "lastChange": "02/06/2023 00:00:00",
#         "type": 'Fabric'
#     }
#     assert component_component.get_normalized_path() == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Fabric1"}'
#     assert component_component.get_normalized_name() == 'Fabric1'
#     assert component_component.get_cr_name() == 'dut1-Fabric1'
#     assert component_component.get_cr_type() == 'Fabric'
#     assert component_component.get_cr_spec() == {"type": "Fabric", "node": "dut1", "slot": '1'}
#     assert component_component.get_cr_status() == {'enabled': True, 'operationalState': 'Up', 'type': 'fabric', 'partNumber': '12345', 'serialNumber': '54321', 'manufacturedDate': '09/19/2002 00:00:00', 'lastChange': '02/06/2023 00:00:00'}
#     assert component_component.normalize_name(INPUT_PATH_4) == "Fabric1"
#     assert component_component.normalize_path(INPUT_PATH_4) == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Fabric1"}'


# def test_component_sanity_5():
#     """Sanity test for class Component"""
#     component_component = component.Component(INPUT_PATH_5, INPUT_VALUE_5)
#     assert isinstance(component_component, component.Component)
#     assert component_component.node == "dut1"
#     assert component_component.platform == constants.PLATFORM_SRL
#     assert component_component.manufactured_date == INPUT_VALUE_5["manufactured-date"]
#     assert component_component.last_change == INPUT_VALUE_5["last-change"]
#     assert component_component.oper_state == "Up"
#     assert component_component.part_number == INPUT_VALUE_5["part-number"]
#     assert component_component.serial_number == INPUT_VALUE_5["serial-number"]
#     assert component_component.normalized_path == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Chassis"}'
#     assert component_component.normalized_name == 'Chassis'
#     assert component_component.cr_type == "Chassis"
#     assert component_component.get_path() == INPUT_PATH_5
#     assert component_component.get_normalized_value() == {
#         "enabled": True,
#         "operationalState": "Up",
#         "partNumber": "12345",
#         "serialNumber": "54321",
#         "manufacturedDate": "09/19/2002 00:00:00",
#         "lastChange": "02/06/2023 00:00:00",
#         "type": 'Chassis',
#         "slot": ''
#     }
#     assert component_component.get_normalized_path() == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Chassis"}'
#     assert component_component.get_normalized_name() == 'Chassis'
#     assert component_component.get_cr_name() == 'dut1-Chassis'
#     assert component_component.get_cr_type() == 'Chassis'
#     assert component_component.get_cr_spec() == {"type": "Chassis", "node": "dut1", "slot": ''}
#     assert component_component.get_cr_status() == {'enabled': True, 'operationalState': 'Up', 'type': 'chassis', 'partNumber': '12345', 'serialNumber': '54321', 'manufacturedDate': '09/19/2002 00:00:00', 'lastChange': '02/06/2023 00:00:00'}
#     assert component_component.normalize_name(INPUT_PATH_5) == "Chassis"
#     assert component_component.normalize_path(INPUT_PATH_5) == '.node{.name=="dut1"}.apps.components_eda_nokia_com.v1alpha1.component{.name=="Chassis"}'


# if __name__ == "__main__":
# test_get_list_request_sanity()
# test_component_sanity_1()
# test_component_sanity_2()
# test_component_sanity_3()
# test_component_sanity_4()
# test_component_sanity_5()
