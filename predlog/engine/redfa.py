from predlog.predlog.engine.utils.graphs_builder import patterns2dfa
from predlog.predlog.engine.utils.lexers import relex
from copy import deepcopy
from typing import Optional, Callable,  List, Union
from warnings import warn


try:
    import matplotlib.pyplot as plt
    import networkx as nx
except ModuleNotFoundError:
    warn("To use draw method of ReDFA install metplotlib and networkx")


class ReDFA:
    __start_state = '<START>'

    def __init__(self, regex: str, lex: Optional[Callable] = None) -> None:
        """
        :param regex: str of regex pattern
        :param wordex: if true use wordex as lexer, else regex lexer
        """
        if lex is None:
            lex = relex
        transition_graph = patterns2dfa(lex(regex))
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

    def match(self, text: Union[str, list]) -> bool:
        """Given any string sequence, iterates it through dfa and returns True if such path exists"""
        current_state = self.__start_state
        for element in text:
            try:
                valid = self.__transitions[current_state]
            except KeyError:
                return False  # if the state does not have transition, its the pattern end
            if element in valid.keys():  # if element is valid, then go further
                current_state = valid[element]
            elif '#' in valid.keys():  # as any class
                current_state = valid['#']
            else:  # if element is not valid, it's simply false
                return False
        return current_state in self.__final_states  # check if such end is allowed

    def __find(self, text: Union[str, list[str]], only_first: bool = False) -> Union[List[slice], slice]:
        """Given text, returns all slices if only first is false else only first slice that matches the pattern"""
        found = []
        skipped_until = -1
        for start in range(len(text)):
            if start >= skipped_until:
                for _end in range(len(text[start:]), 0, -1):
                    end = start+_end
                    word_slice = slice(start, end)
                    if self.match(text[word_slice]):
                        if only_first:
                            return word_slice
                        found.append(word_slice)
                        skipped_until = end
                        break
        return None if only_first else found

    def search(self, text: Union[str, list[str]]) -> slice:
        """Given text, returns only first matched slice"""
        return self.__find(text=text, only_first=True)

    def findall(self, text: Union[str, list[str]]) -> List[slice]:
        """Given text, returns all matched slices"""
        return self.__find(text=text, only_first=False)

    def draw(self, 
             figsize: tuple = (15, 10), dpi: int = 100,
             edge_color: str = "black", width: int = 1, linewidths: int =1,
             node_size: int = 500, node_color: str = 'pink', alpha: float = 0.9, font_color: str = 'red') -> None:
        """Draws directed graph"""
        edges = []
        edge_labels = {}
        
        for s1, transit in self.__transitions.items():
          for label, s2 in transit.items():
            edge = [s1, s2]
            edges.append(edge)
            edge_labels[tuple(edge)] = label
        
        G = nx.DiGraph()
        G.add_edges_from(edges)
        pos = nx.spring_layout(G)
        plt.figure(figsize=figsize, dpi=dpi)
        nx.draw(
            G, pos, edge_color=edge_color, width=width, linewidths=linewidths,
            node_size=node_size, node_color=node_color, alpha=alpha,
            labels={node: node for node in G.nodes()}
        )
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_color=font_color
        )
        plt.axis('off')
        plt.show()


class ReCapturer(ReDFA):

    def __init__(self, regex: str, lex: Optional[Callable] = None) -> None:
        self.capture = None
        capture_groups_split = regex.split('!(')
        if len(capture_groups_split) == 1:
            super().__init__(regex, lex)
        elif len(capture_groups_split) == 2:
            capture_group = capture_groups_split[1].split(')')
            quant = ''
            if capture_group[1][0] in ['+', '*', '?']:
                quant = capture_group[1][0]
            capture_group = '(' + capture_group[0] + ')' + quant
            super().__init__(regex.replace('!(', '('), lex)
            self.capture = ReDFA(capture_group, lex)
        else:
            raise ValueError('Only one capture group is allowed')

    def __find_in_contexts(self, text: Union[str, List[str]], contexts: List[slice]) -> List[slice]:
        found = []
        for context in contexts:
            local_context = self.capture.search(text[context])
            start = context.start + local_context.start
            end = start + local_context.stop
            capture_group_slice = slice(start+1, end-1)
            found.append(capture_group_slice)
        return found

    def findall(self, text: Union[str, List[str]]) -> List[slice]:
        contexts = super().findall(text)
        return self.__find_in_contexts(text, contexts)

    def search(self, text: Union[str, list[str]]) -> Optional[slice]:
        context = super().search(text)
        if context:
            return self.__find_in_contexts(text, [context])[0]
        return None
