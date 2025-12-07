"""Detect and extract action items from meeting transcripts"""
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from src.exceptions import (
    NoActionItemsError,
    InvalidInputError,
    MalformedTranscriptError
)

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class ActionItem:
    """Represents a single action item from a meeting"""
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "medium"
    context: str = ""
    speaker: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class ActionDetector:
    """Detect action items from meeting transcripts"""
    
    def __init__(self):
        # Action keywords (ordered by strength)
        self.action_keywords = [
            r'\baction\s+item\b',
            r'\bTODO\b',
            r'\bto-do\b',
            r'\btask\b',
            r'\bfollow\s*up\b',
            r'\bfollow-up\b',
            r'\bneed(?:s)?\s+to\b',
            r'\bhas\s+to\b',
            r'\bhave\s+to\b',
            r'\bmust\b',
            r'\bshould\b',
            r'\bwill\b',
            r'\bgonna\b',
            r'\bgoing\s+to\b',
            r'\bresponsible\s+for\b',
            r'\btake\s+care\s+of\b',
            r'\bwork\s+on\b',
            r'\bhandle\b',
        ]
        
        # Assignment patterns
        self.assignment_patterns = [
            r'@(\w+)\s+(?:will|should|needs?\s+to|must)',
            r'(\w+)\s+will\s+',
            r'(\w+)\s+should\s+',
            r'(\w+)\s+needs?\s+to\s+',
            r'(\w+)\s+must\s+',
            r'(\w+)\s+is\s+(?:going\s+to|gonna)\s+',
            r'assign(?:ed)?\s+to\s+(\w+)',
            r'(\w+)\s+to\s+(?:handle|work\s+on|take\s+care\s+of)',
            r'I\s+will\s+',  # Speaker is assignee
            r"I'll\s+",
        ]
        
        # Deadline patterns
        self.deadline_patterns = [
            (r'\bby\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', 'weekday'),
            (r'\bby\s+end\s+of\s+(week|month|quarter|year)', 'period'),
            (r'\bby\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)', 'date'),
            (r'\bby\s+(tomorrow|today|tonight)', 'relative'),
            (r'\bby\s+(next\s+\w+)', 'relative'),
            (r'\bby\s+(this\s+\w+)', 'relative'),
            (r'\bin\s+(\d+)\s+(day|week|month)s?', 'duration'),
            (r'\bdue\s+(on\s+)?(\w+\s+\d{1,2})', 'date'),
            (r'\bdeadline:?\s+(\w+\s+\d{1,2})', 'date'),
            (r'\buntil\s+(\w+\s+\d{1,2})', 'date'),
            (r'\bbefore\s+(\w+\s+\d{1,2})', 'date'),
            (r'\bEOD\b', 'eod'),  # End of day
            (r'\bEOW\b', 'eow'),  # End of week
            (r'\bASAP\b', 'asap'),
        ]
        
        # Priority keywords
        self.priority_keywords = {
            'high': [
                r'\burgent\b',
                r'\bASAP\b',
                r'\bcritical\b',
                r'\bimmediate(?:ly)?\b',
                r'\bhigh\s+priority\b',
                r'\btop\s+priority\b',
                r'\bemergency\b',
                r'\bblocking\b',
            ],
            'low': [
                r'\bnice\s+to\s+have\b',
                r'\bwhen\s+(?:you\s+)?(?:have\s+)?time\b',
                r'\bif\s+possible\b',
                r'\boptional\b',
                r'\blow\s+priority\b',
                r'\beventually\b',
            ]
        }
        
        # Negative patterns (exclude these)
        self.negative_patterns = [
            r'\bwon\'t\b',
            r'\bwill\s+not\b',
            r'\bshould\s+not\b',
            r'\bshouldn\'t\b',
            r'\bdon\'t\s+need\b',
            r'\bno\s+need\s+to\b',
            r'\bmaybe\b',
            r'\bmight\b',
            r'\bcould\b',
        ]
    
    def extract_action_items(self, transcript_data: List[Dict]) -> List[ActionItem]:
        """
        Extract action items from parsed transcript
        
        Args:
            transcript_data: List of message dictionaries from parser
            
        Returns:
            List of ActionItem objects
            
        Raises:
            InvalidInputError: If input is invalid
            NoActionItemsError: If no action items found (optional, can return empty list)
        """
        # Input validation
        if not isinstance(transcript_data, list):
            logger.error(f"Invalid transcript_data type: {type(transcript_data)}")
            raise InvalidInputError("transcript_data", f"Expected list, got {type(transcript_data)}")
        
        if not transcript_data:
            logger.warning("Empty transcript data provided")
            return []
        
        # Validate each message has required fields
        for i, message in enumerate(transcript_data):
            if not isinstance(message, dict):
                logger.error(f"Message {i} is not a dictionary")
                raise InvalidInputError("transcript_data", f"Message {i} must be a dictionary")
            
            if 'text' not in message:
                logger.warning(f"Message {i} missing 'text' field, skipping")
                continue
        
        action_items = []
        
        try:
            logger.info(f"Processing {len(transcript_data)} messages for action items")
            
            for i, message in enumerate(transcript_data):
                try:
                    text = message.get('text', '')
                    speaker = message.get('speaker', 'Unknown')
                    timestamp = message.get('timestamp', '')
                    
                    # Skip empty messages
                    if not text or not text.strip():
                        continue
                    
                    # Check if message contains action indicators
                    if not self._is_action_item(text):
                        continue
                    
                    # Skip if contains negative patterns
                    if self._has_negative_pattern(text):
                        logger.debug(f"Skipping message with negative pattern: {text[:50]}")
                        continue
                    
                    # Extract components
                    task = self._extract_task(text)
                    assignee = self._extract_assignee(text, speaker)
                    deadline = self._extract_deadline(text)
                    priority = self._detect_priority(text)
                    context = self._get_context(transcript_data, i)
                    
                    action_item = ActionItem(
                        task=task,
                        assignee=assignee,
                        deadline=deadline,
                        priority=priority,
                        context=context,
                        speaker=speaker,
                        timestamp=timestamp
                    )
                    
                    action_items.append(action_item)
                    logger.debug(f"Extracted action item: {task[:50]}... (assignee: {assignee})")
                    
                except Exception as e:
                    logger.warning(f"Error processing message {i}: {e}")
                    # Continue processing other messages
                    continue
            
            logger.info(f"Extracted {len(action_items)} action items")
            return action_items
            
        except Exception as e:
            logger.error(f"Unexpected error during action item extraction: {e}", exc_info=True)
            raise MalformedTranscriptError(f"Failed to extract action items: {str(e)}")
    
    def _is_action_item(self, text: str) -> bool:
        """Check if text contains action item indicators"""
        text_lower = text.lower()
        
        # Check for action keywords
        for pattern in self.action_keywords:
            if re.search(pattern, text_lower):
                return True
        
        # Check for assignment patterns
        for pattern in self.assignment_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _has_negative_pattern(self, text: str) -> bool:
        """Check if text contains negative patterns that negate action"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.negative_patterns)
    
    def _extract_task(self, text: str) -> str:
        """Extract the task description"""
        # Remove common prefixes
        task = text
        
        # Remove action item prefix
        task = re.sub(r'^(?:action\s+item:?|TODO:?|task:?)\s*', '', task, flags=re.IGNORECASE)
        
        # Clean up
        task = task.strip()
        
        # Limit length
        if len(task) > 200:
            task = task[:197] + '...'
        
        return task
    
    def _extract_assignee(self, text: str, speaker: str) -> Optional[str]:
        """Extract assignee from text"""
        # Check for @mentions
        mention_match = re.search(r'@(\w+)', text)
        if mention_match:
            return mention_match.group(1)
        
        # Check for "I will" pattern first - speaker is assignee
        if re.search(r'\bI\s+(?:will|should|need\s+to|must|\'ll|can)\b', text, re.IGNORECASE):
            return speaker
        
        # Check for explicit assignment with proper names
        # Pattern: "Name will/should/needs to/must"
        name_action_match = re.search(
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:will|should|needs?\s+to|must|can)\b',
            text
        )
        if name_action_match:
            name = name_action_match.group(1)
            # Verify it's not a common word
            if name.lower() not in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'sure', 'got', 'yes', 'okay', 'right', 'also', 'one', 'will', 'sounds', 'that', 'good']:
                return name
        
        # Check for "assigned to Name" pattern
        assigned_match = re.search(r'assign(?:ed)?\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
        if assigned_match:
            return assigned_match.group(1)
        
        # Default to speaker if strong action verb present and no other assignee found
        if re.search(r'\b(?:will|must)\b', text, re.IGNORECASE):
            return speaker
        
        return None
    
    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract and normalize deadline from text"""
        for pattern, deadline_type in self.deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if deadline_type == 'weekday':
                        return self._parse_weekday(match.group(1))
                    elif deadline_type == 'period':
                        return self._parse_period(match.group(1))
                    elif deadline_type == 'date':
                        return self._parse_date(match.group(1))
                    elif deadline_type == 'relative':
                        return self._parse_relative(match.group(1))
                    elif deadline_type == 'duration':
                        return self._parse_duration(int(match.group(1)), match.group(2))
                    elif deadline_type == 'eod':
                        return datetime.now().strftime('%Y-%m-%d') + ' EOD'
                    elif deadline_type == 'eow':
                        return self._parse_weekday('Friday')
                    elif deadline_type == 'asap':
                        return 'ASAP'
                except:
                    # If parsing fails, return the matched text
                    return match.group(0)
        
        return None
    
    def _parse_weekday(self, weekday: str) -> str:
        """Parse weekday to next occurrence date"""
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        target_day = weekdays.index(weekday.lower())
        today = datetime.now()
        current_day = today.weekday()
        
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    def _parse_period(self, period: str) -> str:
        """Parse end of period"""
        today = datetime.now()
        period_lower = period.lower()
        
        if period_lower == 'week':
            # Next Friday
            return self._parse_weekday('Friday')
        elif period_lower == 'month':
            # Last day of current month
            next_month = today.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            return last_day.strftime('%Y-%m-%d')
        elif period_lower == 'quarter':
            # End of current quarter
            quarter = (today.month - 1) // 3
            last_month = (quarter + 1) * 3
            last_day = datetime(today.year, last_month, 1) + timedelta(days=32)
            last_day = last_day.replace(day=1) - timedelta(days=1)
            return last_day.strftime('%Y-%m-%d')
        elif period_lower == 'year':
            return f"{today.year}-12-31"
        
        return f"End of {period}"
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            parsed = date_parser.parse(date_str, fuzzy=True)
            # If year not specified and date is in past, assume next year
            if parsed.year == datetime.now().year and parsed < datetime.now():
                parsed = parsed.replace(year=parsed.year + 1)
            return parsed.strftime('%Y-%m-%d')
        except:
            return date_str
    
    def _parse_relative(self, relative: str) -> str:
        """Parse relative date (tomorrow, next week, etc.)"""
        relative_lower = relative.lower()
        today = datetime.now()
        
        if relative_lower == 'today':
            return today.strftime('%Y-%m-%d')
        elif relative_lower == 'tomorrow':
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        elif relative_lower == 'tonight':
            return today.strftime('%Y-%m-%d') + ' EOD'
        elif relative_lower.startswith('next'):
            # next week, next monday, etc.
            return self._parse_date(relative)
        elif relative_lower.startswith('this'):
            # this week, this friday, etc.
            return self._parse_date(relative)
        
        return relative
    
    def _parse_duration(self, amount: int, unit: str) -> str:
        """Parse duration (in X days/weeks/months)"""
        today = datetime.now()
        
        if unit.lower().startswith('day'):
            target = today + timedelta(days=amount)
        elif unit.lower().startswith('week'):
            target = today + timedelta(weeks=amount)
        elif unit.lower().startswith('month'):
            target = today + timedelta(days=amount * 30)
        else:
            return f"in {amount} {unit}s"
        
        return target.strftime('%Y-%m-%d')
    
    def _detect_priority(self, text: str) -> str:
        """Detect priority level from text"""
        text_lower = text.lower()
        
        # Check high priority keywords
        for pattern in self.priority_keywords['high']:
            if re.search(pattern, text_lower):
                return 'high'
        
        # Check low priority keywords
        for pattern in self.priority_keywords['low']:
            if re.search(pattern, text_lower):
                return 'low'
        
        # Check for deadline-based priority
        if re.search(r'\b(?:ASAP|today|tonight|EOD)\b', text, re.IGNORECASE):
            return 'high'
        
        return 'medium'
    
    def _get_context(self, transcript_data: List[Dict], current_index: int, window: int = 1) -> str:
        """Get surrounding context for action item"""
        start = max(0, current_index - window)
        end = min(len(transcript_data), current_index + window + 1)
        
        context_messages = []
        for i in range(start, end):
            if i != current_index:
                msg = transcript_data[i]
                context_messages.append(f"{msg.get('speaker', 'Unknown')}: {msg.get('text', '')[:100]}")
        
        return " | ".join(context_messages) if context_messages else ""
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize names"""
        # Capitalize first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())
        return name.strip()
    
    def filter_by_assignee(self, action_items: List[ActionItem], assignee: str) -> List[ActionItem]:
        """Filter action items by assignee"""
        return [item for item in action_items if item.assignee and item.assignee.lower() == assignee.lower()]
    
    def filter_by_priority(self, action_items: List[ActionItem], priority: str) -> List[ActionItem]:
        """Filter action items by priority"""
        return [item for item in action_items if item.priority == priority.lower()]
    
    def get_statistics(self, action_items: List[ActionItem]) -> Dict:
        """Get statistics about action items"""
        total = len(action_items)
        
        # Count by assignee
        by_assignee = {}
        for item in action_items:
            assignee = item.assignee or 'Unassigned'
            by_assignee[assignee] = by_assignee.get(assignee, 0) + 1
        
        # Count by priority
        by_priority = {
            'high': len([i for i in action_items if i.priority == 'high']),
            'medium': len([i for i in action_items if i.priority == 'medium']),
            'low': len([i for i in action_items if i.priority == 'low']),
        }
        
        # Count with/without deadlines
        with_deadline = len([i for i in action_items if i.deadline])
        without_deadline = total - with_deadline
        
        return {
            'total': total,
            'by_assignee': by_assignee,
            'by_priority': by_priority,
            'with_deadline': with_deadline,
            'without_deadline': without_deadline,
        }
