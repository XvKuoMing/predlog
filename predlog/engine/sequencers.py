#!/usr/bin/env python
# coding: utf-8

# In[9]:


import json
from typing import Union, List

class DFA:
    
    """----------------------------------Функция для инициализации-----------------------------------------"""
    @staticmethod
    def generate_graph(pattern:List[str])->dict:
        """Генерация графа следования по паттерну, оформленного в виде списка"""
        # функция, которая возвращает элемент без оператора
        _ = lambda el: (el[:-1] if len(el)>1 else el) if el[-1] in ['*', '?', '+'] else el
        # функция, которая разбирает сгруппированный элемент на список элементов
        dissimilate = lambda grouped: [grouped.split('_')[0]+'_'+e.strip() for e in _(grouped.split('_')[1])[1:-1].split(',')]
        
        
        def isclosed(grouped:str)->bool:
            """Проверка элемента на сгруппированность"""
            if (']' in grouped) ^ ('[' in grouped):
                raise TypeError(f'{grouped} is not closed')
            return True if '[' in grouped else False
        
        def disambiguate(l:list, where:list)->list:
            """Если какой-то из элементов l встречался в where с тем же номером, то мы увеличиваем номер"""
            l2 = l.copy()
            for i in l:
                n = 2
                original_i = i
                while i in where:
                    i = f'{n}_'+i.split('_')[1]
                    n += 1
                else:
                    l2.remove(original_i)
                    l2.append(i)
            return l2

        def dissimilated(g:dict)->dict:
            """Разложение всех сгруппированных элементов графа"""
            dissimilated_v = []
            for k, v in g.copy().items():
                for i in v:
                    if isclosed(i):
                        g[k].remove(i)
                        dissimilated_i = dissimilate(i)
                        dissimilated_i = disambiguate(dissimilated_i, dissimilated_v)
                        dissimilated_v = [*dissimilated_v, *dissimilated_i]
                        g[k] = [*g[k], *dissimilated_i]
                    else:
                        dissimilated_v.append(i)
                if isclosed(k):
                    changing_values = g.pop(k)
                    dissimilated_k = dissimilate(k)
                    dissimilated_k = disambiguate(dissimilated_k, g.keys())
                    for new_key in dissimilated_k:
                        g[new_key] = changing_values
            return g 
        
        # 0) посчитаем унакальные элементы
        def figure_out_order(pattern:list, uniq:Union[list, None]=None)->list:
            ol = []
            _uniques = [] if uniq is None else uniq
            for el in pattern:
                _el = _(el)
                if isclosed(_el):
                    _uniques = [*_uniques, *figure_out_order(_el[1:-1].split(','), uniq=_uniques)]
                n = 1
                while f'{n}_{_el}' in _uniques:
                    n += 1
                else:
                    el = f'{n}_{el}'
                    _el = f'{n}_{_el}'
                    _uniques.append(_el)
                    ol.append(el)
            return ol
        
        ol = figure_out_order(pattern)
        
        # 1) Создаем список разложенных элементов без оператора, добавляем ключевые слова
        ## отдельно сохраняем элементы, которые были квантифицированы
        raw = ['<START>']
        _raw = ['<START>'] # список без разложения
        lazy_quantified = []
        self_quantified = []
        for el in ol:
            pure_el = _(el)
            _raw.append(pure_el)
            pure_el = dissimilate(pure_el) if isclosed(pure_el) else [pure_el]
            pure_el = disambiguate(pure_el, raw)
            if el[-1] in ['*', '?']: # элементы, которых может не быть
                lazy_quantified = [*lazy_quantified, *pure_el]
            if el[-1] in ['+', '*']: # элементы которые доступны из самих себя
                self_quantified = [*self_quantified, *pure_el]
            raw = [*raw, *pure_el]
        raw.append('<END>')
        _raw.append('<END>')
        
        # 2) создаем наивный граф следования (каждый следующий элемент следует из другого, операторы исключаем)
        ## делаем тоже самое для обратного графа
        graph = dissimilated({transition:[state] for transition, state in zip(_raw, _raw[1:])})
        reversed_graph = {}
        for k, vals in graph.items():
            for v in vals:
                if v not in reversed_graph.keys():
                    reversed_graph[v] = []
                reversed_graph[v].append(k)

        
        # 3) Теперь вынесем код для итерации по raw (чтобы использовать рекурсию)
        def eval_element(el:str, val:Union[list, None]=None)->None:
            """Если был передан только el, то мы смотрим,
            был ли он квантифицирован, если да, то обновляем граф по правилу
            если был передан val, то мы добавим все элементы из val к el"""
            nonlocal graph
            
            if val is not None:
                for v in val:
                    if ('_' in el) and ('_' in v):
                        v_similar_to_el = (el!=v) and (v.split('_')[1] == el.split('_')[1])
                        el_already_contains_itself = el in graph[el]
                        if v_similar_to_el and el_already_contains_itself:
                            raise TypeError(f'you cannot type the same element after * or +, pattern such as a*a is prohibited')
                    
                    if v not in graph[el]:
                        graph[el].append(v)
                        if v in lazy_quantified:
                            eval_element(el, graph[v])
            else:
                
                if el in self_quantified:
                    eval_element(el, [el]) # добавляем элемент к себе же
                if el in lazy_quantified:
                    pre = reversed_graph[el] # достаем все элементы до el
                    post = graph[el] # достаем все элементы после el
                    for e in pre:
                        eval_element(e, post)
        
        # 4) итерируя, мы изменяем граф
        for e in raw[1:-1]: # слова START и END мы не трогаем
            eval_element(el=e)
        return graph
    
    """-------------------------------------------------------инициализация----------------------------------------"""
    def __init__(self, pattern:List[str])->None:
        self.__raw_pattern = pattern
    
    @property
    def pattern(self):
        if not isinstance(self.__raw_pattern, list):
            raise TypeError(f'pattern must be a list, not {type(value)}')
        return self.__raw_pattern
    
    @pattern.setter
    def pattern(self, value:List[str]):
        self.__raw_pattern = value
        return self.pattern
    
    @property
    def graph(self):
        """Создаем граф по паттерну"""
        return DFA.generate_graph(self.pattern)
    
    def as_json(self, fname:Union[str, None]):
        if fname is not None:
            with open(fname, 'w') as f:
                json.dump(self.graph, f+'.json')
        return json.dumps(self.graph)
    
    def match(self, value:List[str])->bool:
        """Строгое совпадение с паттерном
        :params: value — iterable"""
        g = self.graph
        awaited = g['<START>']
        for v in value:
            allowed_lexicon = [element.split('_')[1] for element in awaited if element != '<END>']
            n = 1
            if v not in allowed_lexicon:
                return False
            while not (f'{n}_{v}' in awaited):
                n += 1
            else:
                awaited = g[f'{n}_{v}']
        return '<END>' in awaited
    
    def find(self, values:List[str], as_index:bool=False, only_first:bool=False)->Union[List[str], str]:
        """Ищет все возможные совпадения с values
        :params: values — iterable
        :returns: найденные слова или их индексы если index=True"""
        matched = []
        skip = -1
        for start in range(len(values)):
            for end in range(len(values[start:])):
                if start >= skip:
                    index = slice(start, -end) if end != 0 else slice(start, None)
                    got = values[index]
                    if self.match(got):
                        result = index if as_index else got
                        if only_first:
                            return result
                        matched.append(result)
                        skip = len(values) - end
        return matched

    
