import string
from typing import List, Optional, Union
from .lexers import relex


def get_thread(n: int,
               prefix: Optional[str] = None) -> str:
    """Given an integer generates unique sequence of ascii uppercase letters"""
    if prefix is None:
        prefix = ''
    try:
        return prefix + string.ascii_uppercase[n]
    except IndexError:
        total = len(string.ascii_uppercase)
        j = n % total
        prefix += get_thread(n // total)
        return get_thread(j,
                          prefix=prefix)

def patterns2dfa(patterns: List[List[Union[str, List[str]]]],
                 graph: Optional[dict] = None,
                 start_state: Optional[str] = None,
                 thread_id: int = 0,
                 cycling: bool = False):
    """Builds DFA from tokenized regex patterns"""
    if graph is None:
        graph = {}

    if '<END>' not in graph.keys():
        graph['<END>'] = []  # capsule for holding finished states

    if start_state is None:
        start_state = '<START>'

    if start_state == '<START>':
        start_from = 0
    else:
        start_from = float(start_state.split(':')[0])

    branches = []  # additional branches that should be considered after execution
    incre = 0
    for n, pattern in enumerate(patterns):
        thread = get_thread(thread_id + n + incre)

        current_state = start_state

        connected = True
        generated_so_far = []
        repeat = None  # else, element
        broken = False
        for state_n, element in enumerate(pattern):
            state = state_n + start_from

            element, quant = (element[:-1], element[-1]) if element[-1] in ['+', '*', '?'] else (element, None)

            if current_state not in graph.keys():
                graph[current_state] = {}

            if isinstance(element, list):
                incre += len(element) - 1
                globals_ends = graph.pop('<END>')
                if quant in ['?', '*']:
                    branches.append(generated_so_far + pattern[state_n + 1:])
                rep = False
                if quant in ['*', '+']:
                    rep = True
                graph = patterns2dfa(patterns=element,
                                     graph=graph,
                                     start_state=current_state,
                                     thread_id=thread_id + n,
                                     cycling=rep)
                local_ends = graph.pop('<END>')
                graph['<END>'] = globals_ends
                tail = [pattern[state_n + 1:]]
                for i, start in enumerate(local_ends):
                    graph = patterns2dfa(patterns=tail,
                                         graph=graph,
                                         start_state=start,
                                         thread_id=thread_id + n + i)
                broken = True
                break

            if connected and element in graph[current_state].keys():
                next_state = graph[current_state][element]  # next state of prev thread
            else:
                next_state = str(state + 1) + ':' + thread
                graph[current_state][element] = next_state
                connected = False

            # dealing with quants
            if repeat is not None:
                if repeat not in graph[current_state].keys():
                    local_next_state = str(state + .5) + ':' + thread
                    graph[current_state][repeat] = local_next_state
                    graph[local_next_state] = {repeat: local_next_state}
                else:
                    local_next_state = graph[current_state][repeat]
                    if local_next_state not in graph.keys():
                        graph[local_next_state] = {}
                    if repeat not in graph[local_next_state].keys():
                        graph[local_next_state][repeat] = local_next_state

                if element not in graph[local_next_state].keys():
                    graph[local_next_state][element] = next_state

                repeat = None

            if quant == '+':  # ab+c > abb*c
                generated_so_far += element
                quant = '*'

            if quant in ['*', '?']:
                branches.append(generated_so_far + pattern[state_n + 1:])  # ac if ab*c
                if quant == '*':
                    repeat = element

            current_state = next_state
            generated_so_far.append(element)

        # adding end state of this pattern
        if not broken and current_state not in graph['<END>']:
            graph['<END>'].append(current_state)

    if cycling:
        for end in graph['<END>']:
            if end not in graph.keys():
                graph[end] = {}
            graph[end] = {**graph[end], **graph[start_state]}

    if bool(branches):
        graph = patterns2dfa(patterns=branches,
                             graph=graph,
                             start_state=start_state,
                             thread_id=len(patterns),
                             cycling=cycling)

    return graph


def regex2dfa(regex: str) -> dict:
    """Given regex string, gererates corresponding dfa"""
    patterns = relex(regex)
    return patterns2dfa(patterns)





