from .utils.graphs_builder import regex2dfa
from copy import deepcopy
from warnings import warn


try:
    import matplotlib.pyplot as plt
    import networkx as nx
except ModuleNotFoundError:
    warn("To use draw method of ReDFA install metplotlib and networkx")
    


class ReDFA:
    __start_state = '<START>'

    def __init__(self, regex: str) -> None:
        transition_graph = regex2dfa(regex)
        self.__regex = regex
        self.__final_states = transition_graph.pop('<END>')
        self.__transitions = transition_graph

    @property
    def graph(self) -> dict:
        return deepcopy(self.__transitions)

    @property
    def final_states(self) -> list:
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

    def draw(self, 
             figzise: tuple = (15, 10), dpi: int = 60,
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
        plt.figure(figsize=figzise, dpi=dpi)
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

