# 📋 Meeting Action Items Extractor

> Automatically extract action items, deadlines, and assignees from meeting transcripts

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Problem Statement

After every meeting, someone needs to manually review notes and extract:
- Who is responsible for what
- When tasks are due
- What the priorities are

This tool automates that process, saving hours of manual work and ensuring nothing falls through the cracks.

## ✨ Features

- ✅ **Web Interface** - Beautiful Streamlit app with charts and visualizations
- ✅ **Multiple Format Support** - Zoom, Google Meet, and plain text transcripts
- ✅ **Smart Detection** - Identifies action items using 18+ keywords and patterns
- ✅ **Assignee Extraction** - Automatically detects who's responsible
- ✅ **Deadline Parsing** - Understands 13+ date formats (by Friday, in 2 days, etc.)
- ✅ **Priority Detection** - Categorizes as high/medium/low priority
- ✅ **Beautiful Output** - Markdown with emojis and JSON for APIs
- ✅ **Interactive Dashboard** - Charts, statistics, and timeline views
- ✅ **Email Integration** - Send summaries directly to participants via SMTP
- ✅ **Batch Processing** - Process multiple files at once
- ✅ **Comprehensive Error Handling** - Never crashes, always helpful
- ✅ **Configurable** - Customize keywords, priorities, and output

## 🚀 Quick Start

### Installation

```bash
# Clone or download the project
cd meeting-action-extractor

# Install dependencies
pip install -r requirements.txt
```

### Option 1: Web Interface (Recommended)

```bash
# Launch the Streamlit web app
streamlit run app.py
```

Then open your browser to `http://localhost:8501` for a beautiful visual interface!

### Option 2: Command Line

```bash
# Parse a single transcript
python main.py parse meeting.txt

# Specify output format
python main.py parse meeting.txt --format json

# Save to specific file
python main.py parse meeting.txt --output summary.md

# Process multiple files
python main.py batch transcripts/
```

## 📖 Usage Examples

### Parse Command

```bash
# Basic parsing
python main.py parse sample_transcripts/zoom_meeting.txt

# With custom title and date
python main.py parse meeting.txt --title "Sprint Planning" --date "Dec 7, 2025"

# Include context for each action item
python main.py parse meeting.txt --context

# Exclude statistics
python main.py parse meeting.txt --no-stats

# Quiet mode (minimal output)
python main.py parse meeting.txt --quiet

# Generate both Markdown and JSON
python main.py parse meeting.txt --format both

# Send via email
python main.py parse meeting.txt --email "team@example.com"

# Send with CC and attachment
python main.py parse meeting.txt \
  --email "team@example.com" \
  --email-cc "manager@example.com" \
  --attach-transcript
```

### Batch Command

```bash
# Process all .txt files in a folder
python main.py batch transcripts/

# Recursive processing
python main.py batch meetings/ --recursive

# Custom file pattern
python main.py batch data/ --pattern "*.txt"

# Specify output directory
python main.py batch transcripts/ --output-dir summaries/
```

### Validate Command

```bash
# Check if a transcript can be parsed
python main.py validate meeting.txt
```

### Config Command

```bash
# View current configuration
python main.py config
```

### Test Email Command

```bash
# Test email configuration
python main.py test-email
```

## 📝 Supported Transcript Formats

### Zoom Format
```
00:00:15 Sarah Chen: We need to update the API documentation by Friday
00:00:35 Mike Johnson: I will handle that
```

### Google Meet Format
```
10:00 AM Jennifer Lee: Let's finalize the design mockups by end of week
10:01 AM Rachel Kim: I'll work on that
```

### Plain Text Format
```
Lisa Thompson: Carlos, you should complete the social media calendar by Monday
Carlos Rivera: Sure, I'll have it ready
```

## 📊 Output Examples

### Markdown Output

```markdown
# 📋 Sprint Planning - Action Items

**Date:** December 07, 2025
**Generated:** 2025-12-07 14:30

---

## 📊 Summary Statistics

- **Total Action Items:** 12
- **Assigned:** 10 | **Unassigned:** 2
- **With Deadlines:** 7
- **Priority Breakdown:**
  - 🔴 High: 4
  - 🟡 Medium: 8
  - 🟢 Low: 0

---

## ✅ Action Items

1. 🔴 [ ] Update API documentation by Friday
   - **Assignee:** @Mike Johnson
   - 📅 **Deadline:** 2025-12-12
   - **Priority:** High
   - **Mentioned at:** 00:00:35

2. 🟡 [ ] Review endpoints and add code examples
   - **Assignee:** @Emily Rodriguez
   - 📅 **Deadline:** 2025-12-12
   - **Mentioned at:** 00:01:18
```

### JSON Output

