#
# Stub for eda_state module, so you can run your scripts in bash
#
import utils.paths as path_utils
import eda_common as eda
import json
from utils.log import log_msg

gStateDb = {}
update_alarm_list = []
update_db_list = []
scratchpad_list = {}

launch_context = None


def update_alarm(name,
                 alarm_type,
                 severity,
                 resource,
                 kind,
                 group,
                 description,
                 probable_cause=None,
                 ns=None,
                 remedial_action=None,
                 jspath=None,
                 parent_alarm=None,
                 targets_affected=None,
                 additional_text=None):
    global update_alarm_list
    temp_cr_dict = {}
    temp_cr_dict["name"] = name
    temp_cr_dict["alarmType"] = alarm_type
    temp_cr_dict["severity"] = severity
    temp_cr_dict["resource"] = resource
    temp_cr_dict["kind"] = kind
    temp_cr_dict["group"] = group
    temp_cr_dict["description"] = description
    temp_cr_dict["ns"] = ns
    temp_cr_dict["probableCause"] = probable_cause
    temp_cr_dict["remedialAction"] = remedial_action
    temp_cr_dict["jspath"] = jspath
    temp_cr_dict["parentAlarm"] = parent_alarm
    temp_cr_dict["targetsAffected"] = targets_affected
    temp_cr_dict["additionalText"] = additional_text
    update_alarm_list.insert(0, temp_cr_dict)
    if eda.DEBUG:
        print('Added alarm: ')
        print(f' name: {name}')
        print(f' alarmType: {alarm_type}')
        print(f' severity: {severity}')
        print(f' resource: {resource}')
        print(f' kind: {resource}')
        print(f' description: {description}')
        print(f' ns: {ns}')
        print(f' group: {resource}')
        print(f' probableCause: {probable_cause}')
        print(f' remedialAction: {remedial_action}')
        print(f' jspath: {jspath}')
        print(f' parentAlarm: {parent_alarm}')
        print(f' targetsAffected: {targets_affected}')
        print(f' additionalText: {additional_text}')


def list_scope(path):
    return


def get_db(path, fields, coalesce=True):
    global gStateDb
    result = {}
    json_result = gStateDb.get(path, {})
    result['path'] = path
    result['value'] = json.loads(json_result)
    return result


def list_db(path, fields, coalesce=True):
    log_msg(f'Got list_db request for path: {path}, fields: {fields}, coalesce: {coalesce}')
    global gStateDb
    result = []
    for key, value in gStateDb.items():
        if path_utils.path_prefix_match(path=key, match=path):
            result.append({
                'path': key,
                'value': json.loads(value)
            })
    return iter(result)


def update_db(path, value, ns=None):
    global update_db_list
    if ns is not None:
        if not path.startswith(".cluster"):
            if path.startswith(".namespace."):
                path.replace(".namespace.", f'.namespace{{name=="{ns}"}}.')
            else:
                path = f'.namespace{{name=="{ns}"}}' + path
    temp_dict = {}
    temp_dict["path"] = path
    temp_dict["value"] = value
    update_db_list.insert(0, temp_dict)
    log_msg('Adding to statedb:', dict=temp_dict)


def set_scratchpad_data(key, data):
    global scratchpad_list
    scratchpad_list[f'{key}'] = data
    if eda.DEBUG:
        print('Adding to scratchpad_list:')
        print(f'  Key: \'{key}\'')
        print(f'  Value: \'{data}\'')


def get_scratchpad_data(key):
    log_msg(f'Got scratchpad_list request for key: {key}')
    global scratchpad_list
    result = {}
    json_result = scratchpad_list.get(key, {})
    if len(json_result) == 0:
        return None
    result = json_result
    return result


def launch(function, key, input):
    global launch_context
    if launch_context is None:
        fn = globals()[function]
    else:
        fn = getattr(launch_context, function)
    fn(input)

#
# Use these functions to add fake information to the DB
#


def test_set_launch_context(context):
    global launch_context
    launch_context = context


def test_adddb(path, value):
    global gStateDb
    gStateDb[path] = value


def test_clear_all():
    """Function to clear all added state DB entries"""
    global gStateDb
    global scratchpad_list
    global update_alarm_list
    gStateDb = {}
    scratchpad_list = {}
    update_alarm_list = []
