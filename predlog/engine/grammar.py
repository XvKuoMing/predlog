#!/usr/bin/env python
# coding: utf-8

from .rules import BRule, CRule

class Parser:
    Rule = BRule
    """========================================Subclass==================================================="""
    class Group:
        def __init__(self, units:list, label:str):
            self.units = units
            self.label = label
        
        @property
        def flatten(self):
            _units = []
            for u in self.units:
                if isinstance(u, Parser.Group):
                    _units = [*_units, *u.flatten]
                else:
                    _units.append(u)
            return _units
        
        def __str__(self):
            return ' '.join(self.flatten)
        def __repr__(self):
            return str(self)
        
        def as_tree(self):
            tree = f'({self.label} ('
            for unit in self.units:
                if isinstance(unit, str):
                    tree += ' '+unit
                else:
                    tree += unit.as_tree()
            tree += '))'
            return tree
        
        def print_tree(self, as_svg=False)->None:
            from nltk.tree import Tree
            if as_svg:
                Tree.fromstring(self.as_tree())
            else:
                Tree.fromstring(self.as_tree()).pretty_print()
                    
    
    
    """====================================Main class========================================================"""
                    
    
    def __init__(self, rules, preprocessor=None, tokenizer=None):
        self.__raw_rules = rules
        self.tokenize = tokenizer
        self.__preprocess = preprocessor # функция предобработки (как именно нам рассматривать входные данные?)
    
    @property
    def preprocess(self):
        """Над функцией предобработки надстраиваем хэндлер для работы с деревом"""
        return lambda x: x.label if isinstance(x, Parser.Group) else        (x if self.__preprocess is None else self.__preprocess(x))
    
    @property
    def rules(self):
        """Парсим все правила: создаем базу правил"""
        rules = []
        units = self.__raw_rules.split('\n')
        for u in units:
            if bool(u.replace(' ', '')):
                nt, tms = u.split('::=')
                tms = tms.split('|')
                for tm in tms:
                    rules.append(
                        self.__class__.Rule(nt=nt.strip(), tms=tm.strip())
                    )
        return rules
    
    def parse(self, text):
        if (not isinstance(text, list)) and (self.tokenize is not None):
            text = self.tokenize(text)    
        
        for r in self.rules:
            last_index = None
            while True:
                index = r.find([self.preprocess(token) for token in text], as_index=True, only_first=True)
                if (not bool(index)) or (last_index == index): 
                    break
                grouped = Parser.Group(units=text[index], label=r.nt)
                _text = [*text[:index.start], grouped]
                if index.stop is not None:
                    _text += text[index.stop:]
                text = _text
                last_index = index
        return text
    

class CParser(Parser):
    Rule = CRule