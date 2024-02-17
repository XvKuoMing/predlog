from predlog.engine.redfa import ReDFA
from predlog.engine.utils.lexers import wordex
from predlog.parsers.natural import parser
from predlog.parsers.formal import logician
from predlog.engine.redfa import ReCapturer

# dfa = ReDFA('abc')
# text = 'aaaaaaaaabcbcbcbbcbcbcbccccabc '
# result = dfa.findall(text)
# print('result: ', result)
# for s in result:
#     print(text[s])
#
#
# r = """
# <HI> ::= Hello World
# <PC> ::= <HI> !
# """
#
# tokenizer = lambda txt: txt.strip().split()
#
# natural_grouper = Grouper(rules=r,
#                           tokenizer=tokenizer,
#                           mirror=None)
#
# natural_result = natural_grouper.parse('Hello World !')
# print(natural_result)
# print(natural_result[0])
# print(natural_result[0].print_tree())

# p = ReDFA('(NUMR|PREP|ADJF|ADVB)* (<OO>|<DO>|<IO>)+ | <OBJ> <CONJ> <OBJ>', lex=wordex)
# print(p.graph)

#
# res = parser.parse('Петя вышел на улицу')
# print(res)
# print(res[0].label)
# res[0].print_tree()
#

# dfa = ReDFA(
#       regex='<OBJ>? PREP? <OBJ>+ | (PRTF|NUMR) <OBJ> | <OBJ> (INFN|ADVB) | <NP> <CONJ> <NP>',
#       lex=wordex)
# print(dfa.graph)
# print(dfa.final_states)

# dfa = ReDFA('#!#')
# print(dfa.graph)
# print(dfa.final_states)
# print(dfa.match('f!c'))


# res2 = parser.parse('Вскоре после восхода солнца пошел дождь и возникли тучи.')
# print(res2)
# res2[0].print_tree()
#
#
# res3 = parser.parse('Мальчик купил пельмени и пошёл домой, а девочка посмотрела в телефон и заплакала.')
# print(res3)
# res3[0].print_tree()

#
# res3 = parser.parse('Я и Петя, и Ваня вышли во двор, а Коля остался дома.')
# print(res3)
# res3[0].print_tree()
# #
# #
# #
#res3 = parser.parse('Александр стоял у дома, куря сигарету.')
#print(res3)
#res3[0].print_tree()
#
# res3 = parser.parse('Дом, который стоит около машины, очень красивый.')
# print(res3)
# res3[0].print_tree()
#
#
# res3 = parser.parse('Я не люблю кашу.')
# print(res3)
# res3[0].print_tree()
#
# res3 = parser.parse('Я ему сказал: «Так делать больше не надо»!')
# print(res3)
# res3[0].print_tree()


# r = math_parser.parse('5 + 5 = 10')
# r[0].print_tree()

# rec = ReCapturer('@!(#+)(.|!)')
# print(rec.graph)
# print(rec.final_states)
# print(rec.capture.graph)
# print(rec.capture.final_states)
# text = '@mail.ru, @gmail.com @yandex.ru'
# res = rec.findall(text)
# for r in res:
#     print(r)
#     print('@mail.ru, @gmail.com @yandex.ru'[r])


r = logician.parse('AxP(x) -> EyQ(y)')
print(r)
r[0].print_tree()


r = logician.parse('~(~(P(x, y))) & AzQ(z)')
print(r)
r[0].print_tree()


r = logician.parse('~{f(5) = 5}')
print(r)
r[0].print_tree()


r = logician.parse('Ax~{x^2 > x}')  # не верно что для каждого x, при возведении его в квадрат  полученное число > x
print(r)
r[0].print_tree()




