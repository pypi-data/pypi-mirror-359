"""
Theta Slide Editor - PowerPoint/Keynote-style visual editor
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from typing import Dict, List, Any, Optional

# Get the directory of this file
_COMPONENT_ROOT = os.path.dirname(os.path.abspath(__file__))
_COMPONENT_URL = None

def theta_slide_editor(
    slides: List[Dict[str, Any]] = None,
    width: int = 800,
    height: int = 600,
    key: str = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Create a PowerPoint/Keynote-style visual slide editor.
    
    Parameters:
    -----------
    slides : List[Dict[str, Any]]
        List of slide dictionaries with 'title' and content elements
    width : int
        Width of the editor in pixels
    height : int  
        Height of the editor in pixels
    key : str
        Unique key for the component
        
    Returns:
    --------
    List[Dict[str, Any]] or None
        Updated slides data or None if no changes
    """
    
    # Default slides if none provided
    if slides is None:
        slides = [
            {
                "id": "slide_1",
                "title": "Sample Slide",
                "elements": [
                    {
                        "type": "text",
                        "id": "text_1",
                        "content": "Click to edit text",
                        "x": 50,
                        "y": 100,
                        "width": 400,
                        "height": 100,
                        "fontSize": 18,
                        "fontFamily": "Arial",
                        "color": "#000000",
                        "bold": False,
                        "italic": False,
                        "underline": False
                    }
                ],
                "background": "#ffffff"
            }
        ]
    
    # Safety check: ensure slides is a proper list, not a DeltaGenerator
    if not isinstance(slides, list):
        # If it's not a list, reset to default to prevent JSON serialization errors
        slides = [
            {
                "id": "slide_1",
                "title": "Sample Slide",
                "elements": [
                    {
                        "type": "text",
                        "id": "text_1",
                        "content": "Click to edit text",
                        "x": 50,
                        "y": 100,
                        "width": 400,
                        "height": 100,
                        "fontSize": 18,
                        "fontFamily": "Arial",
                        "color": "#000000",
                        "bold": False,
                        "italic": False,
                        "underline": False
                    }
                ],
                "background": "#ffffff"
            }
        ]
    
    # Component HTML/CSS/JS
    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Theta Slide Editor</title>
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
                height: 50px;
                background: #2d3748;
                border-radius: 8px 8px 0 0;
                display: flex;
                align-items: center;
                padding: 0 15px;
                gap: 10px;
            }}
            
            .toolbar button {{
                background: #4a5568;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }}
            
            .toolbar button:hover {{
                background: #718096;
            }}
            
            .toolbar button.active {{
                background: #3182ce;
            }}
            
            .editor-main {{
                flex: 1;
                display: flex;
            }}
            
            .slide-thumbnails {{
                width: 150px;
                background: #e2e8f0;
                border-right: 1px solid #cbd5e0;
                overflow-y: auto;
                padding: 10px;
            }}
            
            .slide-thumbnail {{
                width: 130px;
                height: 90px;
                background: white;
                border: 2px solid #cbd5e0;
                border-radius: 4px;
                margin-bottom: 10px;
                cursor: pointer;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                color: #666;
            }}
            
            .slide-thumbnail.active {{
                border-color: #3182ce;
            }}
            
            .slide-canvas {{
                flex: 1;
                background: #f7fafc;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            }}
            
            .slide-area {{
                width: 500px;
                height: 375px;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                position: relative;
                overflow: hidden;
            }}
            
            .slide-element {{
                position: absolute;
                border: 2px solid transparent;
                cursor: move;
                user-select: none;
            }}
            
            .slide-element.selected {{
                border-color: #3182ce;
            }}
            
            .slide-element.text-element {{
                padding: 5px;
                background: rgba(255,255,255,0.9);
                border-radius: 2px;
            }}
            
            .slide-element.text-element:focus {{
                outline: none;
                background: white;
            }}
            
            .resize-handle {{
                position: absolute;
                width: 8px;
                height: 8px;
                background: #3182ce;
                border: 1px solid white;
                border-radius: 2px;
            }}
            
            .resize-handle.nw {{ top: -4px; left: -4px; cursor: nw-resize; }}
            .resize-handle.ne {{ top: -4px; right: -4px; cursor: ne-resize; }}
            .resize-handle.sw {{ bottom: -4px; left: -4px; cursor: sw-resize; }}
            .resize-handle.se {{ bottom: -4px; right: -4px; cursor: se-resize; }}
            
            .properties-panel {{
                width: 200px;
                background: #f7fafc;
                border-left: 1px solid #e2e8f0;
                padding: 15px;
                overflow-y: auto;
            }}
            
            .property-group {{
                margin-bottom: 20px;
            }}
            
            .property-group h4 {{
                margin: 0 0 10px 0;
                font-size: 12px;
                font-weight: 600;
                color: #2d3748;
                text-transform: uppercase;
            }}
            
            .property-row {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                gap: 8px;
            }}
            
            .property-row label {{
                font-size: 11px;
                color: #4a5568;
                flex: 1;
            }}
            
            .property-row input, .property-row select {{
                flex: 1;
                padding: 4px 6px;
                border: 1px solid #e2e8f0;
                border-radius: 3px;
                font-size: 11px;
            }}
            
            .color-input {{
                width: 30px !important;
                height: 24px;
                padding: 0;
                border: none;
                border-radius: 3px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="editor-container">
            <!-- Toolbar -->
            <div class="toolbar">
                <button id="add-text" title="Add Text">T</button>
                <button id="add-image" title="Add Image">📷</button>
                <button id="add-shape" title="Add Shape">⬜</button>
                <button id="delete-element" title="Delete">🗑️</button>
                <div style="flex: 1;"></div>
                <button id="save-slides">Save Changes</button>
            </div>
            
            <!-- Main Editor -->
            <div class="editor-main">
                <!-- Slide Thumbnails -->
                <div class="slide-thumbnails">
                    <div id="slide-list"></div>
                    <button id="add-slide" style="width: 100%; padding: 10px; background: #3182ce; color: white; border: none; border-radius: 4px; cursor: pointer;">+ Add Slide</button>
                </div>
                
                <!-- Slide Canvas -->
                <div class="slide-canvas">
                    <div class="slide-area" id="slide-area"></div>
                </div>
                
                <!-- Properties Panel -->
                <div class="properties-panel" id="properties-panel">
                    <div class="property-group">
                        <h4>Element Properties</h4>
                        <div id="element-properties">
                            <p style="color: #718096; font-size: 11px;">Select an element to edit properties</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Theta Slide Editor JavaScript
            let slides = {json.dumps(slides)};
            let currentSlideIndex = 0;
            let selectedElement = null;
            let isDragging = false;
            let isResizing = false;
            let dragStart = {{}};
            let elementIdCounter = 1;
            
            // Initialize editor
            function initEditor() {{
                renderSlideThumbnails();
                selectSlide(0);
                setupEventListeners();
            }}
            
            function renderSlideThumbnails() {{
                const slideList = document.getElementById('slide-list');
                slideList.innerHTML = '';
                
                slides.forEach((slide, index) => {{
                    const thumbnail = document.createElement('div');
                    thumbnail.className = 'slide-thumbnail';
                    if (index === currentSlideIndex) thumbnail.classList.add('active');
                    thumbnail.textContent = `Slide ${{index + 1}}`;
                    thumbnail.onclick = () => selectSlide(index);
                    slideList.appendChild(thumbnail);
                }});
            }}
            
            function selectSlide(index) {{
                currentSlideIndex = index;
                renderSlideThumbnails();
                renderSlideCanvas();
                clearSelection();
            }}
            
            function renderSlideCanvas() {{
                const slideArea = document.getElementById('slide-area');
                const slide = slides[currentSlideIndex];
                
                slideArea.innerHTML = '';
                slideArea.style.background = slide.background || '#ffffff';
                
                slide.elements.forEach(element => {{
                    const elementDiv = createElementDiv(element);
                    slideArea.appendChild(elementDiv);
                }});
            }}
            
            function createElementDiv(element) {{
                const div = document.createElement('div');
                div.className = 'slide-element';
                div.dataset.elementId = element.id;
                div.style.left = element.x + 'px';
                div.style.top = element.y + 'px';
                div.style.width = element.width + 'px';
                div.style.height = element.height + 'px';
                
                if (element.type === 'text') {{
                    div.classList.add('text-element');
                    div.contentEditable = true;
                    div.textContent = element.content;
                    div.style.fontSize = element.fontSize + 'px';
                    div.style.fontFamily = element.fontFamily;
                    div.style.color = element.color;
                    div.style.fontWeight = element.bold ? 'bold' : 'normal';
                    div.style.fontStyle = element.italic ? 'italic' : 'normal';
                    div.style.textDecoration = element.underline ? 'underline' : 'none';
                }}
                
                div.onclick = (e) => {{
                    e.stopPropagation();
                    selectElement(div);
                }};
                
                return div;
            }}
            
            function selectElement(elementDiv) {{
                clearSelection();
                selectedElement = elementDiv;
                elementDiv.classList.add('selected');
                addResizeHandles(elementDiv);
                updatePropertiesPanel();
            }}
            
            function clearSelection() {{
                document.querySelectorAll('.slide-element').forEach(el => {{
                    el.classList.remove('selected');
                }});
                document.querySelectorAll('.resize-handle').forEach(handle => {{
                    handle.remove();
                }});
                selectedElement = null;
                updatePropertiesPanel();
            }}
            
            function addResizeHandles(elementDiv) {{
                ['nw', 'ne', 'sw', 'se'].forEach(position => {{
                    const handle = document.createElement('div');
                    handle.className = `resize-handle ${{position}}`;
                    elementDiv.appendChild(handle);
                }});
            }}
            
            function updatePropertiesPanel() {{
                const panel = document.getElementById('element-properties');
                
                if (!selectedElement) {{
                    panel.innerHTML = '<p style="color: #718096; font-size: 11px;">Select an element to edit properties</p>';
                    return;
                }}
                
                const elementId = selectedElement.dataset.elementId;
                const element = getCurrentSlide().elements.find(el => el.id === elementId);
                
                if (element.type === 'text') {{
                    panel.innerHTML = `
                        <div class="property-row">
                            <label>Font Size:</label>
                            <input type="number" id="font-size" value="${{element.fontSize}}" min="8" max="72">
                        </div>
                        <div class="property-row">
                            <label>Font:</label>
                            <select id="font-family">
                                <option value="Arial" ${{element.fontFamily === 'Arial' ? 'selected' : ''}}>Arial</option>
                                <option value="Times New Roman" ${{element.fontFamily === 'Times New Roman' ? 'selected' : ''}}>Times</option>
                                <option value="Helvetica" ${{element.fontFamily === 'Helvetica' ? 'selected' : ''}}>Helvetica</option>
                            </select>
                        </div>
                        <div class="property-row">
                            <label>Color:</label>
                            <input type="color" id="text-color" class="color-input" value="${{element.color}}">
                        </div>
                        <div class="property-row">
                            <label><input type="checkbox" id="bold" ${{element.bold ? 'checked' : ''}}> Bold</label>
                        </div>
                        <div class="property-row">
                            <label><input type="checkbox" id="italic" ${{element.italic ? 'checked' : ''}}> Italic</label>
                        </div>
                        <div class="property-row">
                            <label><input type="checkbox" id="underline" ${{element.underline ? 'checked' : ''}}> Underline</label>
                        </div>
                    `;
                    
                    // Add event listeners for property changes
                    document.getElementById('font-size').onchange = updateElementProperty;
                    document.getElementById('font-family').onchange = updateElementProperty;
                    document.getElementById('text-color').onchange = updateElementProperty;
                    document.getElementById('bold').onchange = updateElementProperty;
                    document.getElementById('italic').onchange = updateElementProperty;
                    document.getElementById('underline').onchange = updateElementProperty;
                }}
            }}
            
            function updateElementProperty() {{
                if (!selectedElement) return;
                
                const elementId = selectedElement.dataset.elementId;
                const element = getCurrentSlide().elements.find(el => el.id === elementId);
                
                if (element.type === 'text') {{
                    element.fontSize = parseInt(document.getElementById('font-size').value);
                    element.fontFamily = document.getElementById('font-family').value;
                    element.color = document.getElementById('text-color').value;
                    element.bold = document.getElementById('bold').checked;
                    element.italic = document.getElementById('italic').checked;
                    element.underline = document.getElementById('underline').checked;
                    
                    // Update the element display
                    selectedElement.style.fontSize = element.fontSize + 'px';
                    selectedElement.style.fontFamily = element.fontFamily;
                    selectedElement.style.color = element.color;
                    selectedElement.style.fontWeight = element.bold ? 'bold' : 'normal';
                    selectedElement.style.fontStyle = element.italic ? 'italic' : 'normal';
                    selectedElement.style.textDecoration = element.underline ? 'underline' : 'none';
                }}
            }}
            
            function getCurrentSlide() {{
                return slides[currentSlideIndex];
            }}
            
            function addTextElement() {{
                const element = {{
                    type: 'text',
                    id: `text_${{elementIdCounter++}}`,
                    content: 'Click to edit text',
                    x: 50,
                    y: 50,
                    width: 200,
                    height: 50,
                    fontSize: 18,
                    fontFamily: 'Arial',
                    color: '#000000',
                    bold: false,
                    italic: false,
                    underline: false
                }};
                
                getCurrentSlide().elements.push(element);
                renderSlideCanvas();
            }}
            
            function deleteSelectedElement() {{
                if (!selectedElement) return;
                
                const elementId = selectedElement.dataset.elementId;
                const slide = getCurrentSlide();
                slide.elements = slide.elements.filter(el => el.id !== elementId);
                
                clearSelection();
                renderSlideCanvas();
            }}
            
            function addSlide() {{
                const newSlide = {{
                    id: `slide_${{slides.length + 1}}`,
                    title: `Slide ${{slides.length + 1}}`,
                    elements: [],
                    background: '#ffffff'
                }};
                
                slides.push(newSlide);
                renderSlideThumbnails();
                selectSlide(slides.length - 1);
            }}
            
            function saveSlides() {{
                // Create JSON file content
                const slideData = {{
                    title: "Theta Presentation",
                    slides: slides,
                    created: new Date().toISOString(),
                    version: "1.0.0"
                }};
                
                const jsonContent = JSON.stringify(slideData, null, 2);
                const blob = new Blob([jsonContent], {{ type: 'application/json' }});
                
                // Create download link
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `presentation_${{new Date().toISOString().slice(0,19).replace(/:/g,'-')}}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                alert('Presentation downloaded successfully!');
            }}
            
            function setupEventListeners() {{
                document.getElementById('add-text').onclick = addTextElement;
                document.getElementById('delete-element').onclick = deleteSelectedElement;
                document.getElementById('add-slide').onclick = addSlide;
                document.getElementById('save-slides').onclick = saveSlides;
                
                // Click outside to deselect
                document.getElementById('slide-area').onclick = (e) => {{
                    if (e.target.id === 'slide-area') {{
                        clearSelection();
                    }}
                }};
                
                // Handle text editing
                document.addEventListener('input', (e) => {{
                    if (e.target.classList.contains('text-element')) {{
                        const elementId = e.target.dataset.elementId;
                        const element = getCurrentSlide().elements.find(el => el.id === elementId);
                        if (element) {{
                            element.content = e.target.textContent;
                        }}
                    }}
                }});
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
    
    return component_value 