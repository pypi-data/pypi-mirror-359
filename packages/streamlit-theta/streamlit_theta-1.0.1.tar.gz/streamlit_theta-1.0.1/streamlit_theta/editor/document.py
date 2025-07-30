"""
Theta Word Editor - Visual document editor for Streamlit
Provides a WYSIWYG interface for creating and editing documents.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from typing import Dict, List, Any, Optional

def theta_document_editor(
    content: str = "",
    width: int = 800,
    height: int = 600
) -> None:
    """
    Create a document-style editor.
    
    Parameters:
    -----------
    content : str
        Initial document content (HTML format)
    width : int
        Width of the editor in pixels
    height : int  
        Height of the editor in pixels
    key : str
        Unique key for the component
        
    Returns:
    --------
    str or None
        Updated document content or None if no changes
    """
    
    # Safety check: ensure content is a proper string, not a DeltaGenerator
    if not isinstance(content, str):
        content = ""
    
    # Component HTML/CSS/JS for document-style editor
    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Theta Word Editor</title>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f5f5f5;
            }}
            
            .editor-container {{
                width: {width}px;
                height: {height}px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
            }}
            
            .toolbar {{
                height: 60px;
                background: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
                border-radius: 8px 8px 0 0;
                display: flex;
                align-items: center;
                padding: 0 15px;
                gap: 10px;
                flex-wrap: wrap;
            }}
            
            .toolbar-group {{
                display: flex;
                gap: 5px;
                align-items: center;
                padding-right: 10px;
                border-right: 1px solid #dee2e6;
            }}
            
            .toolbar button {{
                background: #fff;
                border: 1px solid #dee2e6;
                padding: 6px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
            }}
            
            .toolbar button:hover {{
                background: #e9ecef;
                border-color: #adb5bd;
            }}
            
            .toolbar button.active {{
                background: #007bff;
                color: white;
                border-color: #007bff;
            }}
            
            .toolbar select {{
                padding: 4px 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-size: 12px;
            }}
            
            .editor-main {{
                flex: 1;
                display: flex;
                background: #f8f9fa;
            }}
            
            .document-area {{
                flex: 1;
                padding: 20px;
                overflow: auto;
            }}
            
            .document {{
                width: 100%;
                max-width: 21cm; /* A4 width */
                min-height: 29.7cm; /* A4 height */
                background: white;
                margin: 0 auto;
                padding: 2.5cm;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                border: 1px solid #ddd;
                font-family: 'Times New Roman', serif;
                font-size: 12pt;
                line-height: 1.5;
                outline: none;
                overflow-wrap: break-word;
            }}
            
            .document:focus {{
                box-shadow: 0 0 0 2px #007bff;
            }}
            
            .properties-panel {{
                width: 250px;
                background: #f8f9fa;
                border-left: 1px solid #dee2e6;
                padding: 15px;
                overflow-y: auto;
            }}
            
            .property-group {{
                margin-bottom: 20px;
                padding: 15px;
                background: white;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }}
            
            .property-group h4 {{
                margin: 0 0 10px 0;
                font-size: 14px;
                font-weight: 600;
                color: #495057;
            }}
            
            .property-row {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                gap: 8px;
            }}
            
            .property-row label {{
                font-size: 12px;
                color: #6c757d;
                flex: 1;
            }}
            
            .property-row input, .property-row select {{
                flex: 1;
                padding: 4px 6px;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="editor-container">
            <!-- Toolbar -->
            <div class="toolbar">
                <div class="toolbar-group">
                    <button id="bold" title="Bold">B</button>
                    <button id="italic" title="Italic">I</button>
                    <button id="underline" title="Underline">U</button>
                </div>
                
                <div class="toolbar-group">
                    <select id="font-family">
                        <option value="Times New Roman">Times New Roman</option>
                        <option value="Arial">Arial</option>
                        <option value="Calibri">Calibri</option>
                        <option value="Georgia">Georgia</option>
                    </select>
                    <select id="font-size">
                        <option value="10">10</option>
                        <option value="11">11</option>
                        <option value="12" selected>12</option>
                        <option value="14">14</option>
                        <option value="16">16</option>
                        <option value="18">18</option>
                        <option value="20">20</option>
                        <option value="24">24</option>
                    </select>
                </div>
                
                <div class="toolbar-group">
                    <button id="align-left" title="Align Left">⬅</button>
                    <button id="align-center" title="Center">🔘</button>
                    <button id="align-right" title="Align Right">➡</button>
                    <button id="justify" title="Justify">⬛</button>
                </div>
                
                <div class="toolbar-group">
                    <button id="bullet-list" title="Bullet List">• List</button>
                    <button id="number-list" title="Numbered List">1. List</button>
                </div>
                
                <div class="toolbar-group">
                    <button id="save-doc" title="Save Document">💾 Save</button>
                </div>
            </div>
            
            <!-- Main Editor -->
            <div class="editor-main">
                <!-- Document Area -->
                <div class="document-area">
                    <div class="document" id="document" contenteditable="true">
                        {content or "Start typing your document here..."}
                    </div>
                </div>
                
                <!-- Properties Panel -->
                <div class="properties-panel">
                    <div class="property-group">
                        <h4>Document Properties</h4>
                        <div class="property-row">
                            <label>Page Size:</label>
                            <select id="page-size">
                                <option value="A4" selected>A4</option>
                                <option value="Letter">Letter</option>
                                <option value="Legal">Legal</option>
                            </select>
                        </div>
                        <div class="property-row">
                            <label>Orientation:</label>
                            <select id="orientation">
                                <option value="portrait" selected>Portrait</option>
                                <option value="landscape">Landscape</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="property-group">
                        <h4>Paragraph</h4>
                        <div class="property-row">
                            <label>Line Height:</label>
                            <select id="line-height">
                                <option value="1">Single</option>
                                <option value="1.5" selected>1.5 lines</option>
                                <option value="2">Double</option>
                            </select>
                        </div>
                        <div class="property-row">
                            <label>Indent:</label>
                            <input type="number" id="indent" value="0" min="0" max="5" step="0.5">
                        </div>
                    </div>
                    
                    <div class="property-group">
                        <h4>Statistics</h4>
                        <div class="property-row">
                            <label>Words:</label>
                            <span id="word-count">0</span>
                        </div>
                        <div class="property-row">
                            <label>Characters:</label>
                            <span id="char-count">0</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Theta Word Editor JavaScript
            let documentContent = `{content}`;
            
            // Initialize editor
            function initEditor() {{
                setupEventListeners();
                updateStatistics();
            }}
            
            function setupEventListeners() {{
                const doc = document.getElementById('document');
                
                // Formatting buttons
                document.getElementById('bold').onclick = () => document.execCommand('bold');
                document.getElementById('italic').onclick = () => document.execCommand('italic');
                document.getElementById('underline').onclick = () => document.execCommand('underline');
                
                // Alignment
                document.getElementById('align-left').onclick = () => document.execCommand('justifyLeft');
                document.getElementById('align-center').onclick = () => document.execCommand('justifyCenter');
                document.getElementById('align-right').onclick = () => document.execCommand('justifyRight');
                document.getElementById('justify').onclick = () => document.execCommand('justifyFull');
                
                // Lists
                document.getElementById('bullet-list').onclick = () => document.execCommand('insertUnorderedList');
                document.getElementById('number-list').onclick = () => document.execCommand('insertOrderedList');
                
                // Font changes
                document.getElementById('font-family').onchange = (e) => {{
                    document.execCommand('fontName', false, e.target.value);
                }};
                
                document.getElementById('font-size').onchange = (e) => {{
                    document.execCommand('fontSize', false, '3');
                    const selection = window.getSelection();
                    if (selection.rangeCount > 0) {{
                        const range = selection.getRangeAt(0);
                        const span = document.createElement('span');
                        span.style.fontSize = e.target.value + 'pt';
                        try {{
                            range.surroundContents(span);
                        }} catch (e) {{
                            span.appendChild(range.extractContents());
                            range.insertNode(span);
                        }}
                    }}
                }};
                
                // Document properties
                document.getElementById('line-height').onchange = (e) => {{
                    doc.style.lineHeight = e.target.value;
                }};
                
                document.getElementById('indent').onchange = (e) => {{
                    doc.style.textIndent = e.target.value + 'cm';
                }};
                
                // Content change tracking
                doc.oninput = () => {{
                    updateStatistics();
                    documentContent = doc.innerHTML;
                }};
                
                // Save button
                document.getElementById('save-doc').onclick = saveDocument;
            }}
            
            function updateStatistics() {{
                const doc = document.getElementById('document');
                const text = doc.textContent || doc.innerText || '';
                const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
                const chars = text.length;
                
                document.getElementById('word-count').textContent = words;
                document.getElementById('char-count').textContent = chars;
            }}
            
            function saveDocument() {{
                const doc = document.getElementById('document');
                const content = doc.innerHTML;
                
                // Create HTML file content
                const htmlContent = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Theta Document</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.5;
            max-width: 21cm;
            margin: 0 auto;
            padding: 2.5cm;
            background: white;
        }}
    </style>
</head>
<body>
    ${{content}}
</body>
</html>`;
                
                const blob = new Blob([htmlContent], {{ type: 'text/html' }});
                
                // Create download link
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `document_${{new Date().toISOString().slice(0,19).replace(/:/g,'-')}}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                alert('Document downloaded successfully!');
            }}
            
            // Initialize when page loads
            document.addEventListener('DOMContentLoaded', initEditor);
        </script>
    </body>
    </html>
    """
    
    # Create the component
    component_value = components.html(
        component_html,
        width=width + 50,
        height=height + 50
    )
    
    # Component doesn't return data due to Streamlit version compatibility
    return None 