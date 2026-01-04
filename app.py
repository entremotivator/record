import streamlit as st
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Audio Recorder App",
    page_icon="🎙️",
    layout="wide"
)

# Title and description
st.title("🎙️ Audio Recording Studio")
st.markdown("Record, play back, and manage your audio recordings with different quality settings.")

# Initialize session state for storing recordings
if 'recordings' not in st.session_state:
    st.session_state.recordings = []

# Create tabs for different features
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Voice Messages", 
    "🎵 High-Quality Audio", 
    "📊 Audio Library",
    "⚙️ Settings"
])

# Tab 1: Voice Messages (Speech Recognition Quality)
with tab1:
    st.header("Voice Message Recorder")
    st.info("Optimized for speech recognition at 16000 Hz")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        voice_audio = st.audio_input(
            "Record a voice message",
            sample_rate=16000,
            key="voice_recorder",
            help="Click to start recording your voice message"
        )
        
        if voice_audio:
            st.success("✅ Recording captured!")
            st.audio(voice_audio)
            
            # Save button
            if st.button("💾 Save Voice Message", key="save_voice"):
                st.session_state.recordings.append({
                    'type': 'Voice Message',
                    'sample_rate': '16000 Hz',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'data': voice_audio.getvalue()
                })
                st.success("Recording saved to library!")
    
    with col2:
        st.metric("Sample Rate", "16 kHz")
        st.metric("Quality", "Speech")
        st.metric("File Size", "Small")

# Tab 2: High-Quality Audio
with tab2:
    st.header("High-Fidelity Audio Recorder")
    st.info("Professional quality at 48000 Hz - ideal for music and high-quality recordings")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        hq_audio = st.audio_input(
            "Record high-quality audio",
            sample_rate=48000,
            key="hq_recorder",
            help="Requires a quality microphone for best results"
        )
        
        if hq_audio:
            st.success("✅ High-quality recording captured!")
            st.audio(hq_audio)
            
            # Save button
            if st.button("💾 Save HQ Recording", key="save_hq"):
                st.session_state.recordings.append({
                    'type': 'High-Quality',
                    'sample_rate': '48000 Hz',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'data': hq_audio.getvalue()
                })
                st.success("Recording saved to library!")
    
    with col2:
        st.metric("Sample Rate", "48 kHz")
        st.metric("Quality", "Professional")
        st.metric("File Size", "Large")

# Tab 3: Audio Library
with tab3:
    st.header("Your Audio Library")
    
    if st.session_state.recordings:
        st.write(f"Total recordings: **{len(st.session_state.recordings)}**")
        
        for idx, recording in enumerate(reversed(st.session_state.recordings)):
            with st.expander(f"🎵 {recording['type']} - {recording['timestamp']}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.audio(recording['data'])
                
                with col2:
                    st.write(f"**Type:** {recording['type']}")
                    st.write(f"**Sample Rate:** {recording['sample_rate']}")
                
                with col3:
                    st.write(f"**Recorded:** {recording['timestamp']}")
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        st.session_state.recordings.pop(len(st.session_state.recordings) - 1 - idx)
                        st.rerun()
        
        # Clear all button
        st.divider()
        if st.button("🗑️ Clear All Recordings", type="secondary"):
            st.session_state.recordings = []
            st.rerun()
    else:
        st.info("📭 No recordings yet. Start recording in the other tabs!")

# Tab 4: Settings & Info
with tab4:
    st.header("Audio Settings & Information")
    
    st.subheader("📊 Sample Rate Comparison")
    
    sample_rates = {
        "8000 Hz": "Telephone quality - minimal file size",
        "11025 Hz": "Low quality - suitable for simple audio",
        "16000 Hz": "Speech recognition quality - optimal for voice",
        "22050 Hz": "FM radio quality",
        "24000 Hz": "Good quality audio",
        "32000 Hz": "High quality",
        "44100 Hz": "CD quality - standard audio",
        "48000 Hz": "Professional quality - studio recording"
    }
    
    for rate, description in sample_rates.items():
        st.write(f"**{rate}:** {description}")
    
    st.divider()
    
    st.subheader("💡 Tips for Best Results")
    st.markdown("""
    - **Microphone Position:** Keep the microphone 6-12 inches from your mouth
    - **Environment:** Record in a quiet space to minimize background noise
    - **Quality vs Size:** Higher sample rates create larger files but better quality
    - **Speech Recognition:** Use 16 kHz for voice commands and transcription
    - **Music Recording:** Use 44.1 kHz or 48 kHz for musical content
    - **Browser Permissions:** Ensure microphone access is granted
    """)
    
    st.divider()
    
    st.subheader("🔧 Technical Details")
    st.code("""
# Basic usage
audio_value = st.audio_input("Record audio", sample_rate=16000)

if audio_value:
    st.audio(audio_value)
    # Process audio data
    audio_bytes = audio_value.getvalue()
    """, language="python")

# Footer
st.divider()
st.caption("Built with Streamlit 🎈 | Audio Recording Studio v1.0")
