from predlog.predlog.engine.grouper import Grouper
import string


first_order_predicate_logic = """
// целые и дробные числа
<DIG> ::= DIG+ | <DIG> . <DIG>
// арифмитическая операция
<OPERATION> ::= PLUS|MINUS|DIV|POW 
// кванторы
<QUANT> ::= (A|E) letter
// аргумент = число или переменная
<ARG> ::= <DIG>|letter
<EXPR> ::= <ARG> <OPERATION> <ARG>| { <EXPR> } | <EXPR> <OPERATION> <EXPR>
// функция любой набор слов после которых идет скобки и в них -- цифры или мат выражение
<FUNC> ::= letter+ { (<DIG>|<EXPR>|letter) }
// функциональное выражение  любое мат выражение с =
// логическое отрицание
<NEG> ::= ~
// логические бинарные операторы
<BIN_OPERATOR> ::= → | & | V
// аргументы предиката = любая цифра переменная или математетическое выражение 
<ARGS> ::= (<ARG>|<EXPR>) (, <ARG>)* | (<ARG>|<EXPR>) (, <EXPR>)* 
//название предиката
<PREDICATE_NAME> ::= LETTER (letter|LETTER)*
// = - это специальный бинарный предикат
<BIN_PREDICATE_NAME> ::= = | > | <
<BIN_PREDICATE> ::= (<QUANT>|<NEG>)* { (<ARGS>|<FUNC>) <BIN_PREDICATE_NAME> (<ARGS>|<FUNC>) }
<PREDICATE> ::= (<QUANT>|<NEG>)* <PREDICATE_NAME> { <ARGS> } | <EQUAL>
<FORMULA> ::= (<PREDICATE>|<FORMULA>) <BIN_OPERATOR> (<PREDICATE>|<FORMULA>) | <NEG> { (<PREDICATE>|<FORMULA>) }
"""

tokenize = lambda text: [token for token in
                         list(text.replace('->', '→').replace('(', '{').replace(')', '}'))
                         if token.replace(' ', '')]

def preprocessing(token: str) -> str:
    if token in ['A', 'E', 'V']:
        return token
    if token in string.ascii_uppercase:
        return 'LETTER'
    if token in string.ascii_lowercase:
        return 'letter'
    if token.isnumeric():
        return 'DIG'
    if token == '+':
        return 'PLUS'
    if token == '-':
        return 'MINUS'
    if token == '/':
        return 'DIV'
    if token == '^':
        return 'POW'
    return token


logician = Grouper(rules=first_order_predicate_logic,
                   tokenizer=tokenize,
                   mirror=preprocessing)
