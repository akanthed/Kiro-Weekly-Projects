#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Meeting Action Items Extractor CLI"""
import click
import yaml
import logging
import io
from pathlib import Path
from typing import Optional
from datetime import datetime
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.parser import TranscriptParser
from src.action_detector import ActionDetector
from src.summary_generator import SummaryGenerator
from src.email_sender import EmailSender, parse_email_list
from src.exceptions import (
    MeetingExtractorError,
    FileNotFoundError,
    EmptyTranscriptError,
    MalformedTranscriptError,
    NoActionItemsError,
    UnsupportedFormatError,
    EncodingError,
    InvalidInputError,
    OutputError
)

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meeting_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Load configuration
def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file"""
    try:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
    except Exception as e:
        click.echo(click.style(f"⚠️  Warning: Could not load config: {e}", fg='yellow'))
    
    # Return default config
    return {
        'output': {
            'default_format': 'markdown',
            'include_stats': True,
            'include_context': False
        }
    }


CONFIG = load_config()


@click.group()
@click.version_option(version='1.0.0', prog_name='Meeting Action Items Extractor')
def cli():
    """
    🎯 Meeting Action Items Extractor
    
    Automatically extract action items, deadlines, and assignees from meeting transcripts.
    
    Supports Zoom, Google Meet, and plain text formats.
    
    \b
    Examples:
      # Basic parsing
      python main.py parse meeting.txt
      
      # Specify output format
      python main.py parse meeting.txt --format json
      
      # Save to specific file
      python main.py parse meeting.txt --output summary.md
      
      # Process multiple files
      python main.py batch transcripts/
      
      # Custom meeting title
      python main.py parse meeting.txt --title "Sprint Planning"
    """
    pass


@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
@click.option(
    '--format', '-f',
    type=click.Choice(['markdown', 'json', 'both'], case_sensitive=False),
    default=CONFIG.get('output', {}).get('default_format', 'markdown'),
    help='Output format (default: markdown)'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output file path (default: <input>_summary.md)'
)
@click.option(
    '--title', '-t',
    default='Meeting',
    help='Meeting title for the report'
)
@click.option(
    '--date', '-d',
    help='Meeting date (default: today)'
)
@click.option(
    '--no-stats',
    is_flag=True,
    help='Exclude statistics from output'
)
@click.option(
    '--context',
    is_flag=True,
    help='Include surrounding context for each action item'
)
@click.option(
    '--quiet', '-q',
    is_flag=True,
    help='Minimal output (errors only)'
)
@click.option(
    '--email', '-e',
    help='Send summary via email (comma-separated addresses)'
)
@click.option(
    '--email-cc',
    help='CC recipients (comma-separated addresses)'
)
@click.option(
    '--attach-transcript',
    is_flag=True,
    help='Attach original transcript to email'
)
def parse(
    transcript_file: str,
    format: str,
    output: Optional[str],
    title: str,
    date: Optional[str],
    no_stats: bool,
    context: bool,
    quiet: bool,
    email: Optional[str],
    email_cc: Optional[str],
    attach_transcript: bool
):
    """
    Parse a meeting transcript and extract action items.
    
    TRANSCRIPT_FILE: Path to the meeting transcript file
    
    \b
    Supported formats:
      - Zoom: "00:00:00 John Doe: Message"
      - Google Meet: "10:30 AM John Doe: Message"
      - Plain text: "John Doe: Message"
    """
    try:
        transcript_path = Path(transcript_file)
        
        if not quiet:
            click.echo(click.style(f"\n📄 Processing: {transcript_path.name}", fg='cyan', bold=True))
        
        # Read and parse transcript
        if not quiet:
            click.echo("🔍 Parsing transcript...", nl=False)
        
        parser = TranscriptParser()
        messages = parser.parse_file(transcript_file)
        
        if not quiet:
            click.echo(click.style(f" ✓ Found {len(messages)} messages", fg='green'))
        
        # Get format statistics
        stats = parser.get_format_stats(messages)
        if not quiet and stats['unique_speakers'] > 0:
            speakers = parser.get_speakers(messages)
            click.echo(f"   👥 Speakers: {', '.join(speakers[:5])}" + 
                      (f" (+{len(speakers)-5} more)" if len(speakers) > 5 else ""))
        
        # Extract action items
        if not quiet:
            click.echo("🎯 Extracting action items...", nl=False)
        
        detector = ActionDetector()
        action_items = detector.extract_action_items(messages)
        
        if not quiet:
            click.echo(click.style(f" ✓ Found {len(action_items)} action items", fg='green'))
        
        if len(action_items) == 0:
            click.echo(click.style("\n⚠️  No action items detected in transcript", fg='yellow'))
            click.echo("   Try checking if the transcript contains action keywords like:")
            click.echo("   'will', 'should', 'need to', 'action item', 'TODO', etc.")
            return
        
        # Show quick stats
        if not quiet:
            item_stats = detector.get_statistics(action_items)
            click.echo(f"   🔴 High: {item_stats['by_priority']['high']} | "
                      f"🟡 Medium: {item_stats['by_priority']['medium']} | "
                      f"🟢 Low: {item_stats['by_priority']['low']}")
        
        # Generate summary
        if not quiet:
            click.echo("📝 Generating summary...", nl=False)
        
        generator = SummaryGenerator()
        include_stats = not no_stats
        
        # Determine output path
        if not output:
            if format == 'json':
                output = transcript_path.stem + '_summary.json'
            else:
                output = transcript_path.stem + '_summary.md'
        
        # Generate and save
        if format == 'markdown' or format == 'both':
            markdown = generator.generate_markdown(
                action_items,
                meeting_title=title,
                meeting_date=date,
                include_stats=include_stats,
                include_context=context
            )
            
            md_output = output if format == 'markdown' else str(Path(output).with_suffix('.md'))
            generator.save_to_file(markdown, md_output, 'markdown')
            
            if not quiet:
                click.echo(click.style(f" ✓", fg='green'))
                click.echo(click.style(f"✅ Markdown saved to: {md_output}", fg='green', bold=True))
        
        if format == 'json' or format == 'both':
            json_output_str = generator.generate_json(
                action_items,
                meeting_title=title,
                meeting_date=date,
                include_stats=include_stats
            )
            
            json_output = output if format == 'json' else str(Path(output).with_suffix('.json'))
            generator.save_to_file(json_output_str, json_output, 'json')
            
            if not quiet:
                click.echo(click.style(f"✅ JSON saved to: {json_output}", fg='green', bold=True))
        
        # Send email if requested
        if email:
            if not quiet:
                click.echo("\n📧 Sending email...", nl=False)
            
            try:
                email_sender = EmailSender()
                recipients = parse_email_list(email)
                cc_recipients = parse_email_list(email_cc) if email_cc else None
                
                # Use markdown content for email
                email_content = markdown if format != 'json' else generator.generate_markdown(
                    action_items, title, date, include_stats, context
                )
                
                # Determine meeting date for email
                email_date = date if date else datetime.now().strftime('%B %d, %Y')
                
                # Send email
                email_sender.send_summary(
                    recipients=recipients,
                    meeting_title=title,
                    meeting_date=email_date,
                    summary_content=email_content,
                    format_type='markdown',
                    transcript_path=transcript_file if attach_transcript else None,
                    cc=cc_recipients
                )
                
                if not quiet:
                    click.echo(click.style(f" ✓", fg='green'))
                    click.echo(click.style(f"📧 Email sent to: {', '.join(recipients)}", fg='green', bold=True))
                
            except OutputError as e:
                click.echo(click.style(f" ✗", fg='red'))
                click.echo(click.style(f"\n⚠️  Email Error: {e.message}", fg='yellow'), err=True)
                if e.suggestion:
                    click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
                click.echo("\n💡 To configure email:", err=True)
                click.echo("  1. Copy .env.example to .env", err=True)
                click.echo("  2. Fill in your SMTP credentials", err=True)
                click.echo("  3. For Gmail, use an App Password\n", err=True)
            
            except Exception as e:
                click.echo(click.style(f" ✗", fg='red'))
                click.echo(click.style(f"\n⚠️  Failed to send email: {e}", fg='yellow'), err=True)
        
        # Show compact summary
        if not quiet:
            click.echo(f"\n{generator.generate_compact_summary(action_items)}\n")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {transcript_file}")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except EmptyTranscriptError as e:
        logger.error("Empty transcript")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except MalformedTranscriptError as e:
        logger.error(f"Malformed transcript: {e.message}")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"\n💡 Suggestion:", fg='cyan'), err=True)
            click.echo(click.style(f"{e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except NoActionItemsError as e:
        logger.warning("No action items found")
        click.echo(click.style(f"\n⚠️  {e.message}", fg='yellow'))
        if e.suggestion:
            click.echo(click.style(f"\n💡 Suggestion:", fg='cyan'))
            click.echo(click.style(f"{e.suggestion}", fg='yellow'))
        sys.exit(0)  # Not a fatal error
    
    except UnsupportedFormatError as e:
        logger.error(f"Unsupported format: {transcript_file}")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except EncodingError as e:
        logger.error(f"Encoding error: {transcript_file}")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except InvalidInputError as e:
        logger.error(f"Invalid input: {e.message}")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except OutputError as e:
        logger.error(f"Output error: {e.message}")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except MeetingExtractorError as e:
        logger.error(f"Meeting extractor error: {e.message}")
        click.echo(click.style(f"\n❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        click.echo(click.style(f"\n❌ Unexpected Error: {e}", fg='red', bold=True), err=True)
        if not quiet:
            import traceback
            click.echo("\n📋 Full error details:", err=True)
            click.echo(traceback.format_exc(), err=True)
        click.echo("\n💡 If this persists, check the log file: meeting_extractor.log", err=True)
        sys.exit(1)


@cli.command()
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--format', '-f',
    type=click.Choice(['markdown', 'json', 'both'], case_sensitive=False),
    default='markdown',
    help='Output format'
)
@click.option(
    '--pattern', '-p',
    default='*.txt',
    help='File pattern to match (default: *.txt)'
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(),
    help='Output directory (default: <folder>/summaries)'
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Process files recursively'
)
def batch(folder: str, format: str, pattern: str, output_dir: Optional[str], recursive: bool):
    """
    Process multiple transcript files in a folder.
    
    FOLDER: Path to folder containing transcript files
    
    \b
    Examples:
      python main.py batch transcripts/
      python main.py batch meetings/ --pattern "*.txt" --recursive
      python main.py batch data/ --output-dir summaries/
    """
    try:
        folder_path = Path(folder)
        
        # Find files
        if recursive:
            files = list(folder_path.rglob(pattern))
        else:
            files = list(folder_path.glob(pattern))
        
        if not files:
            click.echo(click.style(f"⚠️  No files matching '{pattern}' found in {folder}", fg='yellow'))
            return
        
        click.echo(click.style(f"\n📁 Found {len(files)} file(s) to process\n", fg='cyan', bold=True))
        
        # Setup output directory
        if not output_dir:
            output_dir = folder_path / 'summaries'
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process files with progress bar
        success_count = 0
        error_count = 0
        
        with click.progressbar(
            files,
            label='Processing transcripts',
            item_show_func=lambda f: f.name if f else ''
        ) as bar:
            for file in bar:
                try:
                    # Parse
                    parser = TranscriptParser()
                    messages = parser.parse_file(str(file))
                    
                    # Extract
                    detector = ActionDetector()
                    action_items = detector.extract_action_items(messages)
                    
                    if len(action_items) == 0:
                        click.echo(f"\n⚠️  {file.name}: No action items found", err=True)
                        continue
                    
                    # Generate
                    generator = SummaryGenerator()
                    output_file = output_path / f"{file.stem}_summary"
                    
                    if format == 'markdown' or format == 'both':
                        markdown = generator.generate_markdown(action_items, meeting_title=file.stem)
                        generator.save_to_file(markdown, str(output_file) + '.md', 'markdown')
                    
                    if format == 'json' or format == 'both':
                        json_str = generator.generate_json(action_items, meeting_title=file.stem)
                        generator.save_to_file(json_str, str(output_file) + '.json', 'json')
                    
                    success_count += 1
                    logger.info(f"Successfully processed: {file.name}")
                    
                except (FileNotFoundError, EmptyTranscriptError, MalformedTranscriptError) as e:
                    click.echo(f"\n⚠️  {file.name}: {e.message}", err=True)
                    error_count += 1
                    logger.warning(f"Failed to process {file.name}: {e.message}")
                    
                except Exception as e:
                    click.echo(f"\n❌ {file.name}: {str(e)}", err=True)
                    error_count += 1
                    logger.error(f"Unexpected error processing {file.name}: {e}", exc_info=True)
        
        # Summary
        click.echo(click.style(f"\n✅ Batch processing complete!", fg='green', bold=True))
        click.echo(f"   Success: {success_count} | Errors: {error_count}")
        click.echo(f"   Output directory: {output_path}\n")
        
        if error_count > 0:
            click.echo(click.style(f"💡 Check meeting_extractor.log for detailed error information", fg='yellow'))
        
    except PermissionError as e:
        logger.error(f"Permission error in batch processing: {e}")
        click.echo(click.style(f"\n❌ Permission Error: Cannot access {folder}", fg='red', bold=True), err=True)
        click.echo(click.style("💡 Check folder permissions and try again", fg='yellow'), err=True)
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}", exc_info=True)
        click.echo(click.style(f"\n❌ Batch Error: {e}", fg='red', bold=True), err=True)
        click.echo(click.style("💡 Check the log file for details: meeting_extractor.log", fg='yellow'), err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration settings"""
    click.echo(click.style("\n⚙️  Current Configuration\n", fg='cyan', bold=True))
    
    config_file = Path('config.yaml')
    if config_file.exists():
        click.echo(f"Config file: {config_file.absolute()}\n")
        with open(config_file, 'r') as f:
            click.echo(f.read())
    else:
        click.echo(click.style("No config.yaml found. Using defaults.\n", fg='yellow'))
        click.echo("Create a config.yaml file to customize settings.")
        click.echo("See config.yaml.example for available options.\n")


