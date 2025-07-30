# Streamlit Theta - Open Source Visual Editors Suite for Streamlit
# Provides editors for presentations, documents, spreadsheets, tables, audio, and video.

from .editor.slide import theta_slide_editor
from .editor.document import theta_document_editor
from .editor.spreadsheet import theta_spreadsheet_editor
from .editor.csv import theta_csv_editor
from .editor.audio import theta_audio_editor
from .editor.video import theta_video_editor

# Convenience imports
slide_editor = theta_slide_editor
document_editor = theta_document_editor
spreadsheet_editor = theta_spreadsheet_editor
csv_editor = theta_csv_editor
audio_editor = theta_audio_editor
video_editor = theta_video_editor

__version__ = "1.0.1"
__author__ = "Arcana Team"
__description__ = "Comprehensive visual editors for Streamlit applications"

__all__ = [
    'theta_slide_editor',
    'theta_document_editor',
    'theta_spreadsheet_editor', 
    'theta_csv_editor',
    'theta_audio_editor',
    'theta_video_editor',
    'slide_editor',
    'document_editor',
    'spreadsheet_editor',
    'csv_editor',
    'audio_editor',
    'video_editor'
] 