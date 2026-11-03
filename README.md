# log_record_error_separator

Splits an error record into message, exception type, traceback text, and stack frames.

```python
from log_record_error_separator import split_error_record

text = (
    'Traceback (most recent call last):\n'
    '  File "app.py", line 5, in <module>\n'
    '    raise ValueError("bad input")\n'
    'ValueError: bad input'
)
record = split_error_record(text)
print(record.exception_type)  # ValueError
print(record.message)         # bad input
print(record.stack_frames)    # ['File "app.py", line 5, in <module>']
```

## Why this exists

Log aggregation pipelines often treat a traceback as an opaque string. Downstream
consumers that want to group by exception type or inspect the message must re-parse
the text themselves. This library performs that parse once, in a predictable way,
and returns a frozen dataclass with the four fields most consumers need.

The trade-off is strictness: the parser assumes the last non-empty line is the
exception header. If the input is not a traceback at all, the whole string is
returned as the message with empty other fields. That fallback keeps the function
total, but it means callers should not rely on `exception_type` being non-empty
without checking.

## Edge cases

- A bare exception type (e.g. `KeyboardInterrupt`) yields an empty message.
- Colons inside the message are preserved; only the first `": "` splits the header.
- Leading and trailing blank lines are ignored when locating the header.
- Non-string input raises `TypeError`.
