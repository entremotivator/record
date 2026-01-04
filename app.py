import streamlit as st
import io
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Professional Audio Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'recordings' not in st.session_state:
    st.session_state.recordings = []
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None
if 'playback_speed' not in st.session_state:
    st.session_state.playback_speed = 1.0
if 'recording_notes' not in st.session_state:
    st.session_state.recording_notes = {}

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Studio Settings")
    
    st.subheader("Recording Preferences")
    default_sample_rate = st.selectbox(
        "Default Sample Rate",
        [8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000],
        index=2,
        help="Choose your preferred default recording quality"
    )
    
    auto_save = st.checkbox("Auto-save recordings", value=True)
    show_waveform = st.checkbox("Show waveform visualization", value=False)
    
    st.divider()
    
    st.subheader("📊 Studio Statistics")
    total_recordings = len(st.session_state.recordings)
    st.metric("Total Recordings", total_recordings)
    
    if total_recordings > 0:
        voice_count = sum(1 for r in st.session_state.recordings if r['type'] == 'Voice Message')
        hq_count = sum(1 for r in st.session_state.recordings if r['type'] == 'High-Quality')
        custom_count = sum(1 for r in st.session_state.recordings if r['type'] == 'Custom')
        
        st.metric("Voice Messages", voice_count)
        st.metric("HQ Recordings", hq_count)
        st.metric("Custom", custom_count)
    
    st.divider()
    
    st.subheader("💾 Data Management")
    if st.button("📥 Export All Recordings", use_container_width=True):
        st.info("Export feature would create a ZIP file with all recordings")
    
    if st.button("🔄 Reset Studio", use_container_width=True):
        if st.session_state.recordings:
            st.warning("This will delete all recordings!")
        else:
            st.info("No recordings to reset")

# Main title
st.markdown('<h1 class="main-header">🎙️ Professional Audio Studio</h1>', unsafe_allow_html=True)
st.markdown("**Record, edit, manage, and export professional-quality audio with advanced controls**")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎤 Quick Record", 
    "🎵 Studio Recording", 
    "✂️ Audio Editor",
    "📚 Audio Library",
    "📊 Analytics",
    "📖 Help & Guide"
])

# Tab 1: Quick Record (Voice Messages)
with tab1:
    st.header("🎤 Quick Voice Recording")
    st.markdown("Perfect for voice memos, notes, and quick recordings at speech-optimized quality")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Record Now")
        
        quick_quality = st.radio(
            "Quality Preset",
            ["Telephone (8kHz)", "Speech (16kHz)", "High (24kHz)"],
            index=1,
            horizontal=True
        )
        
        quality_map = {
            "Telephone (8kHz)": 8000,
            "Speech (16kHz)": 16000,
            "High (24kHz)": 24000
        }
        
        selected_rate = quality_map[quick_quality]
        
        voice_audio = st.audio_input(
            "🎙️ Click to record",
            sample_rate=selected_rate,
            key="quick_recorder",
            help="Click the microphone to start recording. Click stop when done."
        )
        
        if voice_audio:
            st.success("✅ Recording captured successfully!")
            
            # Playback section
            st.subheader("Preview & Save")
            st.audio(voice_audio)
            
            # Recording details
            audio_bytes = voice_audio.getvalue()
            file_size_kb = len(audio_bytes) / 1024
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("File Size", f"{file_size_kb:.2f} KB")
            with col_b:
                st.metric("Sample Rate", f"{selected_rate} Hz")
            with col_c:
                st.metric("Quality", quick_quality.split()[0])
            
            st.divider()
            
            # Save options
            recording_name = st.text_input(
                "Recording Name (optional)",
                placeholder="e.g., Meeting notes, Voice memo...",
                key="quick_name"
            )
            
            recording_tags = st.text_input(
                "Tags (comma-separated)",
                placeholder="e.g., work, important, meeting",
                key="quick_tags"
            )
            
            col_save, col_discard = st.columns(2)
            
            with col_save:
                if st.button("💾 Save Recording", type="primary", use_container_width=True):
                    st.session_state.recordings.append({
                        'name': recording_name if recording_name else f"Quick Recording {len(st.session_state.recordings) + 1}",
                        'type': 'Voice Message',
                        'sample_rate': f'{selected_rate} Hz',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'data': audio_bytes,
                        'size_kb': file_size_kb,
                        'tags': [tag.strip() for tag in recording_tags.split(',') if tag.strip()],
                        'notes': ''
                    })
                    st.success("✅ Recording saved to library!")
                    st.balloons()
            
            with col_discard:
                if st.button("🗑️ Discard", use_container_width=True):
                    st.info("Recording discarded")
    
    with col2:
        st.subheader("Quality Info")
        st.info(f"""
        **Current Setting:**
        {quick_quality}
        
        **Best For:**
        - Voice memos
        - Speech recognition
        - Quick notes
        - Phone calls
        
        **File Size:**
        Small to medium
        """)
        
        st.subheader("Tips")
        st.markdown("""
        💡 **Recording Tips:**
        - Speak clearly
        - Minimize background noise
        - Keep mic 6-12" away
        - Test your levels first
        """)

