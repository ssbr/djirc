#!/usr/bin/env python
import unittest

from lxml import etree # mock ... ?
from djirc.ui import common

class Test_dfs(unittest.TestCase):
    def test_singleton(self):
        e = etree.fromstring('<empty/>')
        self.assertEqual(list(common.dfs(e)), [(e, False), (e, True)])
    
    def test_simple_nested(self):
        A = etree.Element('A')
        B = etree.SubElement(A, 'B')
        self.assertEqual(list(common.dfs(A)),
            [(A, False),
                (B, False),
                (B, True),
            (A, True)])
    
    def test_nested_traversal_order(self):
        # test that B comes before C
        A = etree.Element('A')
        B = etree.SubElement(A, 'B')
        C = etree.SubElement(A, 'C')
        self.assertEqual(list(common.dfs(A)),
            [(A, False),
                (B, False),
                (B, True),
                (C, False),
                (C, True),
            (A, True)])

class AbstractTest__etree_to_strings(unittest.TestCase):
    __test__ = False
    def test_empty(self):
        e = etree.fromstring('<empty/>')
        self.assertEqual(list(self.func(e)), [])
        
    def test_nested_emptytail(self):
        e = etree.fromstring('<full><empty/> test</full>')[0]
        if e.tail != ' test':
            raise Exception(e.tail, "e.tail should be ' test'")
        self.assertEqual(list(self.func(e)), [])
        
    def test_contents(self):
        e = etree.fromstring('<full>not empty</full>')
        self.assertEqual(list(self.func(e)), ['not empty'])
        
    def test_nested_contents(self):
        e = etree.fromstring('<full>very<full>not</full>empty</full>')
        self.assertEqual(list(self.func(e)), ['very', 'not', 'empty'])
    
    def test_nested_traversal_order(self):
        e = etree.fromstring(
            '<full><full>not</full><full2>empty</full2></full>')
        self.assertEqual(list(self.func(e)), ['not', 'empty'])

class Test__etree_to_strings(AbstractTest__etree_to_strings):
    def setUp(self):
        self.func = common._etree_to_strings

class Test__etree_to_strings2(AbstractTest__etree_to_strings):
    def setUp(self):
        self.func = common._etree_to_strings2

if __name__ == '__main__':
    unittest.main()
