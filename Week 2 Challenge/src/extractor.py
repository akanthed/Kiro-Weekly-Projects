"""Extract action items from parsed transcripts"""
import re
from typing import List, Dict, Optional
from dateutil import parser as date_parser


class ActionItemExtractor:
    """Extract action items, assignees, and deadlines"""
    
    def __init__(self):
        # Action item indicators
        self.action_patterns = [
            r'\b(will|should|need to|must|have to|going to|gonna)\b',
            r'\b(action item|todo|task|follow up|follow-up)\b',
            r'\b(assign|assigned to|owner)\b',
        ]
        
        # Deadline patterns
        self.deadline_patterns = [
            r'\b(by|before|due|deadline|until)\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)',
            r'\b(by|before|due|deadline|until)\s+(next\s+\w+|this\s+\w+|tomorrow|today)',
            r'\b(in\s+\d+\s+(?:day|week|month)s?)\b',
        ]
        
        # Name patterns (simple heuristic)
        self.name_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b')
    
    def extract(self, messages: List[Dict[str, str]]) -> List[Dict[str, any]]:
        """Extract action items from messages"""
        action_items = []
        
        for msg in messages:
            text = msg['text']
            
            # Check if message contains action indicators
            if not self._is_action_item(text):
                continue
            
            action_item = {
                'text': text,
                'speaker': msg['speaker'],
                'timestamp': msg.get('timestamp', ''),
                'assignee': self._extract_assignee(text, msg['speaker']),
                'deadline': self._extract_deadline(text)
            }
            
            action_items.append(action_item)
        
        return action_items
    
    def _is_action_item(self, text: str) -> bool:
        """Check if text contains action item indicators"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.action_patterns)
    
    def _extract_assignee(self, text: str, default_speaker: str) -> str:
        """Extract assignee from text"""
        text_lower = text.lower()
        
        # Look for explicit assignment
        assign_match = re.search(r'(?:assign|assigned to|owner:?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
        if assign_match:
            return assign_match.group(1)
        
        # Look for "I will" pattern
        if re.search(r'\bI\s+(will|should|need to|must)\b', text):
            return default_speaker
        
        # Extract first capitalized name
        names = self.name_pattern.findall(text)
        if names:
            return names[0] if isinstance(names[0], str) else names[0][0]
        
        return default_speaker
    
    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract deadline from text"""
        for pattern in self.deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline_text = match.group(0)
                try:
                    # Try to parse as date
                    parsed_date = date_parser.parse(deadline_text, fuzzy=True)
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    return deadline_text
        
        return None