# Tab 2: Studio Recording (High-Quality)
with tab2:
    st.header("🎵 Professional Studio Recording")
    st.markdown("High-fidelity recording for music, podcasts, and professional content")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Studio Controls")
        
        # Advanced quality selector
        col_preset, col_custom = st.columns(2)
        
        with col_preset:
            studio_preset = st.selectbox(
                "Quality Preset",
                ["CD Quality (44.1kHz)", "Studio (48kHz)", "Custom"],
                index=1
            )
        
        with col_custom:
            if studio_preset == "Custom":
                custom_rate = st.selectbox(
                    "Custom Sample Rate",
                    [8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000],
                    index=7
                )
                studio_rate = custom_rate
            else:
                studio_rate = 44100 if studio_preset == "CD Quality (44.1kHz)" else 48000
                st.metric("Sample Rate", f"{studio_rate} Hz")
        
        # Recording section
        st.divider()
        
        hq_audio = st.audio_input(
            "🎙️ Record Professional Audio",
            sample_rate=studio_rate,
            key="studio_recorder",
            help="High-quality recording - requires a good microphone for best results"
        )
        
        if hq_audio:
            st.success("✅ Professional recording captured!")
            
            st.subheader("Playback & Analysis")
            st.audio(hq_audio)
            
            # Detailed metrics
            audio_bytes = hq_audio.getvalue()
            file_size_kb = len(audio_bytes) / 1024
            file_size_mb = file_size_kb / 1024
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("File Size", f"{file_size_mb:.2f} MB" if file_size_mb > 1 else f"{file_size_kb:.2f} KB")
            with metric_col2:
                st.metric("Sample Rate", f"{studio_rate/1000:.1f} kHz")
            with metric_col3:
                st.metric("Quality", "Professional")
            with metric_col4:
                estimated_duration = (len(audio_bytes) / (studio_rate * 2)) 
                st.metric("Est. Duration", f"{estimated_duration:.1f}s")
            
            st.divider()
            
            # Advanced save options
            st.subheader("Recording Details")
            
            col_left, col_right = st.columns(2)
            
            with col_left:
                recording_name = st.text_input(
                    "Recording Name",
                    placeholder="e.g., Podcast Episode 1, Song Demo...",
                    key="studio_name"
                )
                
                recording_category = st.selectbox(
                    "Category",
                    ["Music", "Podcast", "Interview", "Performance", "Demo", "Other"],
                    key="studio_category"
                )
                
                recording_tags = st.text_input(
                    "Tags",
                    placeholder="e.g., guitar, vocal, rock",
                    key="studio_tags"
                )
            
            with col_right:
                recording_notes = st.text_area(
                    "Notes",
                    placeholder="Add notes about this recording...",
                    height=150,
                    key="studio_notes"
                )
            
            st.divider()
            
            col_save, col_discard = st.columns(2)
            
            with col_save:
                if st.button("💾 Save to Library", type="primary", use_container_width=True):
                    st.session_state.recordings.append({
                        'name': recording_name if recording_name else f"Studio Recording {len(st.session_state.recordings) + 1}",
                        'type': 'High-Quality',
                        'sample_rate': f'{studio_rate} Hz',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'data': audio_bytes,
                        'size_kb': file_size_kb,
                        'category': recording_category,
                        'tags': [tag.strip() for tag in recording_tags.split(',') if tag.strip()],
                        'notes': recording_notes
                    })
                    st.success("✅ Professional recording saved!")
                    st.balloons()
            
            with col_discard:
                if st.button("🗑️ Discard Recording", use_container_width=True):
                    st.info("Recording discarded")
    
    with col2:
        st.subheader("Studio Info")
        
        st.info(f"""
        **Current Setup:**
        {studio_preset}
        
        **Sample Rate:**
        {studio_rate} Hz
        
        **Best For:**
        - Music production
        - Podcasts
        - Voice-overs
        - Professional content
        """)
        
        st.subheader("Equipment Tips")
        st.markdown("""
        🎧 **For Best Results:**
        
        **Microphone:**
        - Use a quality USB or XLR mic
        - Position 6-12 inches away
        - Use a pop filter
        
        **Environment:**
        - Quiet room
        - Acoustic treatment
        - Minimal echo
        
        **Recording:**
        - Test levels first
        - Monitor with headphones
        - Record multiple takes
        """)

