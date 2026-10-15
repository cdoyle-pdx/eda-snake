import eda_common as eda
import sys
import json


def log_msg(*msg, dict=None):  # pragma: no cover
    if eda.DEBUG:
        if msg:
            print(*msg, sep='\n')
        if dict is not None:
            if sys.implementation.name == "micropython":
                print(json.dumps(dict))
            else:
                print(json.dumps(dict, indent=4))
