"""
A Grammar spec on how to parse and interpret
ABS JSON strings.
"""

import json
import logging
import sys
from modgrammar import *

# To make white spaces loose in the grammar
grammar_whitespace_mode = 'optional'

class KeyValuePairGrammar (Grammar):
    """A Grammar to model a key-value Pair as
        `Pair(Key, Value)`
    """
    grammar = (L("Pair("), WORD("A-Za-z0-9.\""), L(","), WORD("0-9/"), L(")"))

    def value(self):
        """Converts this node to a JSON object
        """
        data = {}
        key = self[1].string.replace("\"", "")
        s = self[3].string
        value = 0.0
        if '/' in s:
            a, b = s.split('/')
            value = float(a) / float(b)
        else:
            value = float(s)
        data[key] = value
        return data

class TimePairGrammar (Grammar):
    """A Grammar to model a list "timed" pairs
        `Pair(Time(N), list[KeyValuePairGrammar])`
    """
    grammar = (L("Pair(Time("), WORD("0-9"), L(")"), L(","), L("list["), LIST_OF(KeyValuePairGrammar, sep=",", min=0), L("])"))

    def value(self):
        """Converts this node to a JSON object
        """
        data = {}
        values = []
        for v in self[5]:
            if v.string == ",":
                continue
            values.append(v.value())
        data[self[1].string] = values
        return data

class MetricGrammar (Grammar):
    """A Grammar to model the top node
        `list[TimePairGrammar]`
    """
    grammar = (L("list["), LIST_OF(TimePairGrammar, sep=",", min=0), L("]"))

    def value(self):
        """Converts this node to a JSON array
        """
        values = []
        for v in self[1]:
            if v.string == ",":
                continue
            values.append(v.value())
        return values

def parse(text):
    """Helper function to create a Grammar parser
    and perform parsing. If the parsing fails, the
    original text is returned.

    text -- the text to be parsed to JSON
    """
    if "list[" in text:
        parser = MetricGrammar.parser()
        try:
            trimmed_text = text[1:-1] if text.startswith("\"") else text
            return parser.parse_text(trimmed_text).value()
        except ParseError as ex:
            logging.error("Invalid text for parsing: %s", ex.message)
            return text
    else:
        logging.warn("Provided text to parse is not compatible: %s", text)
        return text

def print_json(text):
    """Prints a JSON object with indentation
    and sorted keys.
    """
    logging.info("%s", json.dumps(text, indent=2, sort_keys=True))

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    if len(sys.argv) >= 2:
        result = parse(sys.argv[1])
        print_json(result)
    else:
        example_string = """list[Pair(Time(14489), list[Pair(\"slow\", 19/28)]), Pair(Time(14414), list[Pair(\"slow\", 38/55)]), Pair(Time(14337), list[Pair(\"slow\", 37/54)]), Pair(Time(14280), list[Pair(\"slow\", 36/53)]), Pair(Time(14260), list[Pair(\"slow\", 9/13)]), Pair(Time(14242), list[Pair(\"slow\", 12/17)]), Pair(Time(14228), list[Pair(\"slow\", 18/25)]), Pair(Time(14153), list[Pair(\"slow\", 5/7)]), Pair(Time(14076), list[Pair(\"slow\", 35/48)]), Pair(Time(14039), list[Pair(\"slow\", 34/47)]), Pair(Time(13977), list[Pair(\"slow\", 33/46)]), Pair(Time(13916), list[Pair(\"slow\", 11/15)]), Pair(Time(13826), list[Pair(\"slow\", 3/4)]), Pair(Time(13777), list[Pair(\"slow\", 32/43)]), Pair(Time(13738), list[Pair(\"slow\", 16/21)]), Pair(Time(13673), list[Pair(\"slow\", 31/41)]), Pair(Time(13604), list[Pair(\"slow\", 31/40)]), Pair(Time(13562), list[Pair(\"slow\", 10/13)]), Pair(Time(13498), list[Pair(\"slow\", 29/38)]), Pair(Time(13461), list[Pair(\"slow\", 28/37)]), Pair(Time(13455), list[Pair(\"slow\", 3/4)]), Pair(Time(13350), list[Pair(\"slow\", 26/35)]), Pair(Time(13277), list[Pair(\"slow\", 13/17)]), Pair(Time(13100), list[Pair(\"slow\", 26/33)]), Pair(Time(13007), list[Pair(\"slow\", 25/32)]), Pair(Time(12648), list[Pair(\"slow\", 24/31)]), Pair(Time(12370), list[Pair(\"slow\", 23/30)]), Pair(Time(12162), list[Pair(\"slow\", 23/29)]), Pair(Time(11967), list[Pair(\"slow\", 11/14)]), Pair(Time(11710), list[Pair(\"slow\", 7/9)]), Pair(Time(11319), list[Pair(\"slow\", 21/26)]), Pair(Time(10597), list[Pair(\"slow\", 21/25)]), Pair(Time(10422), list[Pair(\"slow\", 5/6)]), Pair(Time(10403), list[Pair(\"slow\", 20/23)]), Pair(Time(10382), list[Pair(\"slow\", 10/11)]), Pair(Time(10213), list[Pair(\"slow\", 19/21)]), Pair(Time(10002), list[Pair(\"slow\", 9/10)]), Pair(Time(9864), list[Pair(\"slow\", 17/19)]), Pair(Time(9659), list[Pair(\"slow\", 8/9)]), Pair(Time(8895), list[Pair(\"slow\", 16/17)]), Pair(Time(8729), list[Pair(\"slow\", 15/16)]), Pair(Time(8663), list[Pair(\"slow\", 14/15)]), Pair(Time(8618), list[Pair(\"slow\", 13/14)]), Pair(Time(8342), list[Pair(\"slow\", 12/13)]), Pair(Time(8083), list[Pair(\"slow\", 1)]), Pair(Time(7851), list[Pair(\"slow\", 1)]), Pair(Time(7777), list[Pair(\"slow\", 1)]), Pair(Time(7520), list[Pair(\"slow\", 1)]), Pair(Time(7340), list[Pair(\"slow\", 1)]), Pair(Time(6966), list[Pair(\"slow\", 1)]), Pair(Time(6743), list[Pair(\"slow\", 1)]), Pair(Time(6582), list[Pair(\"slow\", 1)]), Pair(Time(6338), list[Pair(\"slow\", 1)]), Pair(Time(6183), list[Pair(\"slow\", 1)]), Pair(Time(6061), list[Pair(\"slow\", 1)]), Pair(Time(6048), list[Pair(\"slow\", 1)])]"""
        result = parse(example_string)
        print_json(result)
