from .testutil import LsTestCase
from keywords import XSCALE
from parsing import Script


def parse(text):
    script = Script(text)
    script.parse()
    return script.script_parser.parameters.val[XSCALE]


class TestBasic(LsTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_simple(self):
        text = '''
        n_subjects        : 1
        mechanism         : SR
        behaviors         : b
        stimulus_elements : s1, s2
        start_v           : s1->b:0, default:-1
        alpha_v           : 0.1
        alpha_w           : 0.1
        beta              : 1
        behavior_cost     : default:0
        u                 : s1:2, default:0
        xscale: s1->b
        '''
        c = parse(text)
        expected = ['s1', 'b']
        self.assertEqual(c, expected)

    def test_long_chain(self):
        text = '''
        behaviors         : b1, b2, b3
        stimulus_elements : s1, s2, s3
        xscale: s1->   b1->s2  ->b2-> s3 ->   b3
        '''
        c = parse(text)
        expected = ['s1', 'b1', 's2', 'b2', 's3', 'b3']
        self.assertEqual(c, expected)

    def test_chain_with_compound_stimulus(self):
        text = '''
        behaviors         : b1, b2, b3
        stimulus_elements : s1, s2, s3
        xscale: s1->   b1-> s1,s2  ->b2-> s1,s2,s3 ->   b3
        '''
        c = parse(text)
        expected = ['s1', 'b1', ('s1', 's2'), 'b2', ('s1', 's2', 's3'), 'b3']
        self.assertEqual(c, expected)


class TestExceptions(LsTestCase):
    def setUp(self):
        pass

    def test_before_stimulus_elements(self):
        text = '''
        behaviors         : b
        xscale: s1->b
        stimulus_elements : s1, s2
        '''
        msg = "The parameter 'stimulus_elements' must be assigned before the parameter 'xscale'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_before_behaviors(self):
        text = '''
        stimulus_elements : s1, s2
        xscale: s1->b
        behaviors         : b
        '''
        msg = "The parameter 'behaviors' must be assigned before the parameter 'xscale'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_empty_name(self):
        text = '''
        stimulus_elements: s1, s2, s3
        behaviors: b1, b2
        xscale:
        '''
        msg = "Parameter 'xscale' is not specified."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_wrong_chain_behavior(self):
        text = '''
        behaviors         : b1, b2, b3
        stimulus_elements : s1, s2, s3
        xscale: s1->b1->s2->s1->s3
        '''
        msg = "Expected behavior name, got 's1'."
        with self.assertRaisesX(Exception, msg):
            parse(text)

    def test_wrong_chain_stimulus(self):
        text = '''
        behaviors         : b1, b2, b3
        stimulus_elements : s1, s2, s3
        xscale: s1->b1->b3->foo->bar
        '''
        msg = "Expected stimulus element, got 'b3'."
        with self.assertRaisesX(Exception, msg):
            parse(text)
