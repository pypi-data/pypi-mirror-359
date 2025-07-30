import unittest
from tidyout.main import extract_key_value_blocks, parse_colon_separated_content

class TestTidyoutMain(unittest.TestCase):
    def test_extract_key_value_blocks_simple(self):
        raw = "content='Hello world' response_metadata={\"foo\": 1}"
        result = extract_key_value_blocks(raw)
        self.assertEqual(result['content'], 'Hello world')
        self.assertEqual(result['response_metadata'], {"foo": 1})

    def test_parse_colon_separated_content(self):
        content = "foo: bar\nbaz: qux"
        result = parse_colon_separated_content(content)
        self.assertEqual(result, {"foo": "bar", "baz": "qux"})

    def test_extract_and_parse_content(self):
        raw = "content='foo: bar\\nbaz: qux'"
        result = extract_key_value_blocks(raw)
        parsed = parse_colon_separated_content(result['content'])
        self.assertEqual(parsed, {"foo": "bar", "baz": "qux"})

    def test_non_string_value(self):
        raw = "score=42"
        result = extract_key_value_blocks(raw)
        self.assertEqual(result['score'], 42)

if __name__ == "__main__":
    unittest.main()
