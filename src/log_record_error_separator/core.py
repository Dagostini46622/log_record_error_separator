import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ErrorRecord:
    message: str
    exception_type: str
    traceback_text: str
    stack_frames: List[str]


def split_error_record(text: str) -> ErrorRecord:
    """
    Split a single error record string into structured fields.

    The input is expected to be in the format produced by Python's
    ``traceback.format_exception`` (or similar), i.e. one or more
    traceback lines followed by a final exception line of the form
    ``ExceptionType: message``.

    If the input does not match this shape, the entire input is treated
    as the message, with empty exception type, traceback, and frames.
    This fallback is deliberate: callers who pass arbitrary text still
    get a usable record rather than an exception.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    lines = text.splitlines()
    if not lines:
        return ErrorRecord(message="", exception_type="", traceback_text="", stack_frames=[])

    # Find the last line that looks like an exception header: "Type: message"
    # or just "Type". We search from the end because the exception line is
    # always last in a formatted traceback.
    exception_line_index = None
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if not line:
            continue
        # Exception headers have no leading whitespace (traceback lines do).
        if line[0].isspace():
            continue
        # A valid header contains a colon followed by a space, or is a bare
        # exception type name (no spaces, no colon).
        if ": " in line:
            exception_line_index = i
            break
        if ":" not in line and " " not in line:
            exception_line_index = i
            break

    if exception_line_index is None:
        return ErrorRecord(
            message=text,
            exception_type="",
            traceback_text="",
            stack_frames=[],
        )

    exception_line = lines[exception_line_index].strip()
    if ": " in exception_line:
        exception_type, message = exception_line.split(": ", 1)
    else:
        exception_type = exception_line
        message = ""

    traceback_lines = lines[:exception_line_index]
    traceback_text = "\n".join(traceback_lines)

    # Stack frames are the lines that start with "  File \"".
    stack_frames = [
        line.strip()
        for line in traceback_lines
        if line.lstrip().startswith("File \"")
    ]

    return ErrorRecord(
        message=message,
        exception_type=exception_type,
        traceback_text=traceback_text,
        stack_frames=stack_frames,
    )