@cli.command()
@click.argument('transcript_file', type=click.Path(exists=True))
def validate(transcript_file: str):
    """
    Validate a transcript file without processing.
    
    Checks if the file can be parsed and shows format statistics.
    """
    try:
        click.echo(click.style(f"\n🔍 Validating: {transcript_file}\n", fg='cyan', bold=True))
        
        parser = TranscriptParser()
        messages = parser.parse_file(transcript_file)
        
        click.echo(click.style("✅ File is valid!", fg='green', bold=True))
        
        # Show statistics
        stats = parser.get_format_stats(messages)
        click.echo(f"\n📊 Statistics:")
        click.echo(f"   Total messages: {stats['total_messages']}")
        click.echo(f"   With timestamps: {stats['with_timestamps']}")
        click.echo(f"   Without timestamps: {stats['without_timestamps']}")
        click.echo(f"   Unique speakers: {stats['unique_speakers']}")
        click.echo(f"   Unknown speakers: {stats['unknown_speakers']}")
        
        # Show speakers
        speakers = parser.get_speakers(messages)
        if speakers:
            click.echo(f"\n👥 Speakers: {', '.join(speakers)}")
        
        # Show sample messages
        click.echo(f"\n📝 Sample messages:")
        for msg in messages[:3]:
            timestamp = f"[{msg['timestamp']}] " if msg['timestamp'] else ""
            click.echo(f"   {timestamp}{msg['speaker']}: {msg['text'][:60]}...")
        
        click.echo()
        logger.info(f"Validation successful for: {transcript_file}")
        
    except FileNotFoundError as e:
        logger.error(f"File not found during validation: {transcript_file}")
        click.echo(click.style(f"❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
        
    except EmptyTranscriptError as e:
        logger.error("Empty transcript during validation")
        click.echo(click.style(f"❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
        
    except MalformedTranscriptError as e:
        logger.error(f"Malformed transcript during validation: {e.message}")
        click.echo(click.style(f"❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"\n💡 Suggestion:", fg='cyan'), err=True)
            click.echo(click.style(f"{e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
        
    except MeetingExtractorError as e:
        logger.error(f"Validation error: {e.message}")
        click.echo(click.style(f"❌ {e.message}", fg='red', bold=True), err=True)
        if e.suggestion:
            click.echo(click.style(f"💡 {e.suggestion}", fg='yellow'), err=True)
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}", exc_info=True)
        click.echo(click.style(f"❌ Unexpected error: {e}", fg='red', bold=True), err=True)
        sys.exit(1)


@cli.command()
def test_email():
    """
    Test email configuration and SMTP connection.
    
    Verifies that SMTP credentials are configured correctly.
    """
    try:
        click.echo(click.style("\n🔧 Testing Email Configuration\n", fg='cyan', bold=True))
        
        # Load email sender
        email_sender = EmailSender()
        
        # Check if credentials are configured
        if not email_sender.smtp_username or not email_sender.smtp_password:
            click.echo(click.style("❌ SMTP credentials not configured", fg='red', bold=True))
            click.echo("\n💡 To configure email:")
            click.echo("  1. Copy .env.example to .env")
            click.echo("  2. Fill in your SMTP credentials:")
            click.echo("     - SMTP_SERVER (e.g., smtp.gmail.com)")
            click.echo("     - SMTP_PORT (e.g., 587)")
            click.echo("     - SMTP_USERNAME (your email)")
            click.echo("     - SMTP_PASSWORD (your app password)")
            click.echo("\n  For Gmail:")
            click.echo("     - Enable 2-factor authentication")
            click.echo("     - Generate App Password at: https://myaccount.google.com/apppasswords")
            click.echo()
            sys.exit(1)
        
        # Show configuration
        click.echo(f"SMTP Server: {email_sender.smtp_server}")
        click.echo(f"SMTP Port: {email_sender.smtp_port}")
        click.echo(f"SMTP Username: {email_sender.smtp_username}")
        click.echo(f"Use TLS: {email_sender.use_tls}")
        
        # Test connection
        click.echo("\n🔌 Testing SMTP connection...", nl=False)
        
        if email_sender.test_connection():
            click.echo(click.style(" ✓", fg='green'))
            click.echo(click.style("\n✅ Email configuration is working!", fg='green', bold=True))
            click.echo("\nYou can now send emails using:")
            click.echo("  python main.py parse meeting.txt --email recipient@example.com\n")
        else:
            click.echo(click.style(" ✗", fg='red'))
            click.echo(click.style("\n❌ SMTP connection failed", fg='red', bold=True))
            click.echo("\n💡 Troubleshooting:")
            click.echo("  • Check your SMTP server and port")
            click.echo("  • Verify your username and password")
            click.echo("  • For Gmail, use an App Password (not your regular password)")
            click.echo("  • Check if your firewall allows SMTP connections")
            click.echo()
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Email test error: {e}", exc_info=True)
        click.echo(click.style(f"\n❌ Error: {e}", fg='red', bold=True), err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
