def compare(v1, v2):
    """Compares two version strings."""
    v1_list = [int(x) for x in _findall_num(v1) if x]
    v2_list = [int(x) for x in _findall_num(v2) if x]
    # Compare the lists element-wise.
    for i in range(min(len(v1_list), len(v2_list))):
        if v1_list[i] < v2_list[i]:
            return -1
        elif v1_list[i] > v2_list[i]:
            return 1

    # If the lists are equal in length, the versions are equal.
    if len(v1_list) == len(v2_list):
        return 0

    # If one list is longer, the version with the longer list is greater.
    return 1 if len(v1_list) > len(v2_list) else -1


def _findall_num(text):
    numbers = []
    i = 0
    while i < len(text):
        if text[i].isdigit():
            start = i
            while i < len(text) and text[i].isdigit():
                i += 1
            numbers.append(text[start:i])
        else:
            i += 1
    return numbers
