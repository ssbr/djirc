#!/usr/bin/env python
import unittest
from djirc.ui import wx
import cssutils

class Test__styles2dict(unittest.TestCase):
    def test_invalid_args(self):
        self.assertRaises(ValueError, wx._styles2dict, [])
    
    def test_insufficient_styling(self):
        css_text = "body {color: #ff00ff; }"
        style = cssutils.parseString(css_text).cssRules[0].style
        
        self.assertRaises(ValueError, wx._styles2dict, [style])
    
    def test_insufficient_partial_cascade(self):
        css_text1 = "body {background-color: #00ff00;}"
        style1 = cssutils.parseString(css_text1).cssRules[0].style
        css_text2 = "body {color: #0000ff;}"
        style2 = cssutils.parseString(css_text2).cssRules[0].style
        
        self.assertRaises(ValueError, wx._styles2dict, [style1, style2])
    
    def test_basic(self):
        css_text = (
            "body {color: #ff00ff; "
            "background-color: #00ff00; "
            "font-family: monospace;}")
        style = cssutils.parseString(css_text).cssRules[0].style
        
        self.assertEqual(wx._styles2dict([style]),
            {
                'color': (255, 0, 255),
                'background-color': (0, 255, 0),
                'font-family': ['monospace']})
    
    def test_partial_cascade(self):
        css_text1 = (
            "body {background-color: #00ff00; "
            "font-family: monospace;}")
        style1 = cssutils.parseString(css_text1).cssRules[0].style
        css_text2 = "body {color: #0000ff;}"
        style2 = cssutils.parseString(css_text2).cssRules[0].style
        
        self.assertEqual(wx._styles2dict([style1, style2]),
            {
                'color': (0, 0, 255),
                'background-color': (0, 255, 0),
                'font-family': ['monospace']})
    
    def test_cascade(self):
        css_text1 = (
            "body {color: #ff00ff; "
            "background-color: #00ff00; "
            "font-family: monospace;}")
        style1 = cssutils.parseString(css_text1).cssRules[0].style
        css_text2 = (
            "body {color: #0000ff; "
            "background-color: #ff0000; "
            "font-family: arial;}")
        style2 = cssutils.parseString(css_text2).cssRules[0].style
        
        self.assertEqual(wx._styles2dict([style1, style2]),
            {
                'color': (0, 0, 255),
                'background-color': (255, 0, 0),
                'font-family': ['monospace', 'arial']})

    
class Test__dict2TextAttr(object):
    pass
