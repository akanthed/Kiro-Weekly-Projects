"""Custom exceptions for Meeting Action Items Extractor"""


class MeetingExtractorError(Exception):
    """Base exception for all meeting extractor errors"""
    
    def __init__(self, message: str, suggestion: str = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def __str__(self):
        if self.suggestion:
            return f"{self.message}\n💡 Suggestion: {self.suggestion}"
        return self.message


class FileNotFoundError(MeetingExtractorError):
    """Raised when transcript file is not found"""
    
    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"
        suggestion = "Check the file path and ensure the file exists"
        super().__init__(message, suggestion)


class EmptyTranscriptError(MeetingExtractorError):
    """Raised when transcript is empty or contains no valid content"""
    
    def __init__(self):
        message = "Transcript is empty or contains no valid content"
        suggestion = "Ensure the file contains meeting dialogue with speaker names"
        super().__init__(message, suggestion)


class MalformedTranscriptError(MeetingExtractorError):
    """Raised when transcript format is malformed"""
    
    def __init__(self, details: str = None):
        message = "Transcript format is malformed or unrecognized"
        if details:
            message += f": {details}"
        suggestion = (
            "Supported formats:\n"
            "  • Zoom: '00:00:00 Name: Message'\n"
            "  • Google Meet: '10:30 AM Name: Message'\n"
            "  • Plain text: 'Name: Message'"
        )
        super().__init__(message, suggestion)


class NoActionItemsError(MeetingExtractorError):
    """Raised when no action items are detected"""
    
    def __init__(self):
        message = "No action items detected in transcript"
        suggestion = (
            "Action items should contain keywords like:\n"
            "  • 'will', 'should', 'need to', 'must'\n"
            "  • 'action item', 'TODO', 'task'\n"
            "  • 'follow up', 'deadline', 'by [date]'"
        )
        super().__init__(message, suggestion)


class UnsupportedFormatError(MeetingExtractorError):
    """Raised when file format is not supported"""
    
    def __init__(self, file_type: str):
        message = f"Unsupported file format: {file_type}"
        suggestion = "Only text files (.txt) are supported"
        super().__init__(message, suggestion)


class InvalidInputError(MeetingExtractorError):
    """Raised when input validation fails"""
    
    def __init__(self, parameter: str, reason: str):
        message = f"Invalid input for '{parameter}': {reason}"
        suggestion = "Check the parameter value and try again"
        super().__init__(message, suggestion)


class EncodingError(MeetingExtractorError):
    """Raised when file encoding is not supported"""
    
    def __init__(self, encoding: str = None):
        message = "Unable to read file due to encoding issues"
        if encoding:
            message += f" (tried: {encoding})"
        suggestion = "Ensure the file is saved in UTF-8 encoding"
        super().__init__(message, suggestion)


class OutputError(MeetingExtractorError):
    """Raised when output generation or saving fails"""
    
    def __init__(self, details: str):
        message = f"Failed to generate or save output: {details}"
        suggestion = "Check file permissions and disk space"
        super().__init__(message, suggestion)


# Legacy alias for backward compatibility
TranscriptParseError = MeetingExtractorError
