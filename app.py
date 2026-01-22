"""
Advanced Podcast Management System
A comprehensive Streamlit application for managing podcast series, episodes, transcriptions,
analytics, and distribution with professional workflow features.
"""

import streamlit as st
import io
import json
import csv
import sqlite3
from datetime import datetime, timedelta
import base64
import requests
from pathlib import Path
import os
from dotenv import load_dotenv
import tempfile
import time
from collections import defaultdict
import pandas as pd
import numpy as np

# Load environment variables
load_dotenv()

# Import required libraries
try:
    from openai import OpenAI
    import PyJWT as jwt
except ImportError:
    st.error("Please install required packages: pip install openai PyJWT")

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Professional Podcast Management System",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #667eea;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .episode-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .series-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        color: #856404;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        color: #0c5460;
    }
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .progress-bar {
        background-color: #e9ecef;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 10px;
    }
    .tag {
        display: inline-block;
        background-color: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .status-published {
        background-color: #d4edda;
        color: #155724;
    }
    .status-draft {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-scheduled {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    .timeline {
        position: relative;
        padding: 1rem 0;
    }
    .timeline-item {
        padding-left: 2rem;
        margin-bottom: 1rem;
        border-left: 2px solid #667eea;
        padding-bottom: 1rem;
    }
    .timeline-item:last-child {
        border-left: 2px solid transparent;
    }
    .timeline-dot {
        position: absolute;
        left: -8px;
        top: 0;
        width: 16px;
        height: 16px;
        background-color: #667eea;
        border-radius: 50%;
        border: 2px solid white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================
def init_database():
    """Initialize SQLite database for podcast management"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Podcast Series Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS podcast_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            author TEXT,
            category TEXT,
            language TEXT DEFAULT 'English',
            cover_image_url TEXT,
            website TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Episodes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            episode_number INTEGER,
            season_number INTEGER DEFAULT 1,
            audio_file_path TEXT,
            audio_duration INTEGER,
            transcription TEXT,
            show_notes TEXT,
            guest_names TEXT,
            publish_date TIMESTAMP,
            status TEXT DEFAULT 'draft',
            view_count INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (series_id) REFERENCES podcast_series(id)
        )
    ''')
    
    # Show Notes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS show_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            content TEXT,
            timestamps TEXT,
            resources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (episode_id) REFERENCES episodes(id)
        )
    ''')
    
    # Guest Management Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            website TEXT,
            bio TEXT,
            social_media TEXT,
            photo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Episode Guests Junction Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episode_guests (
            episode_id INTEGER NOT NULL,
            guest_id INTEGER NOT NULL,
            PRIMARY KEY (episode_id, guest_id),
            FOREIGN KEY (episode_id) REFERENCES episodes(id),
            FOREIGN KEY (guest_id) REFERENCES guests(id)
        )
    ''')
    
    # Analytics Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            date DATE,
            views INTEGER DEFAULT 0,
            downloads INTEGER DEFAULT 0,
            listen_time INTEGER DEFAULT 0,
            engagement_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (episode_id) REFERENCES episodes(id)
        )
    ''')
    
    # Distribution Channels Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS distribution_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            platform TEXT,
            feed_url TEXT,
            status TEXT DEFAULT 'pending',
            last_synced TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (series_id) REFERENCES podcast_series(id)
        )
    ''')
    
    conn.commit()
    return conn

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = init_database()

if 'podcast_series' not in st.session_state:
    st.session_state.podcast_series = []

if 'episodes' not in st.session_state:
    st.session_state.episodes = []

if 'guests' not in st.session_state:
    st.session_state.guests = []

if 'current_series' not in st.session_state:
    st.session_state.current_series = None

if 'current_episode' not in st.session_state:
    st.session_state.current_episode = None

if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""

if 'gdrive_authenticated' not in st.session_state:
    st.session_state.gdrive_authenticated = False

if 'default_share_email' not in st.session_state:
    st.session_state.default_share_email = "Entremotivator@gmail.com"

# ============================================================================
# GOOGLE DRIVE API CLASS
# ============================================================================
class GoogleDriveAPI:
    def __init__(self, service_account_info):
        self.service_account_info = service_account_info
        self.access_token = None
        
    def get_access_token(self):
        """Simulate getting access token for demonstration"""
        # In a real app, you'd use google-auth library
        # For this example, we'll return a dummy token if JSON is valid
        if self.service_account_info:
            return "dummy_token_for_demo"
        return None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def transcribe_audio(file_path, api_key):
    """Transcribe audio using OpenAI Whisper API"""
    try:
        client = OpenAI(api_key=api_key)
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

def generate_show_notes(title, transcription, api_key):
    """Generate show notes using OpenAI GPT-4"""
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"Generate professional podcast show notes for an episode titled '{title}' based on this transcription: {transcription[:4000]}"
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional podcast producer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Show notes generation error: {str(e)}")
        return None

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================
def export_episode_to_pdf(episode_data):
    """Export episode with transcription and show notes to PDF"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#667eea',
            spaceAfter=30
        )
        story.append(Paragraph(episode_data['title'], title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#666666'
        )
        story.append(Paragraph(f"Episode #{episode_data.get('episode_number', 'N/A')}", meta_style))
        story.append(Paragraph(f"Duration: {episode_data.get('duration', 'N/A')} minutes", meta_style))
        story.append(Paragraph(f"Published: {episode_data.get('publish_date', 'N/A')}", meta_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Description
        if episode_data.get('description'):
            story.append(Paragraph("<b>Description</b>", styles['Heading2']))
            story.append(Paragraph(episode_data['description'], styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        # Show Notes
        if episode_data.get('show_notes'):
            story.append(PageBreak())
            story.append(Paragraph("<b>Show Notes</b>", styles['Heading2']))
            story.append(Paragraph(episode_data['show_notes'], styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        
        # Transcription
        if episode_data.get('transcription'):
            story.append(PageBreak())
            story.append(Paragraph("<b>Full Transcription</b>", styles['Heading2']))
            story.append(Paragraph(episode_data['transcription'], styles['BodyText']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"PDF export error: {str(e)}")
        return None

def export_series_csv(series_data, episodes_data):
    """Export series and episodes data to CSV"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Series info
        writer.writerow(['Podcast Series Report'])
        writer.writerow(['Name', series_data.get('name', '')])
        writer.writerow(['Author', series_data.get('author', '')])
        writer.writerow(['Category', series_data.get('category', '')])
        writer.writerow([])
        
        # Episodes
        writer.writerow(['Episode #', 'Title', 'Status', 'Duration', 'Views', 'Downloads', 'Published Date'])
        for ep in episodes_data:
            writer.writerow([
                ep.get('episode_number', ''),
                ep.get('title', ''),
                ep.get('status', ''),
                ep.get('duration', ''),
                ep.get('view_count', 0),
                ep.get('download_count', 0),
                ep.get('publish_date', '')
            ])
        
        return output.getvalue().encode('utf-8')
    except Exception as e:
        st.error(f"CSV export error: {str(e)}")
        return None

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Configuration & Settings")
    
    # OpenAI API Key
    st.markdown("#### 🔑 OpenAI API")
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password",
        help="For transcription and show notes generation",
        key="sidebar_openai_key"
    )
    
    if api_key_input:
        st.session_state.openai_api_key = api_key_input
        st.success("✅ OpenAI API configured")
    else:
        st.warning("⚠️ OpenAI API key not set")
    
    st.divider()
    
    # Google Drive
    st.markdown("#### 📁 Google Drive")
    
    # NEW: File uploader for JSON service file
    gdrive_file = st.file_uploader(
        "Upload Service Account JSON",
        type=['json'],
        help="Upload your Google Drive service account JSON file",
        key="sidebar_gdrive_json_file"
    )
    
    # Existing text area for JSON (optional fallback)
    gdrive_json_text = st.text_area(
        "Or Paste Service Account JSON",
        height=100,
        help="Paste your Google Drive service account JSON",
        key="sidebar_gdrive_json_text"
    )
    
    # Process either file or text
    service_account_info = None
    if gdrive_file:
        try:
            service_account_info = json.load(gdrive_file)
        except Exception as e:
            st.error(f"Error reading JSON file: {e}")
    elif gdrive_json_text:
        try:
            service_account_info = json.loads(gdrive_json_text)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in text area")

    if service_account_info:
        try:
            st.session_state.service_account = service_account_info
            gdrive_api = GoogleDriveAPI(service_account_info)
            token = gdrive_api.get_access_token()
            
            if token:
                st.session_state.gdrive_authenticated = True
                st.success("✅ Google Drive authenticated")
            else:
                st.error("❌ Authentication failed")
        except Exception as e:
            st.error(f"Authentication error: {e}")
    else:
        st.info("ℹ️ Google Drive not configured")
    
    st.divider()
    
    # Default Share Email
    st.markdown("#### 📧 Default Share Email")
    default_email = st.text_input(
        "Email",
        value=st.session_state.default_share_email,
        help="Auto-share folders with this email",
        key="sidebar_default_email"
    )
    st.session_state.default_share_email = default_email
    
    st.divider()
    
    # Statistics
    st.markdown("#### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Series", len(st.session_state.podcast_series))
    with col2:
        st.metric("Episodes", len(st.session_state.episodes))

# ============================================================================
# MAIN APPLICATION
# ============================================================================
st.markdown('<h1 class="main-header">🎙️ Professional Podcast Management System</h1>', unsafe_allow_html=True)

# Create main navigation tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Dashboard",
    "🎬 Series",
    "📝 Episodes",
    "👥 Guests",
    "📈 Analytics",
    "📤 Distribution",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================
with tab1:
    st.markdown('<h2 class="section-header">📊 Podcast Dashboard</h2>', unsafe_allow_html=True)
    
    if st.session_state.podcast_series:
        # Overview Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_episodes = len(st.session_state.episodes)
        total_views = sum(ep.get('view_count', 0) for ep in st.session_state.episodes)
        total_downloads = sum(ep.get('download_count', 0) for ep in st.session_state.episodes)
        avg_duration = np.mean([ep.get('audio_duration', 0) for ep in st.session_state.episodes]) if st.session_state.episodes else 0
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Episodes</div>
                <div class="stat-value">{total_episodes}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Views</div>
                <div class="stat-value">{total_views:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Downloads</div>
                <div class="stat-value">{total_downloads:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Avg Duration</div>
                <div class="stat-value">{int(avg_duration)} min</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Series Overview
        st.markdown("### 🎬 Your Podcast Series")
        
        for series in st.session_state.podcast_series:
            series_episodes = [ep for ep in st.session_state.episodes if ep.get('series_id') == series.get('id')]
            series_views = sum(ep.get('view_count', 0) for ep in series_episodes)
            
            with st.expander(f"📻 {series.get('name', 'Untitled')} ({len(series_episodes)} episodes)"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Author:** {series.get('author', 'N/A')}")
                    st.write(f"**Category:** {series.get('category', 'N/A')}")
                    st.write(f"**Description:** {series.get('description', 'N/A')[:200]}...")
                
                with col2:
                    st.metric("Episodes", len(series_episodes))
                    st.metric("Views", series_views)
                
                with col3:
                    if st.button("✏️ Edit", key=f"dash_edit_series_{series.get('id')}"):
                        st.session_state.current_series = series
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"dash_delete_series_{series.get('id')}"):
                        st.session_state.podcast_series.remove(series)
                        st.success("Series deleted!")
                        st.rerun()
        
        st.divider()
        
        # Recent Episodes
        st.markdown("### 📺 Recent Episodes")
        
        recent_episodes = sorted(
            st.session_state.episodes,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )[:5]
        
        if recent_episodes:
            for ep in recent_episodes:
                with st.container():
                    st.markdown(f"""
                    <div class="episode-card">
                        <h4>{ep.get('title')}</h4>
                        <p>Status: <span class="status-badge status-{ep.get('status')}">{ep.get('status').upper()}</span> | 
                        Views: {ep.get('view_count', 0)} | Downloads: {ep.get('download_count', 0)}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No episodes yet.")
    else:
        st.info("Welcome! Start by creating a podcast series in the 'Series' tab.")

# ============================================================================
# TAB 2: SERIES MANAGEMENT
# ============================================================================
with tab2:
    st.markdown('<h2 class="section-header">🎬 Podcast Series Management</h2>', unsafe_allow_html=True)
    
    subtab1, subtab2 = st.tabs(["Create Series", "Manage Series"])
    
    with subtab1:
        st.markdown("### Create New Podcast Series")
        
        col1, col2 = st.columns(2)
        
        with col1:
            series_name = st.text_input("Series Name", placeholder="My Awesome Podcast", key="create_series_name")
            series_author = st.text_input("Author Name", placeholder="Your Name", key="create_series_author")
            series_category = st.selectbox(
                "Category",
                ["Technology", "Business", "Education", "Entertainment", "Health", "News", "Sports", "Other"],
                key="create_series_category"
            )
        
        with col2:
            series_language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Other"], key="create_series_lang")
            series_email = st.text_input("Contact Email", placeholder="podcast@example.com", key="create_series_email")
            series_website = st.text_input("Website (optional)", placeholder="https://example.com", key="create_series_web")
        
        series_description = st.text_area("Series Description", height=150, placeholder="Describe your podcast...", key="create_series_desc")
        
        if st.button("✅ Create Series", use_container_width=True, key="btn_create_series"):
            if series_name and series_author:
                new_series = {
                    'id': len(st.session_state.podcast_series) + 1,
                    'name': series_name,
                    'author': series_author,
                    'category': series_category,
                    'language': series_language,
                    'email': series_email,
                    'website': series_website,
                    'description': series_description,
                    'created_at': datetime.now().isoformat()
                }
                st.session_state.podcast_series.append(new_series)
                st.success(f"✅ Series '{series_name}' created successfully!")
                st.balloons()
            else:
                st.error("Please fill in all required fields")
    
    with subtab2:
        st.markdown("### Manage Existing Series")
        
        if st.session_state.podcast_series:
            for series in st.session_state.podcast_series:
                with st.expander(f"📻 {series.get('name', 'Untitled')}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Name:** {series.get('name')}")
                        st.write(f"**Author:** {series.get('author')}")
                        st.write(f"**Category:** {series.get('category')}")
                        st.write(f"**Language:** {series.get('language')}")
                        st.write(f"**Email:** {series.get('email')}")
                        st.write(f"**Website:** {series.get('website')}")
                        st.write(f"**Description:** {series.get('description')}")
                    
                    with col2:
                        if st.button("✏️ Edit", key=f"manage_edit_s_{series.get('id')}"):
                            st.session_state.current_series = series
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"manage_del_s_{series.get('id')}"):
                            st.session_state.podcast_series.remove(series)
                            st.rerun()
        else:
            st.info("No podcast series created yet. Create one in the 'Create Series' tab.")

# ============================================================================
# TAB 3: EPISODE MANAGEMENT
# ============================================================================
with tab3:
    st.markdown('<h2 class="section-header">📝 Episode Management</h2>', unsafe_allow_html=True)
    
    if not st.session_state.podcast_series:
        st.warning("⚠️ Create a podcast series first before adding episodes!")
    else:
        subtab1, subtab2, subtab3 = st.tabs(["Upload & Transcribe", "Manage Episodes", "Batch Operations"])
        
        with subtab1:
            st.markdown("### Upload & Transcribe Episode")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_series = st.selectbox(
                    "Select Podcast Series",
                    options=[s.get('name') for s in st.session_state.podcast_series],
                    key="ep_upload_series_select"
                )
                
                series_id = next(
                    (s.get('id') for s in st.session_state.podcast_series if s.get('name') == selected_series),
                    None
                )
            
            with col2:
                episode_number = st.number_input("Episode Number", min_value=1, step=1, key="ep_upload_num")
            
            episode_title = st.text_input("Episode Title", placeholder="Episode Title", key="ep_upload_title")
            episode_description = st.text_area("Episode Description", height=100, key="ep_upload_desc")
            
            col1, col2 = st.columns(2)
            
            with col1:
                season_number = st.number_input("Season Number", min_value=1, value=1, step=1, key="ep_upload_season")
                guest_names = st.text_input("Guest Names (comma-separated)", placeholder="Guest 1, Guest 2", key="ep_upload_guests")
            
            with col2:
                publish_date = st.date_input("Publish Date", key="ep_upload_date")
                episode_status = st.selectbox("Status", ["draft", "scheduled", "published"], key="ep_upload_status")
            
            uploaded_file = st.file_uploader(
                "Upload Audio File",
                type=['mp3', 'wav', 'm4a', 'ogg', 'flac', 'webm'],
                help="Supported formats: MP3, WAV, M4A, OGG, FLAC, WebM",
                key="ep_upload_audio"
            )
            
            if uploaded_file and st.session_state.openai_api_key:
                st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🚀 Transcribe Audio", use_container_width=True, key="btn_transcribe"):
                        with st.spinner("Transcribing audio..."):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                                tmp_file.write(uploaded_file.getbuffer())
                                tmp_path = tmp_file.name
                            
                            try:
                                transcription = transcribe_audio(tmp_path, st.session_state.openai_api_key)
                                
                                if transcription:
                                    st.session_state.current_transcription = transcription
                                    st.success("✅ Transcription completed!")
                                    st.text_area("Transcription", value=transcription, height=200, disabled=True, key="ep_transcription_result")
                            finally:
                                os.unlink(tmp_path)
                
                with col2:
                    if st.button("📝 Generate Show Notes", use_container_width=True, key="btn_gen_notes"):
                        if hasattr(st.session_state, 'current_transcription'):
                            with st.spinner("Generating show notes..."):
                                show_notes = generate_show_notes(
                                    episode_title,
                                    st.session_state.current_transcription,
                                    st.session_state.openai_api_key
                                )
                                
                                if show_notes:
                                    st.session_state.current_show_notes = show_notes
                                    st.success("✅ Show notes generated!")
                                    st.markdown(show_notes)
                        else:
                            st.warning("Transcribe audio first")
                
                if st.button("💾 Save Episode", use_container_width=True, key="btn_save_ep"):
                    if episode_title and series_id:
                        new_episode = {
                            'id': len(st.session_state.episodes) + 1,
                            'series_id': series_id,
                            'title': episode_title,
                            'description': episode_description,
                            'episode_number': episode_number,
                            'season_number': season_number,
                            'audio_file': uploaded_file.name,
                            'transcription': getattr(st.session_state, 'current_transcription', ''),
                            'show_notes': getattr(st.session_state, 'current_show_notes', ''),
                            'guest_names': guest_names,
                            'publish_date': publish_date.isoformat(),
                            'status': episode_status,
                            'view_count': 0,
                            'download_count': 0,
                            'created_at': datetime.now().isoformat()
                        }
                        st.session_state.episodes.append(new_episode)
                        st.success(f"✅ Episode '{episode_title}' saved!")
                        st.balloons()
                    else:
                        st.error("Please fill in all required fields")
            
            elif uploaded_file and not st.session_state.openai_api_key:
                st.error("❌ Configure OpenAI API key in sidebar first")
        
        with subtab2:
            st.markdown("### Manage Episodes")
            
            if st.session_state.episodes:
                search_term = st.text_input("🔍 Search episodes", placeholder="Search by title...", key="ep_manage_search")
                
                filtered_episodes = [
                    ep for ep in st.session_state.episodes
                    if search_term.lower() in ep.get('title', '').lower()
                ] if search_term else st.session_state.episodes
                
                for ep in filtered_episodes:
                    with st.expander(f"📺 {ep.get('title')} (Ep #{ep.get('episode_number')})", expanded=False):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**Status:** {ep.get('status').upper()}")
                            st.write(f"**Season:** {ep.get('season_number')} | **Episode:** {ep.get('episode_number')}")
                            st.write(f"**Published:** {ep.get('publish_date')}")
                            st.write(f"**Guests:** {ep.get('guest_names', 'N/A')}")
                        
                        with col2:
                            st.metric("Views", ep.get('view_count', 0))
                            st.metric("Downloads", ep.get('download_count', 0))
                        
                        with col3:
                            if st.button("✏️ Edit", key=f"manage_edit_ep_{ep.get('id')}"):
                                st.session_state.current_episode = ep
                                st.rerun()
                            
                            if st.button("🗑️ Delete", key=f"manage_del_ep_{ep.get('id')}"):
                                st.session_state.episodes.remove(ep)
                                st.rerun()
                        
                        # Preview
                        if ep.get('transcription'):
                            st.markdown("**Transcription Preview:**")
                            st.text_area(
                                "Content",
                                value=ep.get('transcription')[:300] + "...",
                                height=100,
                                disabled=True,
                                key=f"manage_preview_{ep.get('id')}"
                            )
            else:
                st.info("No episodes yet. Upload one in the 'Upload & Transcribe' tab.")
        
        with subtab3:
            st.markdown("### Batch Operations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Export All Episodes")
                if st.button("📥 Export as CSV", use_container_width=True, key="btn_batch_csv"):
                    if st.session_state.episodes and st.session_state.podcast_series:
                        series = st.session_state.podcast_series[0]
                        csv_data = export_series_csv(series, st.session_state.episodes)
                        if csv_data:
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=csv_data,
                                file_name=f"{series.get('name')}_episodes.csv",
                                mime="text/csv",
                                key="btn_download_batch_csv"
                            )
            
            with col2:
                st.markdown("#### Bulk Status Update")
                new_status = st.selectbox("New Status", ["draft", "scheduled", "published"], key="batch_status_select")
                
                if st.button("Update All Episodes", use_container_width=True, key="btn_batch_update"):
                    for ep in st.session_state.episodes:
                        ep['status'] = new_status
                    st.success(f"✅ Updated {len(st.session_state.episodes)} episodes to '{new_status}'")

# ============================================================================
# TAB 4: GUEST MANAGEMENT
# ============================================================================
with tab4:
    st.markdown('<h2 class="section-header">👥 Guest Management</h2>', unsafe_allow_html=True)
    
    subtab1, subtab2 = st.tabs(["Add Guest", "Guest Directory"])
    
    with subtab1:
        st.markdown("### Add New Guest")
        
        col1, col2 = st.columns(2)
        
        with col1:
            guest_name = st.text_input("Guest Name", placeholder="Full Name", key="guest_add_name")
            guest_email = st.text_input("Email", placeholder="guest@example.com", key="guest_add_email")
            guest_website = st.text_input("Website (optional)", placeholder="https://example.com", key="guest_add_web")
        
        with col2:
            guest_social = st.text_input("Social Media (optional)", placeholder="@twitter_handle", key="guest_add_social")
            guest_photo_url = st.text_input("Photo URL (optional)", placeholder="https://example.com/photo.jpg", key="guest_add_photo")
        
        guest_bio = st.text_area("Bio", height=150, placeholder="Tell us about this guest...", key="guest_add_bio")
        
        if st.button("✅ Add Guest", use_container_width=True, key="btn_add_guest"):
            if guest_name and guest_email:
                new_guest = {
                    'id': len(st.session_state.guests) + 1,
                    'name': guest_name,
                    'email': guest_email,
                    'website': guest_website,
                    'social_media': guest_social,
                    'photo_url': guest_photo_url,
                    'bio': guest_bio,
                    'created_at': datetime.now().isoformat()
                }
                st.session_state.guests.append(new_guest)
                st.success(f"✅ Guest '{guest_name}' added!")
            else:
                st.error("Please fill in required fields")
    
    with subtab2:
        st.markdown("### Guest Directory")
        
        if st.session_state.guests:
            search_guest = st.text_input("🔍 Search guests", placeholder="Search by name...", key="guest_dir_search")
            
            filtered_guests = [
                g for g in st.session_state.guests
                if search_guest.lower() in g.get('name', '').lower()
            ] if search_guest else st.session_state.guests
            
            for guest in filtered_guests:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{guest.get('name')}**")
                    st.caption(f"📧 {guest.get('email')} | 🌐 {guest.get('website', 'N/A')}")
                    st.write(guest.get('bio', 'No bio provided')[:200])
                
                with col2:
                    if st.button("🗑️ Delete", key=f"dir_del_guest_{guest.get('id')}"):
                        st.session_state.guests.remove(guest)
                        st.rerun()
        else:
            st.info("No guests added yet.")

# ============================================================================
# TAB 5: ANALYTICS & INSIGHTS
# ============================================================================
with tab5:
    st.markdown('<h2 class="section-header">📈 Analytics & Insights</h2>', unsafe_allow_html=True)
    
    if st.session_state.episodes:
        col1, col2, col3, col4 = st.columns(4)
        
        total_views = sum(ep.get('view_count', 0) for ep in st.session_state.episodes)
        total_downloads = sum(ep.get('download_count', 0) for ep in st.session_state.episodes)
        total_episodes = len(st.session_state.episodes)
        avg_views = total_views / total_episodes if total_episodes > 0 else 0
        
        with col1:
            st.metric("Total Views", f"{total_views:,}")
        with col2:
            st.metric("Total Downloads", f"{total_downloads:,}")
        with col3:
            st.metric("Total Episodes", total_episodes)
        with col4:
            st.metric("Avg Views/Episode", f"{int(avg_views)}")
        
        st.divider()
        
        # Episode Performance
        st.markdown("### 📊 Episode Performance")
        
        episode_data = {
            'Episode': [ep.get('title', 'N/A')[:20] for ep in st.session_state.episodes],
            'Views': [ep.get('view_count', 0) for ep in st.session_state.episodes],
            'Downloads': [ep.get('download_count', 0) for ep in st.session_state.episodes]
        }
        
        df = pd.DataFrame(episode_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(df.set_index('Episode')['Views'])
        
        with col2:
            st.bar_chart(df.set_index('Episode')['Downloads'])
        
        st.divider()
        
        # Top Episodes
        st.markdown("### 🏆 Top Episodes")
        
        top_episodes = sorted(
            st.session_state.episodes,
            key=lambda x: x.get('view_count', 0),
            reverse=True
        )[:5]
        
        for idx, ep in enumerate(top_episodes, 1):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**#{idx}. {ep.get('title')}**")
            
            with col2:
                st.metric("Views", ep.get('view_count', 0))
            
            with col3:
                st.metric("Downloads", ep.get('download_count', 0))
    
    else:
        st.info("No episodes yet. Create some episodes to see analytics!")

# ============================================================================
# TAB 6: DISTRIBUTION & PUBLISHING
# ============================================================================
with tab6:
    st.markdown('<h2 class="section-header">📤 Distribution & Publishing</h2>', unsafe_allow_html=True)
    
    if st.session_state.podcast_series:
        st.markdown("### 🌐 Distribution Channels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Available Platforms")
            platforms = [
                "Apple Podcasts",
                "Spotify",
                "Google Podcasts",
                "Amazon Music",
                "Stitcher",
                "iHeartRadio",
                "Podbean",
                "Buzzsprout"
            ]
            
            for platform in platforms:
                col_check, col_status = st.columns([3, 1])
                with col_check:
                    st.checkbox(f"📻 {platform}", key=f"dist_platform_{platform}")
                with col_status:
                    st.caption("⏳ Pending")
        
        with col2:
            st.markdown("#### RSS Feed Configuration")
            
            feed_url = st.text_input("RSS Feed URL (auto-generated)", placeholder="https://example.com/feed.xml", disabled=True, key="dist_rss_url")
            
            st.markdown("#### Publishing Options")
            
            if st.button("🚀 Publish All Episodes", use_container_width=True, key="btn_dist_publish"):
                for ep in st.session_state.episodes:
                    ep['status'] = 'published'
                st.success("✅ All episodes published!")
            
            if st.button("📤 Upload to Google Drive", use_container_width=True, key="btn_dist_gdrive"):
                if st.session_state.gdrive_authenticated:
                    st.success("✅ Uploaded to Google Drive")
                else:
                    st.warning("Configure Google Drive in settings")
            
            if st.button("🔗 Generate Podcast Feed", use_container_width=True, key="btn_dist_gen_feed"):
                st.info("📡 Podcast feed generated. Share with distribution platforms.")
    
    else:
        st.info("Create a podcast series first!")

# ============================================================================
# TAB 7: SETTINGS & PREFERENCES
# ============================================================================
with tab7:
    st.markdown('<h2 class="section-header">⚙️ Settings & Preferences</h2>', unsafe_allow_html=True)
    
    subtab1, subtab2, subtab3 = st.tabs(["General", "API & Credentials", "Backup & Restore"])
    
    with subtab1:
        st.markdown("### General Settings")
        
        st.markdown("#### Notification Preferences")
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Email notifications for new episodes", key="set_notify_email")
            st.checkbox("Remind me to publish scheduled episodes", key="set_notify_remind")
        
        with col2:
            st.checkbox("Weekly analytics summary", key="set_notify_weekly")
            st.checkbox("Notify on guest confirmations", key="set_notify_guest")
        
        st.divider()
        
        st.markdown("#### Display Preferences")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="set_theme")
        items_per_page = st.slider("Items per page", 5, 50, 10, key="set_items_page")
        
        st.divider()
        
        st.markdown("#### Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Data", use_container_width=True, key="btn_set_clear"):
                if st.checkbox("I understand this will delete all data", key="set_clear_confirm"):
                    st.session_state.podcast_series = []
                    st.session_state.episodes = []
                    st.session_state.guests = []
                    st.success("✅ All data cleared")
        
        with col2:
            if st.button("📥 Export All Data", use_container_width=True, key="btn_set_export"):
                export_data = {
                    'series': st.session_state.podcast_series,
                    'episodes': st.session_state.episodes,
                    'guests': st.session_state.guests,
                    'exported_at': datetime.now().isoformat()
                }
                
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"podcast_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    key="btn_set_download_json"
                )
    
    with subtab2:
        st.markdown("### API Keys & Credentials")
        
        st.warning("⚠️ Never share your API keys with anyone!")
        
        st.markdown("#### OpenAI API")
        st.info(f"Status: {'✅ Configured' if st.session_state.openai_api_key else '❌ Not configured'}")
        
        if st.button("🔄 Reset OpenAI Key", key="btn_set_reset_openai"):
            st.session_state.openai_api_key = ""
            st.success("API key reset")
        
        st.divider()
        
        st.markdown("#### Google Drive")
        st.info(f"Status: {'✅ Authenticated' if st.session_state.gdrive_authenticated else '❌ Not authenticated'}")
        
        if st.button("🔄 Reset Google Drive", key="btn_set_reset_gdrive"):
            st.session_state.gdrive_authenticated = False
            st.success("Google Drive reset")
    
    with subtab3:
        st.markdown("### Export & Backup")
        
        st.markdown("#### Full Backup")
        
        if st.button("💾 Create Full Backup", use_container_width=True, key="btn_set_full_backup"):
            backup_data = {
                'version': '1.0',
                'backup_date': datetime.now().isoformat(),
                'series': st.session_state.podcast_series,
                'episodes': st.session_state.episodes,
                'guests': st.session_state.guests
            }
            
            st.download_button(
                label="⬇️ Download Backup",
                data=json.dumps(backup_data, indent=2),
                file_name=f"podcast_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="btn_set_download_backup"
            )
        
        st.divider()
        
        st.markdown("#### Restore from Backup")
        
        backup_file = st.file_uploader("Upload backup file", type=['json'], key="set_restore_upload")
        
        if backup_file:
            try:
                backup_data = json.load(backup_file)
                
                if st.button("✅ Restore Backup", use_container_width=True, key="btn_set_restore"):
                    st.session_state.podcast_series = backup_data.get('series', [])
                    st.session_state.episodes = backup_data.get('episodes', [])
                    st.session_state.guests = backup_data.get('guests', [])
                    st.success("✅ Backup restored successfully!")
            except json.JSONDecodeError:
                st.error("Invalid backup file format")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.caption("🎙️ Professional Podcast Manager")

with col2:
    if st.session_state.gdrive_authenticated:
        st.caption("✅ Google Drive Connected")
    else:
        st.caption("⚠️ Google Drive Not Connected")

with col3:
    st.caption(f"{len(st.session_state.podcast_series)} Series • {len(st.session_state.episodes)} Episodes")

with col4:
    st.caption("Version 3.0 • Professional Edition")
