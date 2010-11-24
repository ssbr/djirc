#!/usr/bin/env python
# import webcolors # - optional dependency (see below)
import os

DATA_DIR = os.path.join(__file__, '..', '..', 'data')

def dfs(e):
    """Yield `(element, seen)` pairs from an tree of sequences in DFS order
    
    Will "visit" nodes twice: once on the way down, once on the way up.
    On the way down, seen will be False. On the way up, seen will be True.
    
    
    >>> list(dfs([(), [(), {}]]))
    [
        ([(), [(), {}]], False),
            ((), False),
            ((), True),
            ([(), {}], False),
                ((), False),
                ((), True),
                ({}, False),
                ({}, True),
            ([(), {}], True),
        ([(), [(), {}]], True)]
    
    The intended use is to see .text on the way down, and .tail on the way up.
    
    """
    # node, seen
    stack = [[e, False]]
    while stack:
        e, seen = stack[-1]
        yield e, seen
        if seen:
            stack.pop()
        else:
            stack[-1][1] = True
            stack.extend(reversed([[sub, False] for sub in e]))

def _etree_to_strings(e):
    """Yield string parts of an etree Element and subelements"""
    for node, seen in dfs(e):
        if not seen and node.text:
                yield node.text
        elif seen and node is not e and node.tail:
                yield node.tail

def _etree_to_strings2(e, final=True):
    # WANT ...
    if e.text:
        yield e.text
    for sub in e:
        for s in _etree_to_strings2(sub, False):
            yield s
    if not final and e.tail:
        yield e.tail

def etree_tostring(e):
    """Convert an etree Element and subelements to a flat string
    
    >>> etree_tostring(etree.fromstring(
    ... '<p>Hello <b><i>wor</i>ld</b>! &lt;3</p>'))
    'Hello world! <3'
    """
    return ''.join(_etree_to_strings(e))

try:
    import webcolors
except ImportError:
    def css_color_to_rgb(color):
        # defer to whatever handles colors
        # (wx, at least, can handle a subset of CSS-colors)
        return color
else:
    def css_color_to_rgb(color):
        # TODO: rgb(), rgb-percent, hsl
        color_functions = [
            webcolors.name_to_rgb,
            webcolors.hex_to_rgb,
        ]
        for func in color_functions:
            try:
                return func(color)
            except ValueError:
                pass
        raise ValueError
