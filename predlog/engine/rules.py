#!/usr/bin/env python
# coding: utf-8

from .sequencers import DFA, Capturer
from abc import ABC, abstractmethod


class BaseRule(ABC):
    
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Правило есть просто конечный автомат с именем"""
        pass
        
    @classmethod
    def fromstring(cls, pattern):
        nt, tms = pattern.split('::=')
        return cls(nt=nt.strip(), tms=tms.strip())
    
    def __str__(self):
        return self.nt
    
    def __repr__(self):
        return str(self)


class BRule(DFA, BaseRule):
    
    def __init__(self, nt:str, tms:str):
        """Правила принимаются в следующем формате: nt — не-терминал, tms — все элементы справа
        Пример: <NP> ::= <NOUN>+
        Выражение справа может быть сформулировано в формате конечного автомата"""            
        self.nt = nt
        super().__init__([tm for tm in tms.split(' ') if bool(tm)]) # токенизатор по пробелам

class CRule(Capturer, BaseRule):
    
    def __init__(self, nt:str, tms:str):
        """Добавляется возможность использовать захват группы пример: COMMA (NOUN)"""            
        self.nt = nt
        super().__init__(CRule.lexer(tms))