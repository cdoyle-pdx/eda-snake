#!/usr/bin/env python3
MICROPYTHON = False
PYTHON = False
try:
    import ure as re
except ImportError:
    import re
    PYTHON = True
else:
    MICROPYTHON = True  # pragma: no cover


def remove_keys_from_path(path: str) -> str:
    """Remove keys from jspath.
    Implementing function for MicroPython since re.sub is not available"""
    cleaned_path = ''
    i = 0
    while i < len(path):
        if path[i] == '{':
            j = i + 1
            while j < len(path):
                if path[j] == '}':
                    i = j
                    break
                j = j + 1
        else:
            cleaned_path = cleaned_path + path[i]
        i = i + 1
    return cleaned_path


def path_prefix_match(path, match):
    cleaned_path = ''
    cleaned_match = ''
    if MICROPYTHON:  # pragma: no cover
        cleaned_path = remove_keys_from_path(path)
        cleaned_match = remove_keys_from_path(match)
    elif PYTHON:
        cleaned_path = re.sub(r'{[^}]*}', '', path)
        cleaned_match = re.sub(r'{[^}]*}', '', match)
    return cleaned_path.startswith(cleaned_match)


def nearest_ancestor_key_value(path):
    if MICROPYTHON:  # pragma: no cover
        key = ''
        value = ''
        i = len(path) - 1
        while i >= 0:
            if path[i] == '}':
                i = i - 1
                if i < 0:
                    break
                if path[i] != '"':
                    break
                i = i - 1
                if i < 0:
                    break
                end = i + 1
                start = i + 1
                while i >= 0:
                    if path[i] == '"':
                        start = i + 1
                        break
                    i = i - 1
                if start == end:
                    break
                value = path[start:end]
                i = i - 1
                if i < 0:
                    break
                if path[i] != '=':
                    break
                i = i - 1
                if i < 0:
                    break
                if path[i] != '=':
                    break
                i = i - 1
                if i < 0:
                    break
                end = i + 1
                start = i + 1
                while i >= 0:
                    if path[i] == '.':
                        start = i + 1
                        break
                    i = i - 1
                if start == end:
                    break
                key = path[start:end]
                break
            i = i - 1
        if key == '' or value == '':
            return None, None
        return key, value
    matches = list(re.finditer(r'{\.(.+?)==\"(.+?)\"}', path))
    if matches:
        # Extract the key and value from the last match
        key = matches[-1].group(1)
        value = matches[-1].group(2)
        return key, value
    return None, None


# def extract_node_from_path(path):
#     # This is not available in micropython :(
#     # pattern = r'\.(?P<key>[^{.]+)\{(?P<value>[^}]+)\}'
#     # matches = re.findall(pattern, jspath)
#     pattern = r'\.([^{]+)\{([^}]+)\}'
#     matches = []
#     pos = 0
#     while True:
#         m = re.search(pattern, path[pos:])
#         if not m:
#             break
#         matches.append((m.group(1), m.group(2)))
#         pos += len(m.group(0))

#     # Create a dictionary of the key/value pairs
#     result = {key: value.split('==')[1].strip('"') for key, value in matches}

#     # Extract the 'node' and 'srl' keys and their values
#     node = result.get('node', None)
#     srlinux = result.get('srl', None)
#     sros = result.get('sros', None)

#     if node:
#         result['node'] = node
#     if srlinux:
#         result['srl'] = srlinux
#     if sros:
#         result['sros'] = sros
#     result['path'] = path

#     return result


# def path_to_dict(path):
#     extracted = {}
#     i = 0
#     while i < len(path):
#         if path[i] == '.':
#             parent_key = ""
#             for j in range(i + 1, len(path)):
#                 if path[j] != "{":
#                     parent_key += path[j]
#                 else:
#                     i = j + 1
#                     break
#             child_key = ""
#             for j in range(i + 1, len(path)):
#                 if path[j] != "=":
#                     child_key += path[j]
#                 else:
#                     i = j + 1
#                     break
#             child_value = ""
#             for j in range(i + 1, len(path)):
#                 if path[j] != "}":
#                     child_value += path[j]
#                 else:
#                     i = j + 1
#                     break
#             if child_value[0] == '"' and child_value[-1] == '"':
#                 child_value = child_value.lstrip('"')
#                 child_value = child_value.rstrip('"')
#             else:
#                 child_value = int(child_value)
#             extracted[parent_key] = {}
#             extracted[parent_key][child_key] = child_value
#     return extracted


def get_val_for_first_key(path: str, key_name: str):
    try:
        val = re.search(f'.{key_name}=="(.+?)"', path).group(1)
    except AttributeError:
        return None
    return val
