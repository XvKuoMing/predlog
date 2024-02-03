from typing import Union, List

def relex(reg: str) -> List[Union[str, List[str]]]:
    regex = [[]]
    grouping = False
    group = [[]]
    n = 0
    g = 0
    for char in reg:
        current_l = group[g] if grouping else regex[n]

        if char == '(':
            grouping = True
            group = [[]]
            g = 0
            continue

        elif char == ')':
            grouping = False
            regex[n].append(group)
            continue

        if char in ['?', '+', '*']:
            try:
                current_l[-1] += char
            except TypeError:
                current_l[-1].append(char)
            continue

        if char == '|':
            if grouping:
                group.append([])
                g += 1
            else:
                regex.append([])
                n += 1
            continue

        current_l.append(char)

    return regex
