#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Streamlit Web Interface for Meeting Action Items Extractor"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import StringIO
import sys

from src.parser import TranscriptParser
from src.action_detector import ActionDetector
from src.summary_generator import SummaryGenerator
from src.exceptions import MeetingExtractorError


# Page configuration
st.set_page_config(
    page_title="Meeting Action Items Extractor",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    .priority-high {
        color: #e74c3c;
        font-weight: bold;
    }
    .priority-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .priority-low {
        color: #2ecc71;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">📋 Meeting Action Items Extractor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automatically extract action items from meeting transcripts</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        meeting_title = st.text_input(
            "Meeting Title",
            value="Meeting",
            help="Title for the meeting summary"
        )
        
        meeting_date = st.date_input(
            "Meeting Date",
            value=datetime.now(),
            help="Date of the meeting"
        )
        
        include_stats = st.checkbox(
            "Include Statistics",
            value=True,
            help="Include statistics in the summary"
        )
        
        include_context = st.checkbox(
            "Include Context",
            value=False,
            help="Include surrounding context for each action item"
        )
        
        st.divider()
        
        st.header("📚 Supported Formats")
        st.markdown("""
        **Zoom:**
        ```
        00:00:15 Sarah Chen: Good morning everyone!
        ```
        
        **Google Meet:**
        ```
        10:00 AM Jennifer Lee: Hi team, welcome!
        ```
        
        **Plain Text:**
        ```
        Lisa Thompson: Welcome everyone!
        ```
        """)
        
        st.divider()
        
        st.markdown("""
        ### 💡 Tips
        - Upload a .txt file with your transcript
        - Action items are detected using keywords like "will", "should", "need to"
        - Deadlines are parsed from phrases like "by Friday", "in 2 days"
        """)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Extract", "📊 Dashboard", "📥 Download"])
    
    with tab1:
        upload_and_extract(meeting_title, meeting_date, include_stats, include_context)
    
    with tab2:
        show_dashboard()
    
    with tab3:
        show_downloads()


def upload_and_extract(meeting_title, meeting_date, include_stats, include_context):
    """Upload and extract action items"""
    
    st.header("Upload Transcript")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a transcript file",
        type=['txt'],
        help="Upload a .txt file containing your meeting transcript"
    )
    
    # Text area for direct input
    st.markdown("**Or paste transcript directly:**")
    transcript_text = st.text_area(
        "Transcript",
        height=200,
        placeholder="Paste your meeting transcript here...",
        label_visibility="collapsed"
    )
    
    # Process button
    if st.button("🎯 Extract Action Items", type="primary", use_container_width=True):
        
        # Get content
        content = None
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
        elif transcript_text:
            content = transcript_text
        else:
            st.warning("⚠️ Please upload a file or paste transcript text")
            return
        
        # Process transcript
        with st.spinner("Processing transcript..."):
            try:
                # Parse
                parser = TranscriptParser()
                messages = parser.parse(content)
                
                st.success(f"✅ Parsed {len(messages)} messages")
                
                # Show preview
                with st.expander("📝 Transcript Preview", expanded=False):
                    preview_df = pd.DataFrame(messages[:10])
                    st.dataframe(preview_df, use_container_width=True)
                
                # Extract action items
                detector = ActionDetector()
                action_items = detector.extract_action_items(messages)
                
                if not action_items:
                    st.warning("⚠️ No action items detected in transcript")
                    st.info("""
                    **Tips for better detection:**
                    - Use action keywords: will, should, need to, must
                    - Include deadlines: by Friday, next week, in 2 days
                    - Assign tasks: John will..., @mention should...
                    """)
                    return
                
                st.success(f"✅ Found {len(action_items)} action items")
                
                # Store in session state
                st.session_state['action_items'] = action_items
                st.session_state['messages'] = messages
                st.session_state['meeting_title'] = meeting_title
                st.session_state['meeting_date'] = meeting_date.strftime('%B %d, %Y')
                st.session_state['include_stats'] = include_stats
                st.session_state['include_context'] = include_context
                
                # Display action items
                display_action_items(action_items)
                
            except MeetingExtractorError as e:
                st.error(f"❌ {e.message}")
                if e.suggestion:
                    st.info(f"💡 {e.suggestion}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)


def display_action_items(action_items):
    """Display action items in a table"""
    
    st.header("📋 Extracted Action Items")
    
    # Convert to DataFrame
    items_data = []
    for item in action_items:
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(item.priority, '⚪')
        
        items_data.append({
            'Priority': f"{priority_emoji} {item.priority.capitalize()}",
            'Task': item.task[:100] + '...' if len(item.task) > 100 else item.task,
            'Assignee': item.assignee or 'Unassigned',
            'Deadline': item.deadline or 'No deadline',
            'Speaker': item.speaker,
            'Time': item.timestamp or '-'
        })
    
    df = pd.DataFrame(items_data)
    
    # Display with styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Priority': st.column_config.TextColumn('Priority', width='small'),
            'Task': st.column_config.TextColumn('Task', width='large'),
            'Assignee': st.column_config.TextColumn('Assignee', width='medium'),
            'Deadline': st.column_config.TextColumn('Deadline', width='medium'),
            'Speaker': st.column_config.TextColumn('Speaker', width='medium'),
            'Time': st.column_config.TextColumn('Time', width='small')
        }
    )


