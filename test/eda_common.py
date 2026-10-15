#
# Stub for EDA common, so you can run your scripts in bash
#
import os
import json
import sys

DEBUG = os.getenv('DEBUG') if os.getenv('DEBUG') is not None else False
gSpecDb = {}
update_cr_list = []


class Schema:
    def __init__(self, group, version, kind):
        self.group = group
        self.version = version
        self.kind = kind

    def __eq__(self, other):
        return self.group == other.group and self.version == other.version and self.kind == other.kind

    def __hash__(self):
        return hash(self.group) ^ hash(self.kind)

    def __reduce__(self):
        return (self.__class__, (self.group, self.version, self.kind))

    def __lt__(self, other):
        return f'{self.group}_{self.kind}_{self.version}' < f'{other.group}_{other.kind}_{other.version}'


def ec_log_msg(*msg, dict=None):  # pragma: no cover
    if DEBUG:
        if msg:
            print(*msg, sep='\n')
        if dict is not None:
            if sys.implementation.name == "micropython":
                print(json.dumps(dict))
            else:
                print(json.dumps(dict, indent=4))


def update_cr(schema, name, spec=None, status=None, labels: dict = {}, annotations=None, ns=None):
    global update_cr_list
    if labels != {}:
        cr: dict
        for cr in update_cr_list:
            if cr.get('schema', None) == schema and cr.get('name', None) == name:
                for k, v in labels.items():
                    cr[k] = v
                return
    temp_cr_dict = {}
    temp_cr_dict["schema"] = schema
    temp_cr_dict["name"] = name
    if spec is not None:
        temp_cr_dict["spec"] = spec
    if status is not None:
        temp_cr_dict["status"] = status
    if labels != {}:
        temp_cr_dict["labels"] = status
    update_cr_list.insert(0, temp_cr_dict)
    ec_log_msg(f'\n{schema.group}/{schema.version}/{schema.kind} name {name}:')
    if spec is not None:
        ec_log_msg("spec", dict=spec)
        ec_log_msg(f"================ configs for {name}")
        configs = spec.get('configs', [])
        for cfg in configs:
            ec_log_msg(cfg['path'], dict=json.loads(cfg['config']))
        ec_log_msg(f"================ done {name}")
    if status is not None:
        ec_log_msg(f"status: {status}")
    if labels is not None:
        ec_log_msg(f"labels: {labels}")


def get_cr(schema, name, ns=None):
    global gSpecDb
    result = gSpecDb.get(schema, [])
    for cr in result:
        metadata = cr.get('metadata', None)
        if metadata:
            md_name = metadata.get('name', None)
            if md_name == name:
                return cr
    return ""


def process_label_filter(label_filter: list) -> list:
    label_filter_list = []
    for label in label_filter:
        if '=' in label:
            label_filter_list.append({
                'action': 'equals',
                'key': label.split('=')[0],
                'value': label.split('=')[1]
            })
        elif ' in ' in label:
            key = label.split(' in ')[0]
            values = []
            values_str = label.split(' in ')[1]
            if values_str[0] == '(' and values_str[-1] == ')':
                values = [value for value in values_str[1:-1].split(',')]
            else:
                raise AssertionError(f'Failed to parse values_str: {values_str}')
            if values == []:
                raise AssertionError(f'Failed to parse values_str: {values_str}')
            label_filter_list.append({
                'action': 'in',
                'key': key,
                'values': values
            })
        elif label[0] == '!':
            label_filter_list.append({
                'action': 'not_exists',
                'key': label[1:]
            })
        else:
            label_filter_list.append({
                'action': 'exists',
                'key': label
            })
    return label_filter_list


def list_crs(schema, filter=[], label_filter=[], fields=None, ns=None):
    # to do, apply filter
    global gSpecDb
    result = gSpecDb.get(schema, [])
    if label_filter:
        label_filter_list = process_label_filter(label_filter)
        if label_filter_list == []:
            raise AssertionError(f'Returned empty list label_filter_list for input {label_filter}')
        filtered_results = []
        for i in range(len(result)):
            labels_dict: dict = result[i].get('metadata', {}).get('labels', {})
            label: dict
            for label in label_filter_list:
                action = label.get('action', None)
                if action == 'equals':
                    if str(labels_dict.get(label['key'], '')) == label['value']:
                        filtered_results.append(result[i])
                        break
                elif action == 'in':
                    if str(labels_dict.get(label['key'], '')) in label['values']:
                        filtered_results.append(result[i])
                        break
                elif action == 'not_exists':
                    if label['key'] not in labels_dict.keys():
                        filtered_results.append(result[i])
                        break
                elif action == 'exists':
                    if label['key'] in labels_dict.keys():
                        filtered_results.append(result[i])
                        break
        return filtered_results
    return result

#
# Use this functions to add to a fake cr db
#


def test_addcr(schema, cr):
    global gSpecDb
    gvkDb = gSpecDb.get(schema, [])
    gvkDb.append(cr)
    gSpecDb[schema] = gvkDb


def test_removecr(schema, cr):
    global gSpecDb
    gvkDb = gSpecDb.get(schema, [])
    gvkDb.remove(cr)
    gSpecDb[schema] = gvkDb


class InfrastructureError(Exception):
    pass
