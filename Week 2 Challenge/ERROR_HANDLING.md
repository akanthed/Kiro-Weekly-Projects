# Error Handling Documentation

## Overview

The Meeting Action Items Extractor includes comprehensive error handling across all modules to ensure robust operation and helpful user feedback.

## Custom Exception Hierarchy

All custom exceptions inherit from `MeetingExtractorError` base class, which includes:
- `message`: Error description
- `suggestion`: Helpful tip for resolving the issue

### Exception Types

#### 1. FileNotFoundError
**Raised when:** Transcript file doesn't exist
**Suggestion:** Check the file path and ensure the file exists
```python
raise FileNotFoundError("/path/to/file.txt")
```

#### 2. EmptyTranscriptError
**Raised when:** Transcript is empty or contains no valid content
**Suggestion:** Ensure the file contains meeting dialogue with speaker names
```python
raise EmptyTranscriptError()
```

#### 3. MalformedTranscriptError
**Raised when:** Transcript format is unrecognized or malformed
**Suggestion:** Shows supported formats (Zoom, Google Meet, Plain text)
```python
raise MalformedTranscriptError("No valid messages found")
```

#### 4. NoActionItemsError
**Raised when:** No action items detected in transcript
**Suggestion:** Lists action keywords to include (will, should, TODO, etc.)
```python
raise NoActionItemsError()
```

#### 5. UnsupportedFormatError
**Raised when:** File format is not supported
**Suggestion:** Only text files (.txt) are supported
```python
raise UnsupportedFormatError(".pdf")
```

#### 6. EncodingError
**Raised when:** File encoding is not supported
**Suggestion:** Ensure file is saved in UTF-8 encoding
```python
raise EncodingError("UTF-8, latin-1")
```

#### 7. InvalidInputError
**Raised when:** Input validation fails
**Suggestion:** Check parameter value and try again
```python
raise InvalidInputError("parameter_name", "reason")
```

#### 8. OutputError
**Raised when:** Output generation or file saving fails
**Suggestion:** Check file permissions and disk space
```python
raise OutputError("Failed to write file")
```

## Error Handling by Module

### parser.py

**Input Validation:**
- File path must be non-empty string or Path object
- File must exist and be a regular file (not directory)
- File extension must be .txt or empty
- Content must be non-empty string

**Error Handling:**
- Tries UTF-8 encoding first, falls back to latin-1
- Skips metadata lines (Recording started, Meeting ID, etc.)
- Handles continuation lines for multi-line messages
- Validates at least one message was parsed

**Logging:**
```python
logger.info(f"Successfully read file: {file_path}")
logger.warning("UTF-8 decoding failed, trying latin-1")
logger.error(f"File not found: {file_path}")
```

### action_detector.py

**Input Validation:**
- transcript_data must be a list
- Each message must be a dictionary
- Messages must have 'text' field

**Error Handling:**
- Skips messages with negative patterns (won't, shouldn't, etc.)
- Continues processing if individual message fails
- Returns empty list if no action items found (doesn't raise exception)
- Handles date parsing failures gracefully

**Logging:**
```python
logger.info(f"Processing {len(transcript_data)} messages")
logger.debug(f"Extracted action item: {task[:50]}...")
logger.warning(f"Error processing message {i}: {e}")
```

### summary_generator.py

**Input Validation:**
- action_items must be a list
- meeting_title must be non-empty string
- content must be non-empty string for saving
- format_type must be 'markdown' or 'json'
- output_path must be non-empty string or Path

**Error Handling:**
- Creates parent directories automatically
- Handles permission errors
- Handles OS errors (disk full, etc.)
- Validates content before saving

**Logging:**
```python
logger.info(f"Generating markdown for {len(action_items)} items")
logger.debug(f"Created directory: {path.parent}")
logger.error(f"Permission denied writing to {output_path}")
```

### main.py (CLI)

**Error Handling Strategy:**
- Catches specific exceptions first
- Provides user-friendly error messages
- Shows suggestions for resolution
- Logs all errors to meeting_extractor.log
- Exits with appropriate exit codes

**Exit Codes:**
- 0: Success or non-fatal warning
- 1: Fatal error

**Example Error Output:**
```
❌ File not found: meeting.txt
💡 Check the file path and ensure the file exists
```

## Batch Processing Error Handling

The batch command continues processing even if individual files fail:

```python
try:
    # Process file
    ...
except (FileNotFoundError, EmptyTranscriptError, MalformedTranscriptError) as e:
    click.echo(f"⚠️  {file.name}: {e.message}", err=True)
    error_count += 1
    # Continue with next file
```

**Summary Report:**
```
✅ Batch processing complete!
   Success: 8 | Errors: 2
   Output directory: summaries/
💡 Check meeting_extractor.log for detailed error information
```

## Logging Configuration

All modules use Python's logging framework:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meeting_extractor.log'),
        logging.StreamHandler()
    ]
)
```

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages (non-fatal issues)
- ERROR: Error messages (fatal issues)

## Testing Error Handling

The `test_parser.py` includes error handling tests:

```python
def test_error_handling():
    """Test error handling with invalid inputs"""
    
    # Test empty content
    try:
        parser.parse("")
    except EmptyTranscriptError as e:
        print(f"✅ Correctly raised error: {e.message}")
    
    # Test file not found
    try:
        parser.parse_file("nonexistent.txt")
    except FileNotFoundError as e:
        print(f"✅ Correctly raised error: {e.message}")
```

## Best Practices

1. **Always validate input** before processing
2. **Use specific exceptions** instead of generic Exception
3. **Provide helpful suggestions** in error messages
4. **Log errors** for debugging
5. **Don't crash** - handle errors gracefully
6. **Continue processing** when possible (batch mode)
7. **Show progress** to users during long operations
8. **Use appropriate exit codes** for CLI

## User-Friendly Error Messages

All error messages follow this pattern:

```
❌ [Error Type]: [Clear description]
💡 Suggestion: [How to fix it]
```

Examples:
```
❌ File not found: meeting.txt
💡 Check the file path and ensure the file exists

❌ Transcript is empty or contains no valid content
💡 Ensure the file contains meeting dialogue with speaker names

❌ No action items detected in transcript
💡 Action items should contain keywords like:
  • 'will', 'should', 'need to', 'must'
  • 'action item', 'TODO', 'task'
  • 'follow up', 'deadline', 'by [date]'
```

## Recovery Strategies

### File Not Found
1. Check file path spelling
2. Use absolute path instead of relative
3. Verify file exists with `ls` or `dir`

### Empty Transcript
1. Open file in text editor to verify content
2. Check file encoding (should be UTF-8)
3. Ensure file isn't corrupted

### Malformed Transcript
1. Review supported formats in documentation
2. Add speaker names if missing
3. Use consistent format throughout file

### No Action Items
1. Add action keywords (will, should, must, etc.)
2. Include deadlines (by Friday, next week, etc.)
3. Assign tasks explicitly (John will..., @mention)

### Encoding Error
1. Save file as UTF-8 in text editor
2. Use Notepad++ or VS Code to convert encoding
3. Remove special characters if necessary

## Monitoring and Debugging

**Check logs:**
```bash
tail -f meeting_extractor.log
```

**Enable debug logging:**
```python
logging.basicConfig(level=logging.DEBUG)
```

**Validate transcript before processing:**
```bash
python main.py validate meeting.txt
```

This shows format statistics and sample messages without full processing.
