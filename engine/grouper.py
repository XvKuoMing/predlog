from predlog.engine.utils.lexers import wordex
from predlog.engine.redfa import ReDFA
from typing import Callable, Optional
from warnings import warn

try:
    from nltk.tree import Tree
except ModuleNotFoundError:
    warn('parser visualisation is disabled, please install nltk.tree and try again')


class Grouper:

    class Group:
        def __init__(self, units: list, label: str):
            self.units = units
            self.label = label

        @property
        def flatten(self):
            _units = []
            for u in self.units:
                if isinstance(u, Grouper.Group):
                    _units = [*_units, *u.flatten]
                else:
                    _units.append(u)
            return _units

        def __str__(self):
            return ' '.join(self.flatten)

        def __repr__(self):
            return str(self)

        def as_tree(self):
            tree = f'({self.label}'
            for unit in self.units:
                if isinstance(unit, str):
                    tree += f' ({unit})'
                else:
                    tree += unit.as_tree()
            tree += ')'
            return tree

        def print_tree(self, as_svg: bool = False) -> None:
            if as_svg:
                Tree.fromstring(self.as_tree())
            else:
                Tree.fromstring(self.as_tree()).pretty_print()

    class Rule(ReDFA):

        def __init__(self, label: str, words_as_regex: str):
            super().__init__(regex=words_as_regex, lex=wordex)
            self.label = label

    @staticmethod
    def rules2dfa_collections(rules: str) -> tuple:
        dfa_collection = []
        for rule in rules.split('\n'):
            if '::=' in rule:
                if '//' in rule:
                    rule = rule.split('//')[0]
                label, pattern = rule.split('::=')
                dfa_collection.append(
                    Grouper.Rule(label=label.strip(), words_as_regex=pattern.strip())
                )
            else:
                unknown_text = rule.replace(' ', '').split('//')[0]
                if unknown_text:
                    warn(f'Parser does not understand: {unknown_text}, skipping it')
        return tuple(dfa_collection)

    def __init__(self, rules: str, tokenizer: Callable, mirror: Optional[Callable] = None):
        """
        :param rules: context-free grammar rules
        :param tokenizer: tokenizer for texts
        :param mirror: function that for each word gives mirror token a.k.a tags. For example: cat - Noun
        """
        self.rules = Grouper.rules2dfa_collections(rules)
        self.tokenizer = tokenizer
        self.mirror = lambda token: token.label if isinstance(token, Grouper.Group) else \
                                         (token if mirror is None else mirror(token))

    def parse(self, text: str):
        tokenized_text = self.tokenizer(text)
        for rule in self.rules:  # rules order is from top to bottom of given str
            while True:  # each rule could be used recursively
                idx = rule.search([self.mirror(token) for token in tokenized_text])
                if idx is None:
                    break
                tokenized_text = [*tokenized_text[:idx.start],
                                  Grouper.Group(units=tokenized_text[idx], label=rule.label),
                                  *tokenized_text[idx.stop:]]
        return tokenized_text