```json
{
  "meeting": {
    "title": "Sprint Planning",
    "date": "2025-12-07",
    "generated_at": "2025-12-07T14:30:00"
  },
  "action_items": [
    {
      "task": "Update API documentation by Friday",
      "assignee": "Mike Johnson",
      "deadline": "2025-12-12",
      "priority": "high",
      "context": "...",
      "speaker": "Mike Johnson",
      "timestamp": "00:00:35"
    }
  ],
  "statistics": {
    "total_items": 12,
    "assigned": 10,
    "by_priority": {"high": 4, "medium": 8, "low": 0}
  }
}
```

## ⚙️ Configuration

Customize behavior via `config.yaml`:

```yaml
# Output settings
output:
  default_format: markdown
  include_stats: true
  include_context: false

# Detection settings
detection:
  custom_action_keywords:
    - "deliverable"
    - "milestone"
  
  priority:
    high_keywords:
      - "urgent"
      - "ASAP"
      - "critical"
```

See `config.yaml` for all available options.

## 🏗️ Project Structure

```
meeting-action-extractor/
├── src/
│   ├── __init__.py
│   ├── parser.py           # Transcript parsing
│   ├── action_detector.py  # Action item extraction
│   ├── summary_generator.py # Output generation
│   └── exceptions.py       # Custom exceptions
├── sample_transcripts/
│   ├── zoom_meeting.txt
│   ├── google_meet.txt
│   └── plain_meeting.txt
├── main.py                 # CLI interface
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
├── test_parser.py          # Test suite
├── README.md               # This file
└── ERROR_HANDLING.md       # Error handling docs
```

## 🧪 Testing

Run the test suite:

```bash
python test_parser.py
```

Tests include:
- Parsing all three transcript formats
- Action item extraction
- Error handling
- Statistics validation

## 🛠️ Troubleshooting

### No action items detected

**Solution:** Ensure your transcript contains action keywords:
- will, should, need to, must
- action item, TODO, task
- follow up, deadline, by [date]

### File encoding error

**Solution:** Save your transcript as UTF-8:
- In Notepad: Save As → Encoding: UTF-8
- In VS Code: Bottom right → Select Encoding → UTF-8

### Malformed transcript

**Solution:** Check format:
- Zoom: `00:00:00 Name: Message`
- Google Meet: `10:30 AM Name: Message`
- Plain: `Name: Message`

### Permission denied

**Solution:** Check file/folder permissions:
```bash
chmod 755 output_folder/
```

For more troubleshooting, see `ERROR_HANDLING.md`.

## 📚 Documentation

- **README.md** - This file (user guide)
- **STREAMLIT_APP.md** - Web interface guide
- **EMAIL_SETUP.md** - Email configuration and usage guide
- **ERROR_HANDLING.md** - Comprehensive error handling documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **config.yaml** - Configuration options with comments
- **.env.example** - Email credentials template

## 🎓 How It Works

1. **Parse** - Reads transcript and identifies speakers, timestamps, messages
2. **Detect** - Scans for action keywords, assignees, deadlines, priorities
3. **Extract** - Creates structured ActionItem objects
4. **Generate** - Formats as Markdown or JSON
5. **Save** - Writes to file with proper formatting

## 🚦 Error Handling

The tool includes comprehensive error handling:

- ❌ **File not found** → Suggests checking path
- ❌ **Empty transcript** → Suggests adding content
- ❌ **Malformed format** → Shows supported formats
- ❌ **No action items** → Lists required keywords
- ❌ **Encoding error** → Suggests UTF-8 encoding

All errors include helpful suggestions for resolution.

## 🔍 Advanced Features

### Email Integration

Send summaries directly to meeting participants:

```bash
# Setup (one-time)
cp .env.example .env
# Edit .env with your SMTP credentials

# Test configuration
python main.py test-email

# Send email
python main.py parse meeting.txt --email "team@example.com"
```

See **EMAIL_SETUP.md** for detailed configuration guide.

### Context Inclusion

```bash
python main.py parse meeting.txt --context
```

Includes surrounding messages for each action item.

### Statistics

```bash
python main.py parse meeting.txt
```

Automatically includes:
- Total action items
- Items by assignee
- Items by priority
- Deadline statistics

### Batch Processing

```bash
python main.py batch transcripts/ --recursive
```

Processes all files, continues on errors, shows summary.

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional transcript formats (Microsoft Teams, Slack)
- [ ] NLP-based action detection
- [ ] Web interface
- [ ] Email integration
- [ ] Calendar integration
- [ ] Multi-language support

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - CLI framework
- [python-dateutil](https://dateutil.readthedocs.io/) - Date parsing
- [PyYAML](https://pyyaml.org/) - Configuration

## 📞 Support

- **Issues:** Check ERROR_HANDLING.md first
- **Logs:** See `meeting_extractor.log`
- **Validation:** Run `python main.py validate your_file.txt`

---

**Made with ❤️ to save you time after meetings**
