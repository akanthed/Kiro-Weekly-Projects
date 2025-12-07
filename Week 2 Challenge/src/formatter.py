"""Format action items as Markdown"""
from typing import List, Dict
from datetime import datetime


class MarkdownFormatter:
    """Generate structured Markdown summaries"""
    
    def format(self, action_items: List[Dict[str, any]], meeting_title: str = "Meeting") -> str:
        """Format action items as Markdown"""
        if not action_items:
            return f"# {meeting_title} - Action Items\n\nNo action items found."
        
        output = [
            f"# {meeting_title} - Action Items",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\n**Total Items:** {len(action_items)}\n",
            "---\n"
        ]
        
        # Group by assignee
        by_assignee = {}
        for item in action_items:
            assignee = item['assignee']
            if assignee not in by_assignee:
                by_assignee[assignee] = []
            by_assignee[assignee].append(item)
        
        # Format by assignee
        for assignee, items in sorted(by_assignee.items()):
            output.append(f"## {assignee}\n")
            for idx, item in enumerate(items, 1):
                output.append(f"{idx}. **Action:** {item['text']}")
                if item['deadline']:
                    output.append(f"   - **Deadline:** {item['deadline']}")
                if item['timestamp']:
                    output.append(f"   - **Mentioned at:** {item['timestamp']}")
                output.append("")
        
        return "\n".join(output)