"""======================================================================================================"""
class Capturer(DFA):
    
    """-------------------------------------------lexer------------------------------------------------"""
    @staticmethod
    def lexer(pattern:str, sep:str=' ')->List[Union[str, List[str]]]:
        """токенизатор паттерна по заданному сепаратору, влючает обработку захват-групп"""
        tokens = []
        token = ''
        inside_group = False
        for char in pattern:
            if char == '(':
                inside_group = True
                continue
            if char == ')':
                tokens.append(Capturer.lexer(token.strip()))
                inside_group = False
                token = ''
                continue
            if bool(token) and ((char == sep) and not inside_group):
                tokens.append(token.strip())
                token = ''
            else:
                token += char
        if bool(token):
            tokens.append(token.strip())
        return tokens
    
    """------------------------------------initialize params--------------------------------"""
    def __init__(self, pattern:list)->None:
        """Позволяет в паттерне указать под-паттерн, которая играет роль захватывающей группы
        под-паттерн — тоже должен быть в виде списка"""
        pat = []
        self.subpattern = None
        for element in pattern:
            if isinstance(element, list):
                if self.subpattern is not None:
                    raise ValueError('Допускается только одна захват группа')
                pat = [*pat, *element]
                self.subpattern = element
            else:
                pat.append(element)
        super().__init__(pat)
        
    @property
    def capture(self):
        if self.subpattern is None:
            return None
        else:
            return DFA(self.subpattern) # вспомогательный автомат
    
    @classmethod
    def fromstring(cls, pattern:str):
        return cls(Capturer.lexer(pattern))
    
    """========================================================functions=================================="""
    def find(self, values, as_index=False, only_first=False)->Union[List[str], str]:
        if self.capture is None:
            return super().find(values, as_index, only_first)
        
        results = super().find(values, as_index=True, only_first=False)
        
        captured = []
        for index in results:
            # так как у нас одна группа, не будем тратить время, поставим only_first=True
            capt = self.capture.find(values[index], as_index=True, only_first=True)
            
            start = index.start+capt.start
            
            index_end = 0 if index.stop is None else index.stop
            capt_end = 0 if capt.stop is None else capt.stop
            end = index_end+capt_end
            if end == 0:
                end = None
            i = slice(start, end)
            focused = i if as_index else values[i]
            if only_first:
                return focused
            captured.append(focused)
        return captured