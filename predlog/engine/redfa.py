from .utils.graphs_builder import regex2dfa
from copy import deepcopy


class ReDFA:
    __start_state = '<START>'

    def __init__(self, regex: str) -> None:
        transition_graph = regex2dfa(regex)
        self.__regex = regex
        self.__final_states = transition_graph.pop('<END>')
        self.__transitions = transition_graph

    @property
    def graph(self):
        return deepcopy(self.__transitions)

    @property
    def final_states(self):
        return deepcopy(self.__final_states)

    def __str__(self):
        return self.__regex

    def __repr__(self):
        return str(self)

    def match(self, text: str) -> bool:
        """Given any string sequence, iterates it through dfa and returns True if such path exists"""
        current_state = self.__start_state
        for element in text:
            try:
                valid = self.__transitions[current_state]
            except KeyError:
                return False  # if the state does not have transition, its the pattern end
            if element in valid.keys():  # if element is valid, then go further
                current_state = valid[element]
            else:  # if element is not valid, it's simply false
                return False
        return current_state in self.__final_states  # check if such end is allowed

