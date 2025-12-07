# Streamlit Web Interface Guide

## Overview

The Meeting Action Items Extractor includes a beautiful web interface built with Streamlit for easy, visual interaction with the tool.

## Quick Start

### Installation

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### Launch the App

```bash
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

## Features

### 1. 📤 Upload & Extract Tab

**File Upload:**
- Drag and drop .txt files
- Or click to browse and select files
- Supports all transcript formats (Zoom, Google Meet, Plain text)

**Direct Input:**
- Paste transcript text directly into the text area
- No file needed for quick testing

**Live Processing:**
- Real-time parsing and extraction
- Progress indicators
- Transcript preview
- Immediate results

**Action Items Display:**
- Beautiful table with all extracted items
- Priority indicators (🔴 High, 🟡 Medium, 🟢 Low)
- Assignee information
- Deadlines
- Speaker and timestamp

### 2. 📊 Dashboard Tab

**Summary Statistics:**
- Total action items count
- Assigned vs unassigned items
- Items with deadlines
- High priority items count

**Priority Distribution:**
- Interactive pie chart
- Color-coded by priority
- Percentage breakdown
- Hover for details

**Assignee Breakdown:**
- Horizontal bar chart
- Sorted by task count
- Shows workload distribution
- Interactive tooltips

**Timeline View:**
- Scatter plot of deadlines
- Color-coded by priority
- Shows task distribution over time
- Hover to see assignee

### 3. 📥 Download Tab

**Markdown Download:**
- Full formatted summary
- Preview before download
- One-click download button
- Includes all sections

**JSON Download:**
- Structured data format
- API-ready format
- Preview JSON structure
- One-click download button

**Quick Summary:**
- Compact overview
- Key statistics
- Copy-friendly format

**Detailed Statistics:**
- Priority breakdown table
- Deadline status table
- Easy to read format

## Sidebar Settings

### Meeting Configuration

**Meeting Title:**
- Set custom meeting name
- Used in summary headers
- Default: "Meeting"

**Meeting Date:**
- Date picker for meeting date
- Default: Today's date
- Used in summary

**Include Statistics:**
- Toggle statistics section
- Default: Enabled
- Affects Markdown output

**Include Context:**
- Toggle context for each item
- Shows surrounding messages
- Default: Disabled

### Supported Formats

Quick reference for transcript formats:
- Zoom format example
- Google Meet format example
- Plain text format example

### Tips Section

Helpful hints for better results:
- File upload instructions
- Action keyword examples
- Deadline format examples

## User Interface

### Layout

```
┌─────────────────────────────────────────────────────┐
│  📋 Meeting Action Items Extractor                  │
│  Automatically extract action items from transcripts│
├─────────────────────────────────────────────────────┤
│ Sidebar          │  Main Content Area               │
│ ┌──────────┐    │  ┌────────────────────────────┐  │
│ │ Settings │    │  │ Upload & Extract Tab       │  │
│ │          │    │  │ - File upload              │  │
│ │ Title    │    │  │ - Text input               │  │
│ │ Date     │    │  │ - Extract button           │  │
│ │ Options  │    │  │ - Results table            │  │
│ │          │    │  └────────────────────────────┘  │
│ │ Formats  │    │  ┌────────────────────────────┐  │
│ │          │    │  │ Dashboard Tab              │  │
│ │ Tips     │    │  │ - Statistics cards         │  │
│ └──────────┘    │  │ - Charts                   │  │
│                 │  │ - Timeline                 │  │
│                 │  └────────────────────────────┘  │
│                 │  ┌────────────────────────────┐  │
│                 │  │ Download Tab               │  │
│                 │  │ - Markdown preview/download│  │
│                 │  │ - JSON preview/download    │  │
│                 │  │ - Statistics               │  │
│                 │  └────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Color Scheme

