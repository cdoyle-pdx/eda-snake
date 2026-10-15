#!/usr/bin/env python3
import eda_state as estate


def get_state_params(path: str, field_list: list, isleaflist: bool):
    if isleaflist:
        try:
            stateresult_list = estate.list_db(
                path=path,
                fields=field_list,
            )
        except:  # noqa
            return None
        if stateresult_list is None:
            return None
        return stateresult_list
    else:
        try:
            stateresult = next(estate.list_db(
                path=path,
                fields=field_list,
            ))
        except:  # noqa
            return None
        if stateresult is None:
            return None
        value = stateresult['value']
        return value
