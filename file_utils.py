"""
File utility module for the AI Text Transformer Toolbox.
Handles file reading, writing, and format conversions.
"""

import os
import io
import docx
import PyPDF2
import tempfile
from datetime import datetime


def read_text_file(file_obj):
    """Read text from a plain text file."""
    return file_obj.read().decode('utf-8')


def read_markdown_file(file_obj):
    """Read text from a markdown file."""
    return file_obj.read().decode('utf-8')


def read_docx_file(file_obj):
    """Read text from a DOCX file."""
    doc = docx.Document(file_obj)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def read_pdf_file(file_obj):
    """Read text from a PDF file."""
    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file_obj.read())
        temp_path = temp_file.name
    
    # Extract text from the PDF
    text = ""
    try:
        with open(temp_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    return text


def read_file(file_obj, file_type):
    """Read text from a file based on its type."""
    if file_type == "text/plain":
        return read_text_file(file_obj)
    elif file_type == "text/markdown":
        return read_markdown_file(file_obj)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx_file(file_obj)
    elif file_type == "application/pdf":
        return read_pdf_file(file_obj)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def generate_filename(text, extension="txt"):
    """Generate a filename based on the text content and current date/time."""
    # Get the first few words of the text (up to 5 words)
    words = text.split()[:5]
    title = "_".join(words).lower()
    
    # Remove special characters
    title = "".join(c if c.isalnum() or c == "_" else "" for c in title)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine title and timestamp
    filename = f"{title}_{timestamp}.{extension}"
    
    return filename


def save_text_to_file(text, filepath):
    """Save text to a file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    return filepath
