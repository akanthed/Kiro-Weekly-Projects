"""Generate meeting summaries from extracted action items"""
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from src.action_detector import ActionItem
from src.exceptions import (
    InvalidInputError,
    OutputError,
    NoActionItemsError
)

# Setup logging
logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generate formatted summaries from action items"""
    
    def __init__(self):
        self.priority_emojis = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
    
    def generate_markdown(
        self,
        action_items: List[ActionItem],
        meeting_title: str = "Meeting",
        meeting_date: Optional[str] = None,
        include_stats: bool = True,
        include_context: bool = False
    ) -> str:
        """
        Generate a formatted Markdown summary
        
        Args:
            action_items: List of ActionItem objects
            meeting_title: Title of the meeting
            meeting_date: Date of the meeting (defaults to today)
            include_stats: Include statistics section
            include_context: Include context for each action item
            
        Returns:
            Formatted Markdown string
            
        Raises:
            InvalidInputError: If input validation fails
            OutputError: If markdown generation fails
        """
        # Input validation
        if not isinstance(action_items, list):
            logger.error(f"Invalid action_items type: {type(action_items)}")
            raise InvalidInputError("action_items", f"Expected list, got {type(action_items)}")
        
        if not isinstance(meeting_title, str) or not meeting_title.strip():
            logger.error(f"Invalid meeting_title: {meeting_title}")
            raise InvalidInputError("meeting_title", "Must be a non-empty string")
        
        try:
            if meeting_date is None:
                meeting_date = datetime.now().strftime('%B %d, %Y')
            
            logger.info(f"Generating markdown for {len(action_items)} action items")
            
            sections = []
            
            # Header
            sections.append(f"# 📋 {meeting_title}")
            sections.append(f"\n**Date:** {meeting_date}")
            sections.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            sections.append("---\n")
            
            # Statistics
            if include_stats and action_items:
                sections.append(self._generate_stats_section(action_items))
            
            # Action Items
            sections.append(self._generate_action_items_section(action_items, include_context))
            
            # Action Items by Assignee
            if action_items:
                sections.append(self._generate_by_assignee_section(action_items))
            
            # Action Items by Priority
            if action_items:
                sections.append(self._generate_by_priority_section(action_items))
            
            # Upcoming Deadlines
            if action_items:
                sections.append(self._generate_deadlines_section(action_items))
            
            # Next Steps
            sections.append(self._generate_next_steps_section(action_items))
            
            markdown = "\n".join(sections)
            logger.info(f"Successfully generated markdown ({len(markdown)} characters)")
            return markdown
            
        except Exception as e:
            logger.error(f"Error generating markdown: {e}", exc_info=True)
            raise OutputError(f"Markdown generation failed: {str(e)}")
    
    def _generate_stats_section(self, action_items: List[ActionItem]) -> str:
        """Generate statistics section"""
        total = len(action_items)
        
        # Count by priority
        high = len([i for i in action_items if i.priority == 'high'])
        medium = len([i for i in action_items if i.priority == 'medium'])
        low = len([i for i in action_items if i.priority == 'low'])
        
        # Count with deadlines
        with_deadline = len([i for i in action_items if i.deadline])
        
        # Count assigned
        assigned = len([i for i in action_items if i.assignee])
        
        # Unique assignees
        assignees = set(i.assignee for i in action_items if i.assignee)
        
        section = [
            "## 📊 Summary Statistics\n",
            f"- **Total Action Items:** {total}",
            f"- **Assigned:** {assigned} | **Unassigned:** {total - assigned}",
            f"- **With Deadlines:** {with_deadline}",
            f"- **Unique Assignees:** {len(assignees)}",
            f"- **Priority Breakdown:**",
            f"  - {self.priority_emojis['high']} High: {high}",
            f"  - {self.priority_emojis['medium']} Medium: {medium}",
            f"  - {self.priority_emojis['low']} Low: {low}",
            "\n---\n"
        ]
        
        return "\n".join(section)
    
    def _generate_action_items_section(self, action_items: List[ActionItem], include_context: bool) -> str:
        """Generate main action items section"""
        section = ["## ✅ Action Items\n"]
        
        if not action_items:
            section.append("*No action items detected in this meeting.*\n")
            return "\n".join(section)
        
        for idx, item in enumerate(action_items, 1):
            # Priority emoji
            priority_emoji = self.priority_emojis.get(item.priority, '⚪')
            
            # Assignee
            assignee_str = f"@{item.assignee}" if item.assignee else "*Unassigned*"
            
            # Deadline
            deadline_str = f"📅 **Deadline:** {item.deadline}" if item.deadline else ""
            
            # Build task line
            task_line = f"{idx}. {priority_emoji} [ ] {item.task}"
            section.append(task_line)
            
            # Add metadata
            metadata = []
            metadata.append(f"   - **Assignee:** {assignee_str}")
            if deadline_str:
                metadata.append(f"   - {deadline_str}")
            if item.priority != 'medium':
                metadata.append(f"   - **Priority:** {item.priority.capitalize()}")
            if item.timestamp:
                metadata.append(f"   - **Mentioned at:** {item.timestamp}")
            
            section.extend(metadata)
            
            # Add context if requested
            if include_context and item.context:
                section.append(f"   - *Context:* {item.context[:150]}...")
            
            section.append("")  # Empty line between items
        
        section.append("---\n")
        return "\n".join(section)
    
    def _generate_by_assignee_section(self, action_items: List[ActionItem]) -> str:
        """Generate action items grouped by assignee"""
        section = ["## 👥 Action Items by Assignee\n"]
        
        # Group by assignee
        by_assignee = defaultdict(list)
        for item in action_items:
            assignee = item.assignee if item.assignee else "Unassigned"
            by_assignee[assignee].append(item)
        
        # Sort by assignee name
        for assignee in sorted(by_assignee.keys()):
            items = by_assignee[assignee]
            section.append(f"### {assignee} ({len(items)} items)\n")
            
            for item in items:
                priority_emoji = self.priority_emojis.get(item.priority, '⚪')
                deadline = f" - 📅 {item.deadline}" if item.deadline else ""
                section.append(f"- {priority_emoji} {item.task}{deadline}")
            
            section.append("")  # Empty line between assignees
        
        section.append("---\n")
        return "\n".join(section)
    
    def _generate_by_priority_section(self, action_items: List[ActionItem]) -> str:
        """Generate action items grouped by priority"""
        section = ["## 🎯 Action Items by Priority\n"]
        
        # Group by priority
        by_priority = {
            'high': [i for i in action_items if i.priority == 'high'],
            'medium': [i for i in action_items if i.priority == 'medium'],
            'low': [i for i in action_items if i.priority == 'low']
        }
        
        for priority in ['high', 'medium', 'low']:
            items = by_priority[priority]
            if not items:
                continue
            
            emoji = self.priority_emojis[priority]
            section.append(f"### {emoji} {priority.capitalize()} Priority ({len(items)} items)\n")
            
            for item in items:
                assignee = f"@{item.assignee}" if item.assignee else "*Unassigned*"
                deadline = f" - 📅 {item.deadline}" if item.deadline else ""
                section.append(f"- {item.task} ({assignee}){deadline}")
            
            section.append("")
        
        section.append("---\n")
        return "\n".join(section)
    
    def _generate_deadlines_section(self, action_items: List[ActionItem]) -> str:
        """Generate upcoming deadlines section"""
        section = ["## 📅 Upcoming Deadlines\n"]
        
        # Filter items with deadlines
        items_with_deadlines = [i for i in action_items if i.deadline]
        
        if not items_with_deadlines:
            section.append("*No deadlines specified.*\n")
            return "\n".join(section)
        
        # Sort by deadline
        try:
            sorted_items = sorted(
                items_with_deadlines,
                key=lambda x: self._parse_deadline_for_sort(x.deadline)
            )
        except:
            sorted_items = items_with_deadlines
        
        for item in sorted_items:
            priority_emoji = self.priority_emojis.get(item.priority, '⚪')
            assignee = f"@{item.assignee}" if item.assignee else "*Unassigned*"
            section.append(f"- **{item.deadline}** {priority_emoji} - {item.task} ({assignee})")
        
        section.append("\n---\n")
        return "\n".join(section)
    
    def _generate_next_steps_section(self, action_items: List[ActionItem]) -> str:
        """Generate next steps section"""
        section = ["## 🚀 Next Steps\n"]
        
        if not action_items:
            section.append("*No immediate next steps identified.*\n")
            return "\n".join(section)
        
        # Get high priority items
        high_priority = [i for i in action_items if i.priority == 'high']
        
        if high_priority:
            section.append("**Immediate Actions (High Priority):**\n")
            for item in high_priority[:5]:  # Top 5
                assignee = f"@{item.assignee}" if item.assignee else "*Unassigned*"
                section.append(f"1. {assignee} - {item.task}")
            section.append("")
        
        # Get items with near deadlines
        urgent_deadlines = [
            i for i in action_items 
            if i.deadline and any(x in i.deadline.upper() for x in ['ASAP', 'TODAY', 'TOMORROW', 'EOD'])
        ]
        
        if urgent_deadlines:
            section.append("**Urgent Deadlines:**\n")
            for item in urgent_deadlines:
                assignee = f"@{item.assignee}" if item.assignee else "*Unassigned*"
                section.append(f"- {assignee} - {item.task} (Due: {item.deadline})")
            section.append("")
        
        section.append("**General Recommendations:**")
        section.append("- Review and assign unassigned action items")
        section.append("- Set deadlines for items without due dates")
        section.append("- Schedule follow-up meeting if needed")
        section.append("")
        
        return "\n".join(section)
    
    def _parse_deadline_for_sort(self, deadline: str) -> datetime:
        """Parse deadline string for sorting"""
        # Handle special cases
        if 'ASAP' in deadline.upper():
            return datetime.now()
        if 'TODAY' in deadline.upper():
            return datetime.now()
        if 'TOMORROW' in deadline.upper():
            return datetime.now()
        
        # Try to parse ISO date
        try:
            return datetime.strptime(deadline.split()[0], '%Y-%m-%d')
        except:
            # Return far future if can't parse
            return datetime(2099, 12, 31)
    
    def generate_json(
        self,
        action_items: List[ActionItem],
        meeting_title: str = "Meeting",
        meeting_date: Optional[str] = None,
        include_stats: bool = True
    ) -> str:
        """
        Generate JSON output for API integration
        
        Args:
            action_items: List of ActionItem objects
            meeting_title: Title of the meeting
            meeting_date: Date of the meeting
            include_stats: Include statistics
            
        Returns:
            JSON string
        """
        if meeting_date is None:
            meeting_date = datetime.now().strftime('%Y-%m-%d')
        
        output = {
            'meeting': {
                'title': meeting_title,
                'date': meeting_date,
                'generated_at': datetime.now().isoformat()
            },
            'action_items': [item.to_dict() for item in action_items]
        }
        
        if include_stats:
            output['statistics'] = self._generate_statistics_dict(action_items)
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def _generate_statistics_dict(self, action_items: List[ActionItem]) -> Dict:
        """Generate statistics as dictionary"""
        total = len(action_items)
        
        # By assignee
        by_assignee = defaultdict(int)
        for item in action_items:
            assignee = item.assignee if item.assignee else "Unassigned"
            by_assignee[assignee] += 1
        
        # By priority
        by_priority = {
            'high': len([i for i in action_items if i.priority == 'high']),
            'medium': len([i for i in action_items if i.priority == 'medium']),
            'low': len([i for i in action_items if i.priority == 'low'])
        }
        
        # Deadlines
        with_deadline = len([i for i in action_items if i.deadline])
        
        return {
            'total_items': total,
            'assigned': len([i for i in action_items if i.assignee]),
            'unassigned': len([i for i in action_items if not i.assignee]),
            'with_deadline': with_deadline,
            'without_deadline': total - with_deadline,
            'by_assignee': dict(by_assignee),
            'by_priority': by_priority,
            'unique_assignees': len(set(i.assignee for i in action_items if i.assignee))
        }
    
    def save_to_file(
        self,
        content: str,
        output_path: str,
        format_type: str = 'markdown'
    ) -> None:
        """
        Save summary to file
        
        Args:
            content: Content to save
            output_path: Path to output file
            format_type: 'markdown' or 'json'
            
        Raises:
            InvalidInputError: If input validation fails
            OutputError: If file cannot be written
        """
        # Input validation
        if not isinstance(content, str):
            logger.error(f"Invalid content type: {type(content)}")
            raise InvalidInputError("content", f"Expected string, got {type(content)}")
        
        if not content:
            logger.warning("Empty content provided for saving")
            raise InvalidInputError("content", "Content cannot be empty")
        
        if not isinstance(output_path, (str, Path)) or not str(output_path).strip():
            logger.error(f"Invalid output_path: {output_path}")
            raise InvalidInputError("output_path", "Must be a non-empty string or Path")
        
        if format_type not in ['markdown', 'json']:
            logger.error(f"Invalid format_type: {format_type}")
            raise InvalidInputError("format_type", "Must be 'markdown' or 'json'")
        
        try:
            path = Path(output_path)
            
            # Create parent directories if needed
            if path.parent != Path('.'):
                path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {path.parent}")
            
            # Add extension if not present
            if format_type == 'markdown' and not output_path.endswith('.md'):
                path = path.with_suffix('.md')
            elif format_type == 'json' and not output_path.endswith('.json'):
                path = path.with_suffix('.json')
            
            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Successfully saved {format_type} to: {path}")
            
        except PermissionError as e:
            logger.error(f"Permission denied writing to {output_path}: {e}")
            raise OutputError(f"Permission denied: {output_path}")
        except OSError as e:
            logger.error(f"OS error writing to {output_path}: {e}")
            raise OutputError(f"Cannot write to file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error saving file: {e}", exc_info=True)
            raise OutputError(f"Failed to save file: {str(e)}")
    
    def generate_compact_summary(self, action_items: List[ActionItem]) -> str:
        """Generate a compact one-line summary"""
        total = len(action_items)
        high = len([i for i in action_items if i.priority == 'high'])
        assigned = len([i for i in action_items if i.assignee])
        with_deadline = len([i for i in action_items if i.deadline])
        
        return (
            f"📋 {total} action items | "
            f"🔴 {high} high priority | "
            f"👥 {assigned} assigned | "
            f"📅 {with_deadline} with deadlines"
        )
    
    def generate_email_body(
        self,
        action_items: List[ActionItem],
        meeting_title: str = "Meeting",
        meeting_date: Optional[str] = None
    ) -> str:
        """Generate formatted email body"""
        if meeting_date is None:
            meeting_date = datetime.now().strftime('%B %d, %Y')
        
        body = [
            f"Hello Team,\n",
            f"Here's a summary of action items from our {meeting_title} on {meeting_date}.\n",
            f"---\n"
        ]
        
        # Add compact summary
        body.append(self.generate_compact_summary(action_items))
        body.append("\n\nACTION ITEMS:\n")
        
        # Group by assignee
        by_assignee = defaultdict(list)
        for item in action_items:
            assignee = item.assignee if item.assignee else "Unassigned"
            by_assignee[assignee].append(item)
        
        for assignee in sorted(by_assignee.keys()):
            items = by_assignee[assignee]
            body.append(f"\n{assignee}:")
            for item in items:
                deadline = f" (Due: {item.deadline})" if item.deadline else ""
                priority = f" [{item.priority.upper()}]" if item.priority == 'high' else ""
                body.append(f"  • {item.task}{deadline}{priority}")
        
        body.append("\n\nPlease review your assigned items and reach out if you have any questions.")
        body.append("\n\nBest regards")
        
        return "\n".join(body)
