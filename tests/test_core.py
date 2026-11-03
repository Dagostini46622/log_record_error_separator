import unittest

from log_record_error_separator import ErrorRecord, split_error_record


class TestSplitErrorRecord(unittest.TestCase):
    def test_typical_traceback(self):
        text = (
            'Traceback (most recent call last):\n'
            '  File "example.py", line 10, in <module>\n'
            '    raise ValueError("bad value")\n'
            'ValueError: bad value'
        )
        record = split_error_record(text)
        self.assertEqual(record.exception_type, "ValueError")
        self.assertEqual(record.message, "bad value")
        self.assertEqual(
            record.traceback_text,
            'Traceback (most recent call last):\n'
            '  File "example.py", line 10, in <module>\n'
            '    raise ValueError("bad value")'
        )
        self.assertEqual(
            record.stack_frames,
            ['File "example.py", line 10, in <module>']
        )

    def test_bare_exception_type(self):
        text = "KeyboardInterrupt"
        record = split_error_record(text)
        self.assertEqual(record.exception_type, "KeyboardInterrupt")
        self.assertEqual(record.message, "")
        self.assertEqual(record.traceback_text, "")
        self.assertEqual(record.stack_frames, [])

    def test_empty_string(self):
        record = split_error_record("")
        self.assertEqual(record, ErrorRecord("", "", "", []))

    def test_no_exception_header(self):
        text = "Something went wrong"
        record = split_error_record(text)
        self.assertEqual(record.message, "Something went wrong")
        self.assertEqual(record.exception_type, "")
        self.assertEqual(record.traceback_text, "")
        self.assertEqual(record.stack_frames, [])

    def test_exception_with_colon_in_message(self):
        text = "ValueError: bad: value"
        record = split_error_record(text)
        self.assertEqual(record.exception_type, "ValueError")
        self.assertEqual(record.message, "bad: value")

    def test_multiple_stack_frames(self):
        text = (
            'Traceback (most recent call last):\n'
            '  File "a.py", line 1, in <module>\n'
            '  File "b.py", line 2, in foo\n'
            'TypeError: oops'
        )
        record = split_error_record(text)
        self.assertEqual(record.exception_type, "TypeError")
        self.assertEqual(record.message, "oops")
        self.assertEqual(
            record.stack_frames,
            ['File "a.py", line 1, in <module>', 'File "b.py", line 2, in foo']
        )

    def test_leading_and_trailing_whitespace(self):
        text = "  \nValueError: bad\n  "
        record = split_error_record(text)
        self.assertEqual(record.exception_type, "ValueError")
        self.assertEqual(record.message, "bad")

    def test_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            split_error_record(123)


if __name__ == "__main__":
    unittest.main()
