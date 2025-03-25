"""
AI Text Transformer Toolbox

A Linux-based application that allows users to apply various text transformations
using a local large language model (LLM) via the Ollama API.
"""

import os
import streamlit as st
import json
from datetime import datetime
import time

# Import custom modules
import config
import file_utils
import ollama_api
import prompt_utils
import utils


# Initialize session state variables if they don't exist
def init_session_state():
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    if "output_text" not in st.session_state:
        st.session_state.output_text = ""
    if "selected_transformations" not in st.session_state:
        # Load from preferences
        preferences = config.load_preferences()
        st.session_state.selected_transformations = preferences.get("last_used_transformations", ["basic_cleanup"])
    if "search_term" not in st.session_state:
        st.session_state.search_term = ""
    if "ollama_model" not in st.session_state:
        # Load from preferences
        preferences = config.load_preferences()
        st.session_state.ollama_model = preferences.get("model", "llama3")
    if "download_path" not in st.session_state:
        preferences = config.load_preferences()
        st.session_state.download_path = preferences.get("download_path", utils.get_desktop_path())
    if "available_models" not in st.session_state:
        st.session_state.available_models = []
    if "prompts_data" not in st.session_state:
        st.session_state.prompts_data = prompt_utils.load_prompts()
    if "suggested_filename" not in st.session_state:
        st.session_state.suggested_filename = "transformed_text.txt"
    if "ollama_error" not in st.session_state:
        st.session_state.ollama_error = None
    if "transformation_success" not in st.session_state:
        st.session_state.transformation_success = False
    if "transformation_categories" not in st.session_state:
        st.session_state.transformation_categories = {}


# Apply text transformations using Ollama API
def transform_text():
    if not st.session_state.input_text:
        st.warning("Please enter some text to transform.")
        return
    
    with st.spinner("Transforming text..."):
        # Get selected transformation prompts
        selected_prompts = []
        for prompt_id in st.session_state.selected_transformations:
            prompt_text = prompt_utils.get_prompt_text(prompt_id, st.session_state.prompts_data)
            if prompt_text:
                selected_prompts.append(prompt_text)
        
        # If no transformations selected, use default
        if not selected_prompts:
            default_prompt = prompt_utils.get_default_prompt()
            selected_prompts.append(default_prompt["prompt"])
        
        # Concatenate prompts
        system_prompt = ollama_api.concatenate_prompts(selected_prompts)
        
        # Initialize Ollama API client
        client = ollama_api.OllamaAPI()
        
        try:
            # Generate transformed text
            transformed_text = client.generate_text(
                model=st.session_state.ollama_model,
                prompt=st.session_state.input_text,
                system_prompt=system_prompt
            )
            
            # Update output text
            st.session_state.output_text = transformed_text
            
            # Generate suggested filename
            st.session_state.suggested_filename = utils.generate_suggested_filename(transformed_text)
            
            # Save selected transformations to preferences
            config.update_preference("last_used_transformations", st.session_state.selected_transformations)
            
            # Clear any previous errors
            st.session_state.ollama_error = None
            
            # Set success flag
            st.session_state.transformation_success = True
            
        except Exception as e:
            st.session_state.ollama_error = str(e)
            st.error(f"Error transforming text: {str(e)}")
            st.session_state.transformation_success = False


# Handle file upload
def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            # Determine file type
            file_type = uploaded_file.type
            
            # Read file content
            text = file_utils.read_file(uploaded_file, file_type)
            
            # Update input text
            st.session_state.input_text = text
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")


# Save output text to file
def save_output_text(filename=None):
    if not st.session_state.output_text:
        st.warning("No transformed text to save.")
        return
    
    # Use provided filename or the suggested one
    if not filename:
        filename = st.session_state.suggested_filename
    
    # Ensure download directory exists
    utils.ensure_directory_exists(st.session_state.download_path)
    
    # Create full path
    filepath = os.path.join(st.session_state.download_path, filename)
    
    try:
        # Save text to file
        file_utils.save_text_to_file(st.session_state.output_text, filepath)
        st.success(f"Saved to: {filepath}")
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")


# Clear all fields
def clear_all():
    st.session_state.input_text = ""
    st.session_state.output_text = ""
    st.session_state.selected_transformations = ["basic_cleanup"]
    st.session_state.suggested_filename = "transformed_text.txt"
    st.session_state.transformation_success = False


# Check Ollama connection and update available models
def check_ollama_connection():
    client = ollama_api.OllamaAPI()
    if client.check_connection():
        # Update available models
        models = client.list_models()
        if not models:
            models = ["llama3"]  # Default if no models found
        st.session_state.available_models = models
        st.session_state.ollama_error = None
        return True
    else:
        st.session_state.ollama_error = "Cannot connect to Ollama API. Please ensure Ollama is installed and running."
        return False


