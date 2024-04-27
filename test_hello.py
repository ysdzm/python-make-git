from your_script import hello
import sys
from io import StringIO
import contextlib

def test_hello():
    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    # Call hello function
    hello()

    # Get the output
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue().strip()

    # Check if output is correct
    assert output == "hello", "Output is not 'hello'"
