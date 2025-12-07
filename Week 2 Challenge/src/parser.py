"""Parse meeting transcripts from various formats"""
import re
import logging
from typing import List, Dict, Optional
from pathlib import Path
from src.exceptions import (
    FileNotFoundError,
    EmptyTranscriptError,
    MalformedTranscriptError,
    UnsupportedFormatError,
    EncodingError,
    InvalidInputError
)

# Setup logging
logger = logging.getLogger(__name__)


class TranscriptParser:
    """Parse meeting transcripts and normalize format"""
    
    def __init__(self):
        # Zoom format: "00:00:00 John Doe: Message"
        self.zoom_pattern = re.compile(
            r'^(\d{2}:\d{2}:\d{2})\s+(.+?):\s+(.+)$'
        )
        
        # Google Meet format: "10:30 AM John Doe: Message" or "10:30 John Doe: Message"
        self.meet_pattern = re.compile(
            r'^(\d{1,2}:\d{2}(?:\s*[AP]M)?)\s+(.+?):\s+(.+)$',
            re.IGNORECASE
        )
        
        # Plain text with speaker: "John Doe: Message"
        self.plain_pattern = re.compile(
            r'^([A-Z][a-zA-Z\s\.]+?):\s+(.+)$'
        )
        
        # Alternative format: "[00:00:00] John Doe: Message"
        self.bracket_pattern = re.compile(
            r'^\[(\d{2}:\d{2}:\d{2})\]\s+(.+?):\s+(.+)$'
        )
        
        # Microsoft Teams format: "John Doe [10:30 AM]"
        self.teams_pattern = re.compile(
            r'^(.+?)\s+\[(\d{1,2}:\d{2}(?:\s*[AP]M)?)\]$',
            re.IGNORECASE
        )
    
    def parse_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        Parse transcript from file
        
        Args:
            file_path: Path to transcript file
            
        Returns:
            List of message dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            UnsupportedFormatError: If file type is not supported
            EncodingError: If file encoding is not supported
            EmptyTranscriptError: If file is empty
            MalformedTranscriptError: If content cannot be parsed
        """
        # Input validation
        if not file_path:
            logger.error("Empty file path provided")
            raise InvalidInputError("file_path", "Path cannot be empty")
        
        if not isinstance(file_path, (str, Path)):
            logger.error(f"Invalid file path type: {type(file_path)}")
            raise InvalidInputError("file_path", f"Expected string or Path, got {type(file_path)}")
        
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(str(file_path))
            
            # Check if it's a file (not directory)
            if not path.is_file():
                logger.error(f"Path is not a file: {file_path}")
                raise InvalidInputError("file_path", "Path must point to a file, not a directory")
            
            # Check file extension
            if path.suffix.lower() not in ['.txt', '']:
                logger.warning(f"Unsupported file extension: {path.suffix}")
                raise UnsupportedFormatError(path.suffix)
            
            # Try to read file with UTF-8 encoding
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with latin-1 as fallback
                logger.warning("UTF-8 decoding failed, trying latin-1")
                try:
                    with open(path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except UnicodeDecodeError as e:
                    logger.error(f"Encoding error: {e}")
                    raise EncodingError("UTF-8, latin-1")
            
            # Check if file is empty
            if not content or not content.strip():
                logger.error("File is empty")
                raise EmptyTranscriptError()
            
            logger.info(f"Successfully read file: {file_path} ({len(content)} characters)")
            return self.parse(content)
            
        except (FileNotFoundError, UnsupportedFormatError, EncodingError, 
                EmptyTranscriptError, InvalidInputError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading file: {e}", exc_info=True)
            raise MalformedTranscriptError(f"Error reading file: {str(e)}")
    
    def parse(self, content: str) -> List[Dict[str, str]]:
        """
        Parse transcript content and return structured messages
        
        Args:
            content: Raw transcript text
            
        Returns:
            List of dictionaries with keys: 'timestamp', 'speaker', 'text'
            
        Raises:
            EmptyTranscriptError: If content is empty
            MalformedTranscriptError: If no valid messages found
            InvalidInputError: If content is not a string
        """
        # Input validation
        if not isinstance(content, str):
            logger.error(f"Invalid content type: {type(content)}")
            raise InvalidInputError("content", f"Expected string, got {type(content)}")
        
        if not content or not content.strip():
            logger.error("Empty transcript content")
            raise EmptyTranscriptError()
        
        try:
            lines = content.strip().split('\n')
            messages = []
            current_message = None
            valid_lines = 0
            
            logger.debug(f"Parsing {len(lines)} lines")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                valid_lines += 1
                
                # Skip common header/footer patterns
                if self._is_metadata_line(line):
                    logger.debug(f"Skipping metadata line {line_num}: {line[:50]}")
                    continue
                
                # Try to parse as new message
                parsed = self._parse_line(line)
                
                if parsed:
                    # Save previous message if exists
                    if current_message:
                        messages.append(current_message)
                    
                    current_message = parsed
                    logger.debug(f"Parsed message from {parsed['speaker']}")
                else:
                    # Continuation of previous message
                    if current_message:
                        current_message['text'] += ' ' + line
                    else:
                        # No previous message, treat as plain text
                        current_message = {
                            'timestamp': '',
                            'speaker': 'Unknown',
                            'text': line,
                            'line_number': line_num
                        }
            
            # Add last message
            if current_message:
                messages.append(current_message)
            
            # Validate we found messages
            if not messages:
                logger.error(f"No valid messages found in {valid_lines} lines")
                raise MalformedTranscriptError(
                    f"No valid messages found. Processed {valid_lines} lines but couldn't identify speaker/message format"
                )
            
            logger.info(f"Successfully parsed {len(messages)} messages from {valid_lines} lines")
            return self._clean_messages(messages)
            
        except (EmptyTranscriptError, MalformedTranscriptError, InvalidInputError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}", exc_info=True)
            raise MalformedTranscriptError(f"Parsing failed: {str(e)}")
    
    def _parse_line(self, line: str) -> Optional[Dict[str, str]]:
        """
        Try to parse a line with all known formats
        
        Returns:
            Dictionary with timestamp, speaker, text or None if no match
        """
        # Try Zoom format
        match = self.zoom_pattern.match(line)
        if match:
            return {
                'timestamp': match.group(1),
                'speaker': self._clean_speaker_name(match.group(2)),
                'text': match.group(3).strip()
            }
        
        # Try bracket format
        match = self.bracket_pattern.match(line)
        if match:
            return {
                'timestamp': match.group(1),
                'speaker': self._clean_speaker_name(match.group(2)),
                'text': match.group(3).strip()
            }
        
        # Try Google Meet format
        match = self.meet_pattern.match(line)
        if match:
            return {
                'timestamp': match.group(1).strip(),
                'speaker': self._clean_speaker_name(match.group(2)),
                'text': match.group(3).strip()
            }
        
        # Try plain text format (speaker: message)
        match = self.plain_pattern.match(line)
        if match:
            return {
                'timestamp': '',
                'speaker': self._clean_speaker_name(match.group(1)),
                'text': match.group(2).strip()
            }
        
        # Check for Teams format (speaker [time])
        match = self.teams_pattern.match(line)
        if match:
            # This is just the header, next line should be the message
            return None
        
        return None
    
    def _clean_speaker_name(self, name: str) -> str:
        """Clean and normalize speaker names"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common prefixes/suffixes
        name = re.sub(r'\s*\(.*?\)\s*', '', name)  # Remove (you), (host), etc.
        name = re.sub(r'\s*\[.*?\]\s*', '', name)  # Remove [host], etc.
        
        # Capitalize properly
        name = name.strip()
        
        return name if name else 'Unknown'
    
    def _is_metadata_line(self, line: str) -> bool:
        """Check if line is metadata (header/footer) and should be skipped"""
        metadata_patterns = [
            r'^={3,}',  # Separator lines
            r'^-{3,}',
            r'^Meeting\s+ID:',
            r'^Passcode:',
            r'^Recording\s+started',
            r'^Recording\s+ended',
            r'^Transcript\s+(?:started|ended)',
            r'^\d+\s+participants?',
            r'^Zoom\s+Meeting',
            r'^Google\s+Meet',
        ]
        
        return any(re.match(pattern, line, re.IGNORECASE) for pattern in metadata_patterns)
    
    def _clean_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Clean and validate messages"""
        cleaned = []
        
        for msg in messages:
            # Skip very short messages (likely noise)
            if len(msg['text']) < 2:
                continue
            
            # Remove line_number if present (internal use only)
            msg.pop('line_number', None)
            
            # Ensure all required fields exist
            msg.setdefault('timestamp', '')
            msg.setdefault('speaker', 'Unknown')
            msg.setdefault('text', '')
            
            cleaned.append(msg)
        
        return cleaned
    
    def get_speakers(self, messages: List[Dict[str, str]]) -> List[str]:
        """Extract unique speaker names from messages"""
        speakers = set()
        for msg in messages:
            if msg['speaker'] and msg['speaker'] != 'Unknown':
                speakers.add(msg['speaker'])
        return sorted(list(speakers))
    
    def get_format_stats(self, messages: List[Dict[str, str]]) -> Dict[str, int]:
        """Get statistics about the parsed transcript"""
        stats = {
            'total_messages': len(messages),
            'with_timestamps': sum(1 for m in messages if m['timestamp']),
            'without_timestamps': sum(1 for m in messages if not m['timestamp']),
            'unique_speakers': len(self.get_speakers(messages)),
            'unknown_speakers': sum(1 for m in messages if m['speaker'] == 'Unknown')
        }
        return stats