# Handle clipboard paste
def handle_clipboard_paste():
    clipboard_text = utils.try_paste_from_clipboard()
    if clipboard_text:
        st.session_state.input_text = clipboard_text
        return True
    else:
        st.warning("Could not paste from clipboard. Make sure you have text copied and required dependencies installed.")
        return False


# Handle clipboard copy
def handle_clipboard_copy():
    if st.session_state.output_text:
        success = utils.try_copy_to_clipboard(st.session_state.output_text)
        if success:
            st.success("Copied to clipboard!")
        else:
            st.warning("Could not copy to clipboard. Make sure required dependencies are installed.")
    else:
        st.warning("No text to copy.")


# Categorize prompts for better organization
def categorize_prompts(prompts_data):
    categories = {
        "General": [],
        "Format Conversion": [],
        "Style": [],
        "Professional": [],
        "Academic": [],
        "Creative": [],
        "Technical": [],
        "Social Media": [],
        "Prompting": [],
        "Other": []
    }
    
    # Map prompts to categories based on keywords in name or description
    for prompt_id, prompt_data in prompts_data.items():
        name = prompt_data.get("name", "").lower()
        description = prompt_data.get("description", "").lower()
        
        if any(word in name or word in description for word in ["cleanup", "extract", "anonymization", "bullet", "summary"]):
            categories["General"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["email", "letter", "minutes", "documentation", "status", "responder"]):
            categories["Professional"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["academic", "scientific", "paper"]):
            categories["Academic"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["blog", "social", "media"]):
            categories["Social Media"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["poetry", "poem", "shakespeare", "tolkien", "creative"]):
            categories["Creative"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["code", "technical", "development", "software"]):
            categories["Technical"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["format", "convert", "transform"]):
            categories["Format Conversion"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["tone", "style", "formal", "casual"]):
            categories["Style"].append((prompt_id, prompt_data.get("name", "Unknown")))
        elif any(word in name or word in description for word in ["prompt", "chatgpt", "ai"]):
            categories["Prompting"].append((prompt_id, prompt_data.get("name", "Unknown")))
        else:
            categories["Other"].append((prompt_id, prompt_data.get("name", "Unknown")))
    
    # Sort each category alphabetically by name
    for category in categories:
        categories[category].sort(key=lambda x: x[1])
    
    return categories


