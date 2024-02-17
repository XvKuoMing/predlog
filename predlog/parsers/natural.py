from predlog.predlog.engine.grouper import Grouper
from typing import List
from warnings import warn

try:
    from pymorphy2 import MorphAnalyzer
    from razdel import tokenize

    morph = MorphAnalyzer()

except ModuleNotFoundError:
    warn('russian language parsers is disabled, please install pymorphy2 and razdel')


simple_sub_conjs = ['который', 'что', 'где', 'если', 'чтобы', 'как', 'ибо', 'пока', 'словно']
complex_sub_conjs = ['потому что', 'с тех пор как', 'так что', 'лишь только',
                      'оттого что', 'как будто']

russian_grammar = """
<CONJ> ::= ,? CONJ | ; | ,

// причастный и деепричастный обороты
<PART> ::= <CONJ> #* PRTF #+ (<CONJ>|PNCT)| <PART> <CONJ> <PART>
<TRANS> ::= <CONJ> #* GRND #+ (<CONJ>|PNCT) | <TRANS> <CONJ> <TRANS>

// обхект субъект и глагол
<OBJ> ::= (PRTF|NUMR|ADJF)* (NOUN|NPRO) | PREP (nomn_NOUN|nomn_NPRO|<OBJ>)
<SUBJECT> ::= (PRTF|NUMR|ADJF)* (nomn_NOUN|nomn_NPRO) | <SUBJECT> <CONJ> <SUBJECT>
<VERB> ::= (VERB|ADJS|COMP|PRTS|INFN|GRND|PRED|PRCL)+

// именное наречное и глагольное словосочетания
<NP> ::= <OBJ>+ (INFN|ADVB)? | <NP> <CONJ> <NP>
<AP> ::= PRCL? ADVB (ADVB|<OBJ>|ADJF)* | <AP> <CONJ> <AP>
<VP> ::=  <VERB> (<AP>|<NP>)? | <VP> <CONJ> <VP>

// подчинительное предложение и прямая речь
<SUB_SENT> ::= <CONJ> #* SUB_CONJ #+ <CONJ> | <SUB_SENT> (<CONJ>|SUB_CONJ) <SUB_SENT>
<DS> ::= : « #+ »

// предложение
<SEN> ::= (<SUBJECT>|PRCL|<NP>|<AP>|<VP>|<TRANS>|<PART>|<SUB_SENT>|<DS>)+ PNCT? | <SEN> <CONJ> <SEN>
"""

def preprocessing(token: str) -> str:
    if token in [',', ';', ':', '«', '»']:
        return token
    if ' '.join(token.split('_')) in complex_sub_conjs+simple_sub_conjs:
        return 'SUB_CONJ'  # subordinate conjunction
    tag = morph.parse(token)[0].tag
    pos = tag.POS
    if pos in ['NOUN', 'NPRO'] and 'nomn' in tag.case:
        return f'{tag.case}_{pos}'
    if pos is not None:
        return pos
    elif 'PNCT' in tag:
        return 'PNCT'
    else:
        return token

def tokenizer(text: str) -> List[str]:
    for complex_sub_conj in complex_sub_conjs:
        if complex_sub_conj in text:
            text = text.replace(complex_sub_conj, '_'.join(complex_sub_conj.split()))
    return [t.text for t in tokenize(text)]


russian_parser = Grouper(rules=russian_grammar,
                 tokenizer=tokenizer,
                 mirror=preprocessing)
