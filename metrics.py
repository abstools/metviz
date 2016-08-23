
import logging
from modgrammar import *

example_string = """list[
    Pair(Time(2206), 
        list[Pair(\"gamma.fas.live.200ms\", 30),Pair(\"gamma.fas.live.500ms\", 5)]), 
    Pair(Time(1485), 
        list[Pair(\"gamma.fas.live.200ms\", 25)])]"""

grammar_whitespace_mode = 'optional'

class KeyValuePairGrammar (Grammar):
    grammar = (L("Pair("), WORD("A-Za-z0-9.\""), L(","), WORD("0-9"), L(")"))

    def value(self):
        data = {}
        key = self[1].string.replace("\"", "")
        data[key] = self[3].string
        return data

class TimePairGrammar (Grammar):
    grammar = (L("Pair(Time("), WORD("0-9"), L(")"), L(","), L("list["), LIST_OF(KeyValuePairGrammar, sep=",", min=0), L("])"))

    def value(self):
        data = {}
        values = []
        for v in self[5]:
            if v.string == ",":
                continue
            values.append(v.value())
        data[self[1].string] = values
        return data

class MetricGrammar (Grammar):
    grammar = (L("list["), LIST_OF(TimePairGrammar, sep=",", min=0), L("]"))

    def value(self):
        values = []
        for v in self[1]:
            if v.string == ",":
                continue
            values.append(v.value())
        return values