# Main application
def main():
    st.set_page_config(
        page_title="AI Text Transformer Toolbox",
        page_icon="📝",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Application title
    st.title("AI Text Transformer Toolbox")
    
    # Application description
    st.markdown(
        """
        A simple GUI interface for applying a wide variety of short system prompts to text in order to modify it for 
        multiple formatting and stylistic edits. The underlying mode of operation is concatenating multiple short 
        system prompts, applying it and then gathering the output suitable for text editing, reformatting purposes.
        """
    )
    
    # Check Ollama connection
    ollama_connected = check_ollama_connection()
    if st.session_state.ollama_error:
        st.error(
            f"{st.session_state.ollama_error} "
            "Visit https://ollama.com/ for installation instructions."
        )
    
    # Create three columns for the interface
    col1, col2, col3 = st.columns([3, 2, 3])
    
    # Left column (Input)
    with col1:
        st.header("Input Text")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload a file (TXT, Markdown, DOCX, PDF)",
            type=["txt", "md", "docx", "pdf"]
        )
        if uploaded_file:
            handle_file_upload(uploaded_file)
        
        # Input buttons row
        input_col1, input_col2 = st.columns(2)
        with input_col1:
            # Paste button
            if st.button("📋 Paste from Clipboard"):
                handle_clipboard_paste()
        
        with input_col2:
            # Clear input button
            if st.button("🧹 Clear Input"):
                st.session_state.input_text = ""
        
        # Input text area
        st.session_state.input_text = st.text_area(
            "Enter or paste text here:",
            value=st.session_state.input_text,
            height=400
        )
    
    # Middle column (Transformation Selector)
    with col2:
        st.header("Transformations")
        
        # Model selection
        model_options = st.session_state.available_models
        
        selected_model = st.selectbox(
            "Select LLM Model:",
            options=model_options,
            index=model_options.index(st.session_state.ollama_model) if st.session_state.ollama_model in model_options else 0
        )
        
        # Update model preference if changed
        if selected_model != st.session_state.ollama_model:
            st.session_state.ollama_model = selected_model
            config.update_preference("model", selected_model)
        
        # Prominent Transform button at the top
        transform_col1, transform_col2 = st.columns([3, 1])
        with transform_col1:
            if st.button("🔄 Transform Text", disabled=not ollama_connected, use_container_width=True, type="primary"):
                transform_text()
        
        # Display success message if transformation was successful
        if st.session_state.transformation_success:
            st.success("Text transformed successfully!")
            # Reset success flag after displaying
            st.session_state.transformation_success = False
        
        # Search box for transformations
        search_term = st.text_input(
            "Search transformations:",
            value=st.session_state.search_term
        )
        
        # Update search term in session state
        if search_term != st.session_state.search_term:
            st.session_state.search_term = search_term
        
        # Filter prompts based on search term
        filtered_prompts = prompt_utils.filter_prompts(
            st.session_state.prompts_data,
            st.session_state.search_term
        )
        
        # Categorize prompts for better organization
        if not st.session_state.search_term:
            # Only categorize when not searching
            if not st.session_state.transformation_categories:
                st.session_state.transformation_categories = categorize_prompts(st.session_state.prompts_data)
            categories = st.session_state.transformation_categories
            
            # Display transformations by category
            st.write("Select transformations (up to 10):")
            
            # Create a container with scrollable height
            transformation_container = st.container()
            selected_transformations = []
            
            with transformation_container:
                # Create tabs for categories
                category_tabs = st.tabs(list(categories.keys()))
                
                # Display transformations in each category tab
                for i, (category, tab) in enumerate(zip(categories.keys(), category_tabs)):
                    with tab:
                        for prompt_id, prompt_name in categories[category]:
                            # Check if this prompt is already selected
                            is_selected = prompt_id in st.session_state.selected_transformations
                            
                            # Create checkbox
                            selected = st.checkbox(
                                prompt_name,
                                value=is_selected,
                                key=f"checkbox_{prompt_id}"
                            )
                            
                            # Add to selected transformations if checked
                            if selected:
                                selected_transformations.append(prompt_id)
        else:
            # When searching, display flat list of filtered results
            prompt_options = prompt_utils.get_prompt_names_and_ids(filtered_prompts)
            
            # Display transformation options
            st.write("Select transformations (up to 10):")
            
            # Create a container with scrollable height
            transformation_container = st.container()
            selected_transformations = []
            
            # Display transformations in the scrollable container
            with transformation_container:
                # Create checkboxes for each transformation
                for prompt_id, prompt_name in prompt_options:
                    # Check if this prompt is already selected
                    is_selected = prompt_id in st.session_state.selected_transformations
                    
                    # Create checkbox
                    selected = st.checkbox(
                        prompt_name,
                        value=is_selected,
                        key=f"checkbox_{prompt_id}"
                    )
                    
                    # Add to selected transformations if checked
                    if selected:
                        selected_transformations.append(prompt_id)
        
        # Limit to 10 transformations
        if len(selected_transformations) > 10:
            st.warning("You can select up to 10 transformations. Only the first 10 will be applied.")
            selected_transformations = selected_transformations[:10]
        
        # Update selected transformations in session state
        st.session_state.selected_transformations = selected_transformations
    
    # Right column (Output)
    with col3:
        st.header("Output Text")
        
        # Output text area
        st.session_state.output_text = st.text_area(
            "Transformed text:",
            value=st.session_state.output_text,
            height=400
        )
        
        # Output buttons row
        output_col1, output_col2 = st.columns(2)
        with output_col1:
            # Copy to clipboard button
            if st.button("📋 Copy to Clipboard"):
                handle_clipboard_copy()
        
        with output_col2:
            # Clear output button
            if st.button("🧹 Clear Output"):
                st.session_state.output_text = ""
        
        # Download section
        st.subheader("Download Output")
        
        # Filename input
        filename = st.text_input(
            "Filename:",
            value=st.session_state.suggested_filename
        )
        
        # Download path
        download_path = st.text_input(
            "Download path:",
            value=st.session_state.download_path
        )
        
        # Update download path if changed
        if download_path != st.session_state.download_path:
            st.session_state.download_path = download_path
            config.update_preference("download_path", download_path)
        
        # Download button
        if st.button("💾 Download Output"):
            save_output_text(filename)
    
    # Bottom section for additional controls
    st.markdown("---")
    
    # Clear all button
    if st.button("🧹 Clear All Fields"):
        clear_all()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**AI Text Transformer Toolbox** | Using Ollama for local LLM processing | "
        f"Connected to Ollama: {'✅' if ollama_connected else '❌'}"
    )


if __name__ == "__main__":
    main()
