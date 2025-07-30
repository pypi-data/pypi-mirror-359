"""
Streamlit Theta - Comprehensive Visual Editors for Streamlit

A collection of advanced visual editors for different content types:
- Slide/PowerPoint presentations
- Word documents  
- Excel spreadsheets
- CSV data tables
- Audio files
- Video files
"""

from .editor.slide import theta_slide_editor
from .editor.word import theta_word_editor
from .editor.excel import theta_excel_editor
from .editor.csv import theta_csv_editor
from .editor.audio import theta_audio_editor
from .editor.video import theta_video_editor

__version__ = "1.0.0"
__author__ = "Arcana Team"
__description__ = "Comprehensive visual editors for Streamlit applications"

__all__ = [
    "theta_slide_editor",
    "theta_word_editor", 
    "theta_excel_editor",
    "theta_csv_editor",
    "theta_audio_editor",
    "theta_video_editor"
]

# Convenience import - users can import from top level
slide_editor = theta_slide_editor
word_editor = theta_word_editor
excel_editor = theta_excel_editor
csv_editor = theta_csv_editor
audio_editor = theta_audio_editor
video_editor = theta_video_editor 