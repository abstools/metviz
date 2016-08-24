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
    grammar = (L("Pair("), WORD("A-Za-z0-9.\""), L(","), WORD("0-9"), L(")"))

    def value(self):
        """Converts this node to a JSON object
        """
        data = {}
        key = self[1].string.replace("\"", "")
        data[key] = self[3].string
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
        example_string = """list[
Pair(Time(2206), 
    list[Pair(\"gamma.fas.live.200ms\", 30),Pair(\"gamma.fas.live.500ms\", 5)]), 
Pair(Time(1485), 
    list[Pair(\"gamma.fas.live.200ms\", 25)])]"""
        result = parse(example_string)
        print_json(result)
