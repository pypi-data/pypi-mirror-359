"""
Custom exceptions for the XenTokeniser package.
"""

class TokenizerError(Exception):
    """Base exception for all tokenizer-related errors."""
    pass


class TokenizerWarning(Warning):
    """Base warning for tokenizer-related warnings."""
    pass


class TokenizerInitializationError(TokenizerError):
    """Raised when tokenizer initialization fails."""
    pass


class TokenizerSerializationError(TokenizerError):
    """Raised when tokenizer serialization/deserialization fails."""
    pass


class TokenizerTypeError(TokenizerError, TypeError):
    """Raised when an incorrect type is passed to a tokenizer method."""
    pass


class TokenizerValueError(TokenizerError, ValueError):
    """Raised when an invalid value is passed to a tokenizer method."""
    pass


class TokenizerFileError(TokenizerError, IOError):
    """Raised when there's an error reading/writing tokenizer files."""
    pass


class TokenizerRuntimeError(TokenizerError, RuntimeError):
    """Raised when a runtime error occurs during tokenization."""
    pass
