#!/usr/bin/env python
import unittest

from djirc import eventtemplates

class TestJinjaTemplateDict(unittest.TestCase):
    def test_escapes_html(self):
        d = eventtemplates.JinjaTemplateDict(dict(t="<b>{{foo}}</b>"))
        t = d['t']
        self.assertEqual(t.render(foo="<br/>"), "<b>&lt;br/&gt;</b>")
