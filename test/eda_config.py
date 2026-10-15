#
# Stub for eda_config module, so you can run your scripts in bash
#

gSpecDb = {}
gAllocDb = {}


def pool_name_and_key_to_string(pool_name, key):
    return pool_name + '.' + key


class Pool:
    TYPE_ANY = "Any"
    TYPE_INDEX = "Index"
    TYPE_IP = "IP"
    TYPE_IP_IN_SUBNET = "IPInSubnet"
    TYPE_SUBNET = "Subnet"

    def __init__(self, name, scope, type):
        self.name = name
        self.scope = scope
        self.type = type

    def alloc(self, key):
        alloc_key = pool_name_and_key_to_string(f'{self.name}.{self.scope}', key)
        assert alloc_key in gAllocDb, f'key {key} has not been added to pool {self.name} with scope {self.scope} - use test_add_alloc("{self.name}","{self.scope}","{key}","some-value") to add this pool/key'
        return gAllocDb[alloc_key]


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


class ConfigError(Exception):
    def __init__(self,
                 msg: str,
                 msg_key: str = None,
                 values=None):
        super().__init__(msg)
        self.msg = msg
        self.msg_key = msg_key
        self.values = values

    def __str__(self):
        result = f'ConfigError(msg={self.msg}'
        if self.msg_key is not None:
            result += f', msg_key={self.msg_key}'
        if self.values is not None:
            result += f', values={self.values}'
        result += ')'
        return result

#
# Use these functions to add prepopulate DB
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


def test_add_alloc(pool_name, scope, key, value):
    global gAllocDb
    gAllocDb[pool_name_and_key_to_string(f'{pool_name}.{scope}', key)] = value


def test_clear_all():
    """Function to clear all added CRs and allocation pools"""
    global gSpecDb
    global gAllocDb
    gSpecDb = {}
    gAllocDb = {}