# Tab 3: Audio Editor
with tab3:
    st.header("✂️ Audio Editor")
    st.markdown("Edit, trim, and enhance your recordings with advanced tools")
    
    if not st.session_state.recordings:
        st.info("📭 No recordings available. Create a recording first in the other tabs!")
    else:
        # Select recording to edit
        recording_names = [f"{r['name']} ({r['timestamp']})" for r in st.session_state.recordings]
        selected_recording = st.selectbox(
            "Select Recording to Edit",
            range(len(recording_names)),
            format_func=lambda x: recording_names[x]
        )
        
        if selected_recording is not None:
            recording = st.session_state.recordings[selected_recording]
            
            st.divider()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Original Recording")
                st.audio(recording['data'])
                
                st.subheader("Edit Tools")
                
                # Editing options
                edit_tab1, edit_tab2, edit_tab3 = st.tabs(["📝 Metadata", "🏷️ Tags & Notes", "⚙️ Properties"])
                
                with edit_tab1:
                    st.write("**Edit Recording Information**")
                    
                    new_name = st.text_input(
                        "Recording Name",
                        value=recording['name'],
                        key=f"edit_name_{selected_recording}"
                    )
                    
                    new_category = st.selectbox(
                        "Category",
                        ["Voice Message", "High-Quality", "Custom", "Music", "Podcast", "Interview", "Other"],
                        index=0 if recording['type'] == 'Voice Message' else 1,
                        key=f"edit_category_{selected_recording}"
                    )
                    
                    if st.button("💾 Save Metadata Changes", key=f"save_meta_{selected_recording}"):
                        st.session_state.recordings[selected_recording]['name'] = new_name
                        st.session_state.recordings[selected_recording]['type'] = new_category
                        st.success("✅ Metadata updated!")
                        st.rerun()
                
                with edit_tab2:
                    st.write("**Manage Tags and Notes**")
                    
                    current_tags = ', '.join(recording.get('tags', []))
                    new_tags = st.text_input(
                        "Tags (comma-separated)",
                        value=current_tags,
                        key=f"edit_tags_{selected_recording}"
                    )
                    
                    current_notes = recording.get('notes', '')
                    new_notes = st.text_area(
                        "Notes",
                        value=current_notes,
                        height=150,
                        key=f"edit_notes_{selected_recording}"
                    )
                    
                    if st.button("💾 Save Tags & Notes", key=f"save_tags_{selected_recording}"):
                        st.session_state.recordings[selected_recording]['tags'] = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
                        st.session_state.recordings[selected_recording]['notes'] = new_notes
                        st.success("✅ Tags and notes updated!")
                        st.rerun()
                
                with edit_tab3:
                    st.write("**Recording Properties**")
                    
                    st.text_input("Sample Rate", value=recording['sample_rate'], disabled=True)
                    st.text_input("File Size", value=f"{recording['size_kb']:.2f} KB", disabled=True)
                    st.text_input("Recorded", value=recording['timestamp'], disabled=True)
                    st.text_input("Type", value=recording['type'], disabled=True)
                    
                    st.info("💡 Audio processing features would include trimming, volume adjustment, and effects")
            
            with col2:
                st.subheader("Recording Info")
                
                st.metric("Name", recording['name'])
                st.metric("Type", recording['type'])
                st.metric("Sample Rate", recording['sample_rate'])
                st.metric("Size", f"{recording['size_kb']:.2f} KB")
                
                if recording.get('tags'):
                    st.write("**Tags:**")
                    for tag in recording['tags']:
                        st.badge(tag)
                
                st.divider()
                
                st.subheader("Quick Actions")
                
                if st.button("📥 Download", use_container_width=True, key=f"download_{selected_recording}"):
                    st.info("Download feature would save the audio file")
                
                if st.button("📋 Duplicate", use_container_width=True, key=f"duplicate_{selected_recording}"):
                    new_recording = recording.copy()
                    new_recording['name'] = f"{recording['name']} (Copy)"
                    new_recording['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.recordings.append(new_recording)
                    st.success("✅ Recording duplicated!")
                    st.rerun()
                
                if st.button("🗑️ Delete", use_container_width=True, type="secondary", key=f"delete_editor_{selected_recording}"):
                    st.session_state.recordings.pop(selected_recording)
                    st.success("🗑️ Recording deleted!")
                    st.rerun()

# Tab 4: Audio Library
with tab4:
    st.header("📚 Audio Library")
    st.markdown("Browse, search, and manage all your recordings")
    
    if not st.session_state.recordings:
        st.info("📭 No recordings yet. Start recording in the Quick Record or Studio Recording tabs!")
        
        # Show example of what library looks like
        st.divider()
        st.subheader("Library Preview")
        st.write("Your library will display recordings with:")
        st.markdown("""
        - 🎵 Audio playback
        - 📊 Detailed metadata
        - 🏷️ Tag filtering
        - 🔍 Search functionality
        - 📥 Export options
        - ✏️ Quick editing
        """)
    else:
        # Search and filter
        col_search, col_filter, col_sort = st.columns([2, 1, 1])
        
        with col_search:
            search_query = st.text_input(
                "🔍 Search recordings",
                placeholder="Search by name, tags, or notes...",
                key="library_search"
            )
        
        with col_filter:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "Voice Message", "High-Quality", "Custom"],
                key="library_filter"
            )
        
        with col_sort:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest First", "Oldest First", "Name (A-Z)", "Size (Largest)"],
                key="library_sort"
            )
        
        st.divider()
        
        # Filter and sort recordings
        filtered_recordings = st.session_state.recordings.copy()
        
        # Apply type filter
        if filter_type != "All":
            filtered_recordings = [r for r in filtered_recordings if r['type'] == filter_type]
        
        # Apply search
        if search_query:
            search_lower = search_query.lower()
            filtered_recordings = [
                r for r in filtered_recordings 
                if search_lower in r['name'].lower() 
                or search_lower in r.get('notes', '').lower()
                or any(search_lower in tag.lower() for tag in r.get('tags', []))
            ]
        
        # Apply sorting
        if sort_by == "Newest First":
            filtered_recordings = list(reversed(filtered_recordings))
        elif sort_by == "Name (A-Z)":
            filtered_recordings.sort(key=lambda x: x['name'].lower())
        elif sort_by == "Size (Largest)":
            filtered_recordings.sort(key=lambda x: x['size_kb'], reverse=True)
        
        # Display results
        st.write(f"**Showing {len(filtered_recordings)} of {len(st.session_state.recordings)} recordings**")
        
        # Library view options
        view_mode = st.radio(
            "View Mode",
            ["Detailed", "Compact", "Grid"],
            horizontal=True,
            key="view_mode"
        )
        
        st.divider()
        
        if view_mode == "Detailed":
            # Detailed view with expanders
            for idx, recording in enumerate(filtered_recordings):
                original_idx = st.session_state.recordings.index(recording)
                
                with st.expander(f"🎵 {recording['name']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.audio(recording['data'])
                        
                        if recording.get('notes'):
                            st.write("**Notes:**")
                            st.write(recording['notes'])
                    
                    with col2:
                        st.write(f"**Type:** {recording['type']}")
                        st.write(f"**Sample Rate:** {recording['sample_rate']}")
                        st.write(f"**Size:** {recording['size_kb']:.2f} KB")
                        st.write(f"**Recorded:** {recording['timestamp']}")
                        
                        if recording.get('tags'):
                            st.write("**Tags:**")
                            for tag in recording['tags']:
                                st.markdown(f"`{tag}`")
                        
                        st.divider()
                        
                        if st.button("✏️ Edit", key=f"lib_edit_{original_idx}", use_container_width=True):
                            st.info("Switch to Audio Editor tab to edit this recording")
                        
                        if st.button("🗑️ Delete", key=f"lib_delete_{original_idx}", use_container_width=True):
                            st.session_state.recordings.pop(original_idx)
                            st.rerun()
        
        elif view_mode == "Compact":
            # Compact table view
            for idx, recording in enumerate(filtered_recordings):
                original_idx = st.session_state.recordings.index(recording)
                
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{recording['name']}**")
                    st.audio(recording['data'])
                
                with col2:
                    st.write(f"{recording['type']}")
                
                with col3:
                    st.write(f"{recording['size_kb']:.1f} KB")
                
                with col4:
                    st.write(recording['timestamp'].split()[0])
                
                with col5:
                    if st.button("🗑️", key=f"compact_delete_{original_idx}"):
                        st.session_state.recordings.pop(original_idx)
                        st.rerun()
                
                st.divider()
        
        else:  # Grid view
            # Grid view with cards
            cols_per_row = 3
            recordings_list = list(enumerate(filtered_recordings))
            
            for i in range(0, len(recordings_list), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(recordings_list):
                        idx, recording = recordings_list[i + j]
                        original_idx = st.session_state.recordings.index(recording)
                        
                        with col:
                            with st.container():
                                st.subheader(recording['name'][:20] + "..." if len(recording['name']) > 20 else recording['name'])
                                st.audio(recording['data'])
                                st.caption(f"{recording['type']} • {recording['size_kb']:.1f} KB")
                                st.caption(recording['timestamp'])
                                
                                if st.button("🗑️", key=f"grid_delete_{original_idx}", use_container_width=True):
                                    st.session_state.recordings.pop(original_idx)
                                    st.rerun()
        
        # Bulk actions
        st.divider()
        st.subheader("Bulk Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export All", use_container_width=True):
                st.info("Export feature would create a ZIP file with all recordings")
        
        with col2:
            if st.button("🏷️ Batch Tag", use_container_width=True):
                st.info("Batch tagging feature would allow adding tags to multiple recordings")
        
        with col3:
            if st.button("🗑️ Clear Library", use_container_width=True, type="secondary"):
                if st.session_state.recordings:
                    st.warning(f"⚠️ This will delete all {len(st.session_state.recordings)} recordings!")
                    if st.button("⚠️ Confirm Delete All", type="secondary"):
                        st.session_state.recordings = []
                        st.success("Library cleared!")
                        st.rerun()

# Tab 5: Analytics
with tab5:
    st.header("📊 Recording Analytics")
    st.markdown("Analyze your recording patterns and statistics")
    
    if not st.session_state.recordings:
        st.info("📭 No data available. Start recording to see analytics!")
    else:
        # Overview metrics
        st.subheader("Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_recordings = len(st.session_state.recordings)
        total_size = sum(r['size_kb'] for r in st.session_state.recordings)
        avg_size = total_size / total_recordings
        
        with col1:
            st.metric("Total Recordings", total_recordings)
        
        with col2:
            st.metric("Total Size", f"{total_size:.2f} KB" if total_size < 1024 else f"{total_size/1024:.2f} MB")
        
        with col3:
            st.metric("Average Size", f"{avg_size:.2f} KB")
        
        with col4:
            latest = st.session_state.recordings[-1]['timestamp'].split()[0]
            st.metric("Latest Recording", latest)
        
        st.divider()
        
        # Type distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recording Types")
            
            type_counts = {}
            for r in st.session_state.recordings:
                type_counts[r['type']] = type_counts.get(r['type'], 0) + 1
            
            for rec_type, count in type_counts.items():
                percentage = (count / total_recordings) * 100
                st.write(f"**{rec_type}:** {count} ({percentage:.1f}%)")
                st.progress(percentage / 100)
        
        with col2:
            st.subheader("Sample Rate Distribution")
            
            rate_counts = {}
            for r in st.session_state.recordings:
                rate_counts[r['sample_rate']] = rate_counts.get(r['sample_rate'], 0) + 1
            
            for rate, count in rate_counts.items():
                percentage = (count / total_recordings) * 100
                st.write(f"**{rate}:** {count} ({percentage:.1f}%)")
                st.progress(percentage / 100)
        
        st.divider()
        
        # Timeline
        st.subheader("Recording Timeline")
        
        dates = {}
        for r in st.session_state.recordings:
            date = r['timestamp'].split()[0]
            dates[date] = dates.get(date, 0) + 1
        
        if dates:
            st.write("**Recordings per day:**")
            for date, count in sorted(dates.items()):
                st.write(f"**{date}:** {count} recording{'s' if count > 1 else ''}")
        
        st.divider()
        
        # Tag cloud
        st.subheader("Tag Analysis")
        
        all_tags = {}
        for r in st.session_state.recordings:
            for tag in r.get('tags', []):
                all_tags[tag] = all_tags.get(tag, 0) + 1
        
        if all_tags:
            st.write("**Most used tags:**")
            sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
            
            for tag, count in sorted_tags[:10]:
                col_tag, col_count = st.columns([3, 1])
                with col_tag:
                    st.write(f"**{tag}**")
                with col_count:
                    st.write(f"{count} uses")
        else:
            st.info("No tags used yet. Add tags to your recordings!")
        
        st.divider()
        
        # Storage optimization
        st.subheader("Storage Optimization")
        
        st.write("**Largest recordings:**")
        sorted_by_size = sorted(st.session_state.recordings, key=lambda x: x['size_kb'], reverse=True)[:5]
        
        for r in sorted_by_size:
            col_name, col_size = st.columns([3, 1])
            with col_name:
                st.write(f"**{r['name']}**")
            with col_size:
                st.write(f"{r['size_kb']:.2f} KB")

# Tab 6: Help & Guide
with tab6:
    st.header("📖 Help & User Guide")
    st.markdown("Learn how to get the most out of the Professional Audio Studio")
    
    help_tab1, help_tab2, help_tab3, help_tab4 = st.tabs([
        "🚀 Getting Started",
        "🎙️ Recording Tips",
        "📊 Sample Rates",
        "❓ FAQ"
    ])
    
    with help_tab1:
        st.subheader("Welcome to Professional Audio Studio!")
        
        st.markdown("""
        This comprehensive audio recording platform provides everything you need to create, 
        manage, and organize professional-quality audio recordings.
        
        ### Quick Start Guide
        
        **1. Choose Your Recording Mode**
        - **Quick Record**: Perfect for voice memos and quick notes (8-24 kHz)
        - **Studio Recording**: Professional-quality recording for music and podcasts (44.1-48 kHz)
        
        **2. Record Your Audio**
        - Click the microphone icon to start recording
        - Speak or perform your content
        - Click stop when finished
        
        **3. Preview & Save**
        - Listen to your recording
        - Add a name, tags, and notes
        - Save to your library
        
        **4. Manage Your Library**
        - Browse all recordings in the Audio Library tab
        - Edit metadata in the Audio Editor tab
        - View analytics in the Analytics tab
        
        ### Key Features
        
        - ✅ Multiple quality presets (8kHz to 48kHz)
        - ✅ Comprehensive metadata management
        - ✅ Tag-based organization
        - ✅ Search and filter capabilities
        - ✅ Recording analytics
        - ✅ Professional studio controls
        """)
    
    with help_tab2:
        st.subheader("🎙️ Professional Recording Tips")
        
        st.markdown("""
        ### Microphone Setup
        
        **Position**
        - Keep microphone 6-12 inches from mouth
        - Angle slightly off-axis to reduce plosives
        - Use a pop filter for best results
        
        **Environment**
        - Choose a quiet room
        - Minimize background noise
        - Add acoustic treatment if possible
        - Close windows and doors
        
        ### Recording Technique
        
        **Voice Recording**
        - Speak naturally and clearly
        - Maintain consistent distance from mic
        - Take breaks to avoid fatigue
        - Stay hydrated
        
        **Music Recording**
        - Test levels before recording
        - Use headphones for monitoring
        - Record multiple takes
        - Leave headroom (don't peak)
        
        ### Quality Settings
        
        **For Speech (Voice Memos, Calls):**
        - Use 8-16 kHz sample rate
        - Smaller file sizes
        - Optimized for voice clarity
        
        **For Music (Production, Podcasts):**
        - Use 44.1-48 kHz sample rate
        - Larger file sizes
        - Maximum fidelity
        
        ### Common Issues
        
        **Problem: Background Noise**
        - Solution: Record in quieter environment, use noise reduction
        
        **Problem: Distortion**
        - Solution: Reduce input level, move further from mic
        
        **Problem: Low Volume**
        - Solution: Move closer to mic, increase input gain
        
        **Problem: Pops and Clicks**
        - Solution: Use pop filter, adjust mic position
        """)
    
    with help_tab3:
        st.subheader("📊 Understanding Sample Rates")
        
        st.markdown("""
        Sample rate determines the quality and file size of your recordings.
        Higher sample rates capture more detail but create larger files.
        
        ### Sample Rate Guide
        """)
        
        sample_rate_info = {
            "8000 Hz": {
                "quality": "Telephone",
                "best_for": "Phone calls, simple voice",
                "file_size": "Very Small",
                "use_case": "Basic voice recording where file size matters"
            },
            "11025 Hz": {
                "quality": "Low",
                "best_for": "Simple audio, low-quality music",
                "file_size": "Small",
                "use_case": "Basic audio where quality isn't critical"
            },
            "16000 Hz": {
                "quality": "Speech",
                "best_for": "Voice memos, speech recognition, dictation",
                "file_size": "Small",
                "use_case": "Voice messages, meeting notes, transcription"
            },
            "22050 Hz": {
                "quality": "FM Radio",
                "best_for": "Voice with better quality",
                "file_size": "Medium",
                "use_case": "Voice recordings that need better clarity"
            },
            "24000 Hz": {
                "quality": "Good",
                "best_for": "Quality voice, basic music",
                "file_size": "Medium",
                "use_case": "Podcasts, voice-overs"
            },
            "32000 Hz": {
                "quality": "High",
                "best_for": "Music, video soundtracks",
                "file_size": "Large",
                "use_case": "Video production audio"
            },
            "44100 Hz": {
                "quality": "CD Quality",
                "best_for": "Music production, professional audio",
                "file_size": "Large",
                "use_case": "Music recording, professional podcasts"
            },
            "48000 Hz": {
                "quality": "Studio/Professional",
                "best_for": "Professional music, film audio",
                "file_size": "Large",
                "use_case": "Professional recording, broadcast, film"
            }
        }
        
        for rate, info in sample_rate_info.items():
            with st.expander(f"**{rate}** - {info['quality']} Quality"):
                st.write(f"**Best For:** {info['best_for']}")
                st.write(f"**File Size:** {info['file_size']}")
                st.write(f"**Use Case:** {info['use_case']}")
        
        st.divider()
        
        st.markdown("""
        ### Choosing the Right Sample Rate
        
        **Quick Decision Guide:**
        
        1. **Voice Only (Speech, Memos, Notes)**
           - Recommended: 16000 Hz
           - Alternative: 8000 Hz (smallest files)
        
        2. **Podcasts & Interviews**
           - Recommended: 24000-48000 Hz
           - Professional: 48000 Hz
        
        3. **Music Recording**
           - Minimum: 44100 Hz
           - Professional: 48000 Hz
        
        4. **File Size Critical**
           - Use lowest rate that meets quality needs
           - 8000-16000 Hz for voice
        
        5. **Maximum Quality**
           - Always use 48000 Hz
           - Requires good microphone
        """)
    
    with help_tab4:
        st.subheader("❓ Frequently Asked Questions")
        
        faq_items = [
            {
                "q": "How do I grant microphone permissions?",
                "a": """Your browser will prompt you for microphone access when you first try to record. 
                Click 'Allow' to enable recording. If you denied access, you can enable it in your browser 
                settings under Privacy > Microphone."""
            },
            {
                "q": "What's the best sample rate for podcasts?",
                "a": """For professional podcasts, use 48000 Hz. For good quality with smaller files, 
                24000 Hz works well. The default speech rate of 16000 Hz is fine for simple voice podcasts."""
            },
            {
                "q": "Why are my recordings so large?",
                "a": """Higher sample rates (44.1kHz, 48kHz) create larger files because they capture more 
                audio data. For voice-only content, use 16000 Hz to reduce file size significantly."""
            },
            {
                "q": "Can I edit my recordings after saving?",
                "a": """Yes! Go to the Audio Editor tab to edit metadata, tags, notes, and properties. 
                Full audio editing features (trimming, effects) would be available in future updates."""
            },
            {
                "q": "How do I export my recordings?",
                "a": """Use the download button in the library or editor to save individual recordings. 
                The 'Export All' feature creates a ZIP file with all recordings."""
            },
            {
                "q": "What microphone should I use?",
                "a": """For voice: Any USB microphone works well. For music: Use a quality condenser or 
                dynamic microphone. Budget options: Blue Snowball, Audio-Technica AT2020. 
                Professional: Shure SM7B, Neumann U87."""
            },
            {
                "q": "Why can't I hear my recording?",
                "a": """Check your browser's audio settings and ensure your speakers/headphones are connected. 
                Also verify the recording was saved (check the file size isn't 0 KB)."""
            },
            {
                "q": "How many recordings can I save?",
                "a": """The app stores recordings in your browser session. The limit depends on your device's 
                memory. For permanent storage, download important recordings."""
            },
            {
                "q": "What format are the recordings saved in?",
                "a": """Recordings are saved in WAV format by default, which provides uncompressed, 
                high-quality audio."""
            },
            {
                "q": "Can I use this for music production?",
                "a": """Yes! Use the Studio Recording tab with 48000 Hz sample rate. However, for serious 
                music production, consider using dedicated DAW software like Audacity, GarageBand, or Pro Tools."""
            }
        ]
        
        for faq in faq_items:
            with st.expander(f"**Q: {faq['q']}**"):
                st.write(f"**A:** {faq['a']}")
        
        st.divider()
        
        st.subheader("Need More Help?")
        st.markdown("""
        **Additional Resources:**
        - 📚 Check out the other help tabs for detailed information
        - 🎙️ Recording Tips tab for professional techniques
        - 📊 Sample Rates tab for quality information
        - ⚙️ Use the sidebar for studio settings and statistics
        
        **Technical Support:**
        - Ensure your browser is up to date
        - Grant microphone permissions when prompted
        - Use headphones to prevent feedback
        - Close other applications using the microphone
        """)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🎙️ Professional Audio Studio")

with col2:
    st.caption(f"Version 2.0 | {len(st.session_state.recordings)} Recordings")

with col3:
    st.caption("Built with Streamlit 🎈")
