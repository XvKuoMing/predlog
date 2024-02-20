import unittest
from redfa import ReDFA


class MyTestCase(unittest.TestCase):

    def test_simple_regularity(self):
        dfa = ReDFA('abc')
        self.assertTrue(dfa.match('abc'))

    def test_similarity(self):
        dfa = ReDFA('aaa')
        self.assertTrue(dfa.match('aaa'))

    def test_repetition(self):
        dfa = ReDFA('a+b+c')
        self.assertTrue(dfa.match('aaaaaaaaabbbbbbbc'))

    def test_skiping(self):
        dfa = ReDFA('ab?c')
        self.assertTrue(dfa.match('ac'))

    def test_skiping_with_repetition(self):
        dfa = ReDFA('ab*c')
        self.assertTrue(dfa.match('ac') and dfa.match('abbbbbbbbbbc'))

    def test_multiple_patterns(self):
        dfa = ReDFA('abc|ghj')
        self.assertTrue(dfa.match('ghj'))

    def test_pattern_with_sub_group(self):
        dfa = ReDFA('abc(a?h|ak)op')
        self.assertTrue(dfa.match('abchop') and dfa.match('abcahop'))

    def test_patterns_with_sub_group(self):
        dfa = ReDFA('isaac_(newton|asimov)|alexander_(I*V|VI)')
        self.assertTrue(dfa.match('isaac_newton') and dfa.match('alexander_IIV'))

    def test_patterns_with_quantified_sub_groups(self):
        dfa = ReDFA('a*bc(ot|oe)+k|ab?d(op|ol)*y')
        missing_sub_group2 = dfa.match('abdy')
        repeated_sub_group1 = dfa.match('bcotototk')
        self.assertTrue(missing_sub_group2 and repeated_sub_group1)

    def test_continuous_groups(self):
        dfa = ReDFA('(c|d)*(f|g)+|cop')
        self.assertTrue(dfa.match('cop') and
                        dfa.match('cf') and
                        dfa.match('cdcdcdcdcdcdcddggg') and
                        dfa.match('fggfgfgfgfgf') and
                        not dfa.match('cdfffffffc'))

    def test_groupes_quantified(self):
        dfa = ReDFA('(CA)+(CD)+')
        self.assertTrue(dfa.match('CACACACDCDCD') and
                        not dfa.match('CACA'))

if __name__ == '__main__':
    unittest.main()
