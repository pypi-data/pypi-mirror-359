# exitcodes.py

# Define standard exit codes
SUCCESS = 0
UNHANDLED_ERROR = 1
ABRUPT_TERMINATION = 5
UNHANDLEABLE_ERROR = 10

# Map codes to their messages
_exit_messages = {
    SUCCESS: "Success",
    UNHANDLED_ERROR: "Unhandled error",
    ABRUPT_TERMINATION: "Abrupt termination (program ended without proper exit)",
    UNHANDLEABLE_ERROR: "Handled but unresolvable error",
}

def message_for(code: int) -> str:
    """
    Return the message corresponding to the exit code.
    Raises ValueError if code is not defined.
    """
    if code not in _exit_messages:
        raise ValueError(f"Invalid exit code: {code}")
    return _exit_messages[code]

def format_exit_message(code: int) -> str:
    """
    Return a formatted exit message for the code.
    Example: "Exit code 1: Unhandled error"
    Raises ValueError if code is invalid.
    """
    msg = message_for(code)
    return f"Exit code {code}: {msg}"

if __name__ == "__main__":
    # Demo / test
    for code in [SUCCESS, UNHANDLED_ERROR, ABRUPT_TERMINATION, UNHANDLEABLE_ERROR, 999]:
        try:
            print(format_exit_message(code))
        except ValueError as e:
            print(f"Caught error for code {code}: {e}")