def show_dashboard():
    """Show statistics dashboard"""
    
    st.header("📊 Statistics Dashboard")
    
    if 'action_items' not in st.session_state:
        st.info("👆 Upload and extract action items first to see statistics")
        return
    
    action_items = st.session_state['action_items']
    
    if not action_items:
        st.warning("No action items to display")
        return
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(action_items)}</div>
            <div class="stat-label">Total Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        assigned = len([i for i in action_items if i.assignee])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{assigned}</div>
            <div class="stat-label">Assigned</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        with_deadline = len([i for i in action_items if i.deadline])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{with_deadline}</div>
            <div class="stat-label">With Deadlines</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        high_priority = len([i for i in action_items if i.priority == 'high'])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: #e74c3c;">{high_priority}</div>
            <div class="stat-label">High Priority</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Priority Distribution")
        priority_counts = {
            'High': len([i for i in action_items if i.priority == 'high']),
            'Medium': len([i for i in action_items if i.priority == 'medium']),
            'Low': len([i for i in action_items if i.priority == 'low'])
        }
        
        fig_priority = px.pie(
            values=list(priority_counts.values()),
            names=list(priority_counts.keys()),
            color=list(priority_counts.keys()),
            color_discrete_map={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#2ecc71'},
            hole=0.4
        )
        fig_priority.update_traces(textposition='inside', textinfo='percent+label')
        fig_priority.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_priority, use_container_width=True)
    
    with col2:
        st.subheader("👥 Assignee Breakdown")
        assignee_counts = {}
        for item in action_items:
            assignee = item.assignee or 'Unassigned'
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        # Sort by count
        sorted_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)
        
        fig_assignee = px.bar(
            x=[count for _, count in sorted_assignees],
            y=[name for name, _ in sorted_assignees],
            orientation='h',
            color=[count for _, count in sorted_assignees],
            color_continuous_scale='Blues'
        )
        fig_assignee.update_layout(
            showlegend=False,
            xaxis_title="Number of Tasks",
            yaxis_title="Assignee",
            height=300,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_assignee, use_container_width=True)
    
    # Timeline
    st.subheader("📅 Timeline View")
    
    items_with_deadlines = [i for i in action_items if i.deadline]
    
    if items_with_deadlines:
        timeline_data = []
        for item in items_with_deadlines:
            timeline_data.append({
                'Task': item.task[:50] + '...' if len(item.task) > 50 else item.task,
                'Deadline': item.deadline,
                'Assignee': item.assignee or 'Unassigned',
                'Priority': item.priority
            })
        
        df_timeline = pd.DataFrame(timeline_data)
        
        # Try to parse dates for sorting
        try:
            df_timeline['Deadline_Sort'] = pd.to_datetime(df_timeline['Deadline'], errors='coerce')
            df_timeline = df_timeline.sort_values('Deadline_Sort')
        except:
            pass
        
        # Create timeline chart
        fig_timeline = px.scatter(
            df_timeline,
            x='Deadline',
            y='Task',
            color='Priority',
            color_discrete_map={'high': '#e74c3c', 'medium': '#f39c12', 'low': '#2ecc71'},
            hover_data=['Assignee'],
            size_max=15
        )
        fig_timeline.update_traces(marker=dict(size=12))
        fig_timeline.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No items with deadlines to display in timeline")


def show_downloads():
    """Show download options"""
    
    st.header("📥 Download Summary")
    
    if 'action_items' not in st.session_state:
        st.info("👆 Upload and extract action items first to download summaries")
        return
    
    action_items = st.session_state['action_items']
    meeting_title = st.session_state.get('meeting_title', 'Meeting')
    meeting_date = st.session_state.get('meeting_date', datetime.now().strftime('%B %d, %Y'))
    include_stats = st.session_state.get('include_stats', True)
    include_context = st.session_state.get('include_context', False)
    
    generator = SummaryGenerator()
    
    # Generate summaries
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Markdown Format")
        
        try:
            markdown = generator.generate_markdown(
                action_items,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                include_stats=include_stats,
                include_context=include_context
            )
            
            # Preview
            with st.expander("Preview Markdown", expanded=False):
                st.markdown(markdown)
            
            # Download button
            st.download_button(
                label="⬇️ Download Markdown",
                data=markdown,
                file_name=f"{meeting_title.replace(' ', '_')}_summary.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error generating Markdown: {e}")
    
    with col2:
        st.subheader("📊 JSON Format")
        
        try:
            json_str = generator.generate_json(
                action_items,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                include_stats=include_stats
            )
            
            # Preview
            with st.expander("Preview JSON", expanded=False):
                st.json(json_str)
            
            # Download button
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name=f"{meeting_title.replace(' ', '_')}_summary.json",
                mime="application/json",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error generating JSON: {e}")
    
    st.divider()
    
    # Compact summary
    st.subheader("📋 Quick Summary")
    compact = generator.generate_compact_summary(action_items)
    st.info(compact)
    
    # Statistics table
    if action_items:
        st.subheader("📈 Detailed Statistics")
        
        detector = ActionDetector()
        stats = detector.get_statistics(action_items)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Priority Breakdown**")
            priority_df = pd.DataFrame([
                {'Priority': '🔴 High', 'Count': stats['by_priority']['high']},
                {'Priority': '🟡 Medium', 'Count': stats['by_priority']['medium']},
                {'Priority': '🟢 Low', 'Count': stats['by_priority']['low']}
            ])
            st.dataframe(priority_df, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("**Deadline Status**")
            deadline_df = pd.DataFrame([
                {'Status': '📅 With Deadline', 'Count': stats['with_deadline']},
                {'Status': '⏰ No Deadline', 'Count': stats['without_deadline']}
            ])
            st.dataframe(deadline_df, hide_index=True, use_container_width=True)


if __name__ == '__main__':
    main()
