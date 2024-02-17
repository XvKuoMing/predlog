import string
from typing import List, Optional


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

def patterns2dfa(patterns: List[List[str]],
                 graph: Optional[dict] = None,
                 start_state: Optional[str] = None,
                 thread_id: int = 0,
                 cycling: bool = False):
    """Builds DFA from lex regex patterns"""
    if graph is None:
        graph = {}

    if '<END>' not in graph.keys():
        graph['<END>'] = []  # capsule for holding finished states

    if start_state is None:
        start_state = '<START>'

    if start_state == '<START>':
        start_from = 0
    else:
        _sta = start_state.split(':')[0]
        try:
            start_from = int(_sta)
        except ValueError:
            start_from = float(_sta)

    protected_start = {}  # elements that must not be manipulated
    if cycling and start_state in graph.keys():
        protected_start = graph.pop(start_state)

    execute_ambiguous = []
    for n, pattern in enumerate(patterns):
        thread = get_thread(thread_id + n)

        current_state = start_state

        connected = True
        repeat = None  # else, element
        skips = []
        broken = False
        for state_n, element in enumerate(pattern):
            state = state_n + start_from

            element, quant = (element[:-1], element[-1]) if element[-1] in ['+', '*', '?'] else (element, None)

            if current_state not in graph.keys():
                graph[current_state] = {}

            if isinstance(element, list):
                for skipped_state in skips:
                    head = []
                    if skipped_state != start_state:
                        _sta = skipped_state.split(':')[0]
                        skipped_state_n = int(_sta)
                        head = pattern[:skipped_state_n]
                    tail = pattern[state_n:]
                    execute_ambiguous.append(head + tail)

                globals_ends = graph.pop('<END>')
                rep = True if quant in ['+', '*'] else False
                graph = patterns2dfa(patterns=element,
                                     graph=graph,
                                     start_state=current_state,
                                     thread_id=thread_id,
                                     cycling=rep)
                if repeat is not None:
                    graph[local_next_state] = {**graph[local_next_state], **graph[current_state]}
                    repeat = None

                thread_id += len(element)

                local_ends = graph.pop('<END>')
                tail = [pattern[state_n + 1:]]
                if quant in ['?', '*']:
                    skips.append(current_state)
                else:
                    skips = []
                for i, start in enumerate(local_ends + skips):
                    graph = patterns2dfa(patterns=tail,
                                         graph=graph,
                                         start_state=start,
                                         thread_id=thread_id + n + i)

                thread_id += len(graph['<END>'])
                graph['<END>'] = [*globals_ends, *graph['<END>']]
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
                if element not in graph[local_next_state].keys():
                    graph[local_next_state][element] = next_state
                repeat = None

            for last_state in skips:
                if element in graph[last_state].keys():
                    head = []
                    if last_state != start_state:
                        _sta = last_state.split(':')[0]
                        start_state_n = int(_sta)
                        head = pattern[:start_state_n]
                    tail = pattern[state_n:]
                    execute_ambiguous.append(head + tail)  # executing as different pattern a?b?ad == abad | ad
                    continue
                else:
                    graph[last_state][element] = next_state

            if quant in ['*', '+']:
                repeat = element
                if next_state not in graph.keys():
                    graph[next_state] = {}
                if repeat not in graph[next_state].keys():
                    local_next_state = str(state + 1.5) + ':' + thread
                    graph[next_state][repeat] = local_next_state
                    graph[local_next_state] = {repeat: local_next_state}
                else:
                    local_next_state = graph[next_state][repeat]
                    if local_next_state not in graph.keys():
                        graph[local_next_state] = {}
                    if repeat not in graph[local_next_state].keys():
                        graph[local_next_state][repeat] = local_next_state

            if quant in ['?', '*']:
                skips.append(current_state)
            else:
                skips = []

            current_state = next_state

        # adding end state of this pattern
        if not broken:
            if repeat is not None:
                skips += [local_next_state]

            for end_state in skips + [current_state]:
                if end_state not in graph['<END>']:
                    graph['<END>'].append(end_state)

    if execute_ambiguous:
        graph = patterns2dfa(patterns=execute_ambiguous,
                             graph=graph,
                             start_state=start_state,
                             thread_id=thread_id)

    if cycling:
        for end_st in graph['<END>']:
            if end_st not in graph.keys():
                graph[end_st] = {}
            graph[end_st] = {**graph[end_st], **graph[start_state]}
        graph[start_state] = {**protected_start, **graph[start_state]}
    return graph