- **Primary:** Blue (#1f77b4)
- **High Priority:** Red (#e74c3c)
- **Medium Priority:** Orange (#f39c12)
- **Low Priority:** Green (#2ecc71)
- **Background:** Light gray (#f0f2f6)

## Usage Examples

### Example 1: Upload File

1. Click "Browse files" or drag and drop
2. Select your transcript.txt file
3. Click "🎯 Extract Action Items"
4. View results in the table
5. Switch to Dashboard tab for visualizations
6. Download summaries from Download tab

### Example 2: Paste Text

1. Paste transcript in text area
2. Click "🎯 Extract Action Items"
3. View extracted items
4. Explore dashboard
5. Download results

### Example 3: Custom Settings

1. Set meeting title: "Sprint Planning"
2. Select meeting date
3. Enable "Include Context"
4. Upload transcript
5. Extract and download

## Screenshots

### Upload & Extract Tab
```
┌─────────────────────────────────────────┐
│ Upload Transcript                       │
│ ┌─────────────────────────────────────┐ │
│ │ Drag and drop file here             │ │
│ │ or click to browse                  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Or paste transcript directly:           │
│ ┌─────────────────────────────────────┐ │
│ │ [Text area for transcript]          │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [🎯 Extract Action Items]              │
│                                         │
│ ✅ Found 12 action items               │
│                                         │
│ 📋 Extracted Action Items              │
│ ┌─────────────────────────────────────┐ │
│ │ Priority │ Task │ Assignee │ ...    │ │
│ │ 🔴 High  │ ... │ John     │ ...    │ │
│ │ 🟡 Medium│ ... │ Jane     │ ...    │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Dashboard Tab
```
┌─────────────────────────────────────────┐
│ 📊 Statistics Dashboard                 │
│                                         │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐           │
│ │ 12 │ │ 10 │ │  7 │ │  4 │           │
│ │Tot.│ │Asg.│ │Ddl.│ │Hi. │           │
│ └────┘ └────┘ └────┘ └────┘           │
│                                         │
│ ┌──────────────┐ ┌──────────────┐     │
│ │ Priority     │ │ Assignee     │     │
│ │ Distribution │ │ Breakdown    │     │
│ │ [Pie Chart]  │ │ [Bar Chart]  │     │
│ └──────────────┘ └──────────────┘     │
│                                         │
│ 📅 Timeline View                       │
│ ┌─────────────────────────────────────┐ │
│ │ [Scatter plot of deadlines]         │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Download Tab
```
┌─────────────────────────────────────────┐
│ 📥 Download Summary                     │
│                                         │
│ ┌──────────────┐ ┌──────────────┐     │
│ │ 📄 Markdown  │ │ 📊 JSON      │     │
│ │              │ │              │     │
│ │ [Preview]    │ │ [Preview]    │     │
│ │              │ │              │     │
│ │ [⬇️ Download]│ │ [⬇️ Download]│     │
│ └──────────────┘ └──────────────┘     │
│                                         │
│ 📋 Quick Summary                       │
│ 📋 12 items | 🔴 4 high | 👥 10 ...   │
│                                         │
│ 📈 Detailed Statistics                 │
│ [Statistics tables]                     │
└─────────────────────────────────────────┘
```

## Technical Details

### Technology Stack

- **Streamlit:** Web framework
- **Plotly:** Interactive charts
- **Pandas:** Data manipulation
- **Python:** Backend processing

### Performance

- **Fast Processing:** Real-time extraction
- **Responsive UI:** Smooth interactions
- **Efficient Charts:** Interactive visualizations
- **Memory Efficient:** Handles large transcripts

### Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Customization

### Modify Styling

Edit the CSS in `app.py`:

```python
st.markdown("""
<style>
    .main-header {
        /* Your custom styles */
    }
</style>
""", unsafe_allow_html=True)
```

### Add New Charts

Add to the dashboard section:

```python
# Your custom chart
fig = px.bar(...)
st.plotly_chart(fig, use_container_width=True)
```

### Modify Layout

Change the column layout:

```python
col1, col2, col3 = st.columns([2, 1, 1])
```

## Deployment

### Local Deployment

```bash
streamlit run app.py
```

### Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Deploy!

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Build and run:

```bash
docker build -t meeting-extractor .
docker run -p 8501:8501 meeting-extractor
```

## Troubleshooting

### Port Already in Use

```bash
streamlit run app.py --server.port 8502
```

### Module Not Found

```bash
pip install -r requirements.txt
```

### Charts Not Displaying

Clear cache:
```bash
streamlit cache clear
```

### File Upload Issues

- Check file size (default limit: 200MB)
- Verify file encoding (UTF-8)
- Ensure .txt extension

## Tips for Best Experience

### 1. Use Chrome

Chrome provides the best Streamlit experience with full feature support.

### 2. Enable Wide Mode

The app uses wide mode by default for better chart visibility.

### 3. Clear Cache

If experiencing issues, clear the Streamlit cache:
- Press 'C' in the app
- Or restart the server

### 4. Large Files

For very large transcripts:
- Use the CLI instead for better performance
- Or split into smaller files

### 5. Mobile Access

The app is responsive but works best on desktop for full feature access.

## Keyboard Shortcuts

- **R:** Rerun the app
- **C:** Clear cache
- **Ctrl+Enter:** Submit form
- **Esc:** Close sidebar (mobile)

## Advanced Features

### Session State

The app uses Streamlit session state to persist data across tabs:

```python
st.session_state['action_items'] = action_items
```

### Caching

Functions are cached for better performance:

```python
@st.cache_data
def process_transcript(content):
    # Processing logic
    return results
```

### Custom Components

Add custom Streamlit components for enhanced functionality.

## FAQ

### Q: Can I use this offline?

A: Yes, run locally with `streamlit run app.py`

### Q: How do I change the port?

A: Use `streamlit run app.py --server.port 8502`

### Q: Can I customize the theme?

A: Yes, create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Q: Is my data secure?

A: All processing happens locally. No data is sent to external servers.

### Q: Can I add authentication?

A: Yes, use Streamlit's authentication features or deploy with auth proxy.

### Q: How do I share with my team?

A: Deploy to Streamlit Cloud or your own server, then share the URL.

## Support

For issues:
1. Check the console for error messages
2. Clear cache and refresh
3. Restart the Streamlit server
4. Check `meeting_extractor.log`

## Examples

### Example Workflow

1. **Launch:** `streamlit run app.py`
2. **Upload:** Drag transcript file
3. **Configure:** Set meeting title and date
4. **Extract:** Click extract button
5. **Review:** Check action items table
6. **Analyze:** View dashboard charts
7. **Download:** Get Markdown/JSON summaries

### Example Use Cases

**Daily Standup:**
- Quick paste of meeting notes
- Extract action items
- Download and share

**Sprint Planning:**
- Upload full transcript
- Review all action items
- Analyze workload distribution
- Download for documentation

**Client Meeting:**
- Upload transcript
- Extract commitments
- Share summary with team
- Track deadlines

---

**Enjoy the beautiful web interface!** 🎨✨
