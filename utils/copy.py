#!/usr/bin/env python3
import json


def _update_dict(data_copy, data):
    for k, v in data_copy.items():
        if v != data[k]:  # pragma: no cover
            if isinstance(v, dict):
                _update_dict(v, data[k])
            elif isinstance(v, list):
                _update_list(v, data[k])
            elif isinstance(v, float):
                data_copy[k] = data[k]


def _update_list(data_copy, data):
    for i, value in enumerate(data_copy):
        if value != data[i]:  # pragma: no cover
            if isinstance(value, dict):
                _update_dict(value, data[i])
            elif isinstance(value, list):
                _update_list(value, data[i])
            elif isinstance(value, float):
                data_copy[i] = data[i]


def json_deep_copy(data):
    if data is None:
        return data

    #  precise_float is slower, but we get more reports of diffs
    #  without it (floats being floats)
    data_copy = json.loads(json.dumps(data))
    if isinstance(data_copy, list):
        _update_list(data_copy, data)
    else:
        _update_dict(data_copy, data)

    return data_copy
