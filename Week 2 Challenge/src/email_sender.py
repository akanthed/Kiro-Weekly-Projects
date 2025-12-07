"""Send meeting summaries via email"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from src.exceptions import InvalidInputError, OutputError

# Setup logging
logger = logging.getLogger(__name__)


class EmailSender:
    """Send meeting summaries via email using SMTP"""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: bool = True
    ):
        """
        Initialize email sender
        
        Args:
            smtp_server: SMTP server address (default: from env SMTP_SERVER)
            smtp_port: SMTP port (default: from env SMTP_PORT or 587)
            smtp_username: SMTP username (default: from env SMTP_USERNAME)
            smtp_password: SMTP password (default: from env SMTP_PASSWORD)
            use_tls: Use TLS encryption (default: True)
        """
        # Load from environment variables if not provided
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = smtp_username or os.getenv('SMTP_USERNAME', '')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD', '')
        self.use_tls = use_tls
        
        # Validate credentials
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
    
    def send_summary(
        self,
        recipients: List[str],
        meeting_title: str,
        meeting_date: str,
        summary_content: str,
        format_type: str = 'markdown',
        transcript_path: Optional[str] = None,
        sender_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send meeting summary via email
        
        Args:
            recipients: List of recipient email addresses
            meeting_title: Title of the meeting
            meeting_date: Date of the meeting
            summary_content: Summary content (markdown or plain text)
            format_type: 'markdown' or 'plain'
            transcript_path: Optional path to transcript file to attach
            sender_email: Sender email (default: SMTP username)
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            
        Returns:
            True if email sent successfully
            
        Raises:
            InvalidInputError: If input validation fails
            OutputError: If email sending fails
        """
        # Input validation
        if not recipients or not isinstance(recipients, list):
            raise InvalidInputError("recipients", "Must be a non-empty list of email addresses")
        
        if not all('@' in email for email in recipients):
            raise InvalidInputError("recipients", "All recipients must be valid email addresses")
        
        if not meeting_title or not isinstance(meeting_title, str):
            raise InvalidInputError("meeting_title", "Must be a non-empty string")
        
        if not summary_content or not isinstance(summary_content, str):
            raise InvalidInputError("summary_content", "Must be a non-empty string")
        
        # Check credentials
        if not self.smtp_username or not self.smtp_password:
            raise OutputError(
                "SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables"
            )
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            
            # Set sender
            sender = sender_email or self.smtp_username
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Set subject
            subject = f"Action Items from {meeting_title} - {meeting_date}"
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Create email body
            if format_type == 'markdown':
                # Convert markdown to HTML for better email display
                html_body = self._markdown_to_html(summary_content, meeting_title, meeting_date)
                plain_body = self._create_plain_text_body(summary_content, meeting_title, meeting_date)
                
                # Attach both plain text and HTML versions
                msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            else:
                plain_body = self._create_plain_text_body(summary_content, meeting_title, meeting_date)
                msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
            
            # Attach transcript if provided
            if transcript_path and Path(transcript_path).exists():
                self._attach_file(msg, transcript_path)
            
            # Send email
            logger.info(f"Sending email to {len(recipients)} recipient(s)")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.smtp_username, self.smtp_password)
                
                # Combine all recipients
                all_recipients = recipients.copy()
                if cc:
                    all_recipients.extend(cc)
                if bcc:
                    all_recipients.extend(bcc)
                
                server.send_message(msg, from_addr=sender, to_addrs=all_recipients)
            
            logger.info(f"Email sent successfully to {', '.join(recipients)}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise OutputError(
                "Email authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD"
            )
        
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise OutputError(f"Failed to send email: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}", exc_info=True)
            raise OutputError(f"Failed to send email: {str(e)}")
    
    def _create_plain_text_body(
        self,
        summary_content: str,
        meeting_title: str,
        meeting_date: str
    ) -> str:
        """Create plain text email body"""
        template = f"""
Hello Team,

Please find below the action items from our {meeting_title} meeting held on {meeting_date}.

{'='*70}

{summary_content}

{'='*70}

This summary was automatically generated by the Meeting Action Items Extractor.

Please review your assigned action items and reach out if you have any questions.

Best regards,
Meeting Action Items Extractor
"""
        return template.strip()
    
    def _markdown_to_html(
        self,
        markdown_content: str,
        meeting_title: str,
        meeting_date: str
    ) -> str:
        """Convert markdown summary to HTML for email"""
        # Simple markdown to HTML conversion
        # For production, consider using a library like markdown2 or mistune
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        li {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .priority-high {{
            border-left-color: #e74c3c;
        }}
        .priority-medium {{
            border-left-color: #f39c12;
        }}
        .priority-low {{
            border-left-color: #2ecc71;
        }}
        .stats {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        .assignee {{
            color: #3498db;
            font-weight: bold;
        }}
        .deadline {{
            color: #e74c3c;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1>📋 {meeting_title}</h1>
            <p><strong>Date:</strong> {meeting_date}</p>
        </div>
        
        <div class="content">
            {self._convert_markdown_to_html_simple(markdown_content)}
        </div>
        
        <div class="footer">
            <p>This summary was automatically generated by the Meeting Action Items Extractor.</p>
            <p>Please review your assigned action items and reach out if you have any questions.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _convert_markdown_to_html_simple(self, markdown: str) -> str:
        """Simple markdown to HTML conversion"""
        html = markdown
        
        # Convert headers
        html = html.replace('# ', '<h1>').replace('\n\n', '</h1>\n\n')
        html = html.replace('## ', '<h2>').replace('\n\n', '</h2>\n\n')
        html = html.replace('### ', '<h3>').replace('\n\n', '</h3>\n\n')
        
        # Convert bold
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert lists
        lines = html.split('\n')
        in_list = False
        result = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        
        if in_list:
            result.append('</ul>')
        
        html = '\n'.join(result)
        
        # Convert line breaks
        html = html.replace('\n\n', '<br><br>')
        
        return html
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Attach a file to the email"""
        try:
            path = Path(file_path)
            
            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {path.name}'
            )
            
            msg.attach(part)
            logger.debug(f"Attached file: {path.name}")
            
        except Exception as e:
            logger.warning(f"Failed to attach file {file_path}: {e}")
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection and credentials
        
        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Testing SMTP connection to {self.smtp_server}:{self.smtp_port}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.smtp_username, self.smtp_password)
            
            logger.info("SMTP connection test successful")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return False
        
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False


def parse_email_list(email_string: str) -> List[str]:
    """
    Parse comma-separated email addresses
    
    Args:
        email_string: Comma-separated email addresses
        
    Returns:
        List of email addresses
    """
    if not email_string:
        return []
    
    # Split by comma and clean up
    emails = [email.strip() for email in email_string.split(',')]
    
    # Filter out empty strings
    emails = [email for email in emails if email]
    
    return emails
