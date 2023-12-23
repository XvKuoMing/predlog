#!/usr/bin/env python
# coding: utf-8

from engine.grammar import Parser, CParser

from razdel import tokenize
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()



gramm = """
<CONJ> ::= CONJ | COMMA <CONJ>
<S> ::= [nomn:NOUN,NPRO]+ | ADJF <S> 
<ASPECT> ::= [PREP,ADVB,ADJF]+ [NOUN,<S>] | <ASPECT> <CONJ> <ASPECT>
<PARTICIPLE> ::= COMMA PRTF [ADVB,NOUN,<ASPECT>]+ COMMA? | PRTF 
<TRANSGRESSIVE> ::= COMMA GRND [ADVB,NOUN,<ASPECT>]+ COMMA? | GRND
<S> ::= <S> [<PARTICIPLE>,<TRANSGRESSIVE>] | [<PARTICIPLE>,<TRANSGRESSIVE>] <S> | <S> <CONJ> <S>
<VP> ::= [VERB,ADJS,INFN,PRTS,COMP]+ | [ADVB,NOUN,<ASPECT>,<PARTICIPLE>,<TRANSGRESSIVE>]+ <VP> 
<VP> ::= <VP> [ADVB,NOUN,<ASPECT>,<PARTICIPLE>,<TRANSGRESSIVE>]+ | <VP> <CONJ> <VP>

<SEN> ::= [<VP>,<S>]+

"""

def precr(token):
    if token == ',':
        return 'COMMA'
    t = morph.parse(token)[0].tag
    if (t.POS == 'NOUN') and (t.case == 'nomn'):
        return 'nomn:NOUN'
    else:
        return str(t.POS)


g = Parser(rules=gramm, 
           tokenizer=lambda text: [token.text for token in tokenize(text)],
           preprocessor=precr)




simplify = lambda text: [sen for sen in g.parse(text) if hasattr(sen, 'label') and sen.label!='<CONJ>']

