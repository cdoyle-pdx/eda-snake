#!/usr/bin/env python3
#
# example use:
#     kubectl get srlconfigs.core.eda.nokia.com -o json | srlconfig_pp.py
#     kubectl get srlconfigs.core.eda.nokia.com gen-srlcfg-vrf-red-dut1 -o json | srlconfig_pp.py
#

import sys
import json
import textwrap

from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import JsonLexer


def dumpCrCfg(cr):
    name = cr['metadata']['name']
    print(f'{name}')
    for cfg_tuple in cr['spec']['configs']:
        print(f'    {cfg_tuple["path"]}')
        cfg_json_str = cfg_tuple['config']
        pp_json = json.dumps(json.loads(cfg_json_str), indent=4)
        pp_json = textwrap.indent(pp_json, "    ")
        pp_json = highlight(
            pp_json,
            lexer=JsonLexer(),
            formatter=Terminal256Formatter(),
        )
        print(pp_json)


if __name__ == "__main__":
    jsonStr = ""
    for line in sys.stdin:
        jsonStr += line

    crs = json.loads(jsonStr)

    if 'items' in crs:
        # output was from a list
        for cr in crs['items']:
            dumpCrCfg(cr)
    else:
        # output was from an individual get
        dumpCrCfg(crs)
