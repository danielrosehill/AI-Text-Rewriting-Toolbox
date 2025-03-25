"""
Utility functions for the AI Text Transformer Toolbox.
"""

import os
import platform
import subprocess
from datetime import datetime

def get_desktop_path():
    """Get the path to the user's desktop."""
    return os.path.join(os.path.expanduser("~"), "Desktop")

def ensure_directory_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory

def generate_suggested_filename(text, extension="txt"):
    """Generate a suggested filename based on the content."""
    # Extract the first line or first few words
    first_line = text.split("\n", 1)[0].strip()
    
    # Limit to first 5 words
    words = first_line.split()[:5]
    filename_base = "_".join(words)
    
    # Clean the filename (remove special characters)
    filename_base = "".join(c if c.isalnum() or c == "_" else "_" for c in filename_base)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine and ensure it's not too long
    filename = f"{filename_base}_{timestamp}.{extension}"
    if len(filename) > 255:  # Max filename length for most filesystems
        filename = f"{filename_base[:50]}_{timestamp}.{extension}"
    
    return filename

def try_copy_to_clipboard(text):
    """
    Try to copy text to clipboard using platform-specific methods.
    Returns True if successful, False otherwise.
    """
    try:
        # For Linux
        if platform.system() == "Linux":
            # Try using xclip
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE, close_fds=True
            )
            process.communicate(input=text.encode('utf-8'))
            return process.returncode == 0
    except Exception:
        pass
    
    # If we get here, the platform-specific method failed or isn't implemented
    try:
        # Try using pyperclip as a fallback
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False

def try_paste_from_clipboard():
    """
    Try to paste text from clipboard using platform-specific methods.
    Returns the clipboard text if successful, None otherwise.
    """
    try:
        # For Linux
        if platform.system() == "Linux":
            # Try using xclip
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard', '-o'],
                stdout=subprocess.PIPE, close_fds=True
            )
            stdout, _ = process.communicate()
            if process.returncode == 0:
                return stdout.decode('utf-8')
    except Exception:
        pass
    
    # If we get here, the platform-specific method failed or isn't implemented
    try:
        # Try using pyperclip as a fallback
        import pyperclip
        return pyperclip.paste()
    except Exception:
        return None
