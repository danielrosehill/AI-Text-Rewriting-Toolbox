"""
Ollama API module for the AI Text Transformer Toolbox.
Handles interactions with the Ollama API for text transformations.
"""

import requests
import json


class OllamaAPI:
    def __init__(self, base_url="http://localhost:11434"):
        """Initialize the Ollama API client."""
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def list_models(self):
        """List available models from Ollama."""
        try:
            response = requests.get(f"{self.api_url}/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                return []
        except requests.RequestException:
            return []
    
    def generate_text(self, model, prompt, system_prompt=None, temperature=0.7):
        """Generate text using the specified model and prompt."""
        url = f"{self.api_url}/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                return f"Failed to generate text. {error_msg}"
        except requests.RequestException as e:
            return f"Failed to connect to Ollama API: {str(e)}"
    
    def check_connection(self):
        """Check if Ollama API is accessible."""
        try:
            response = requests.get(f"{self.base_url}/")
            return response.status_code == 200
        except requests.RequestException:
            return False


def concatenate_prompts(prompts):
    """Concatenate multiple prompts into a single system prompt."""
    if not prompts:
        return ""
    
    # Join all prompts with a separator
    concatenated = "\n\n".join(prompts)
    
    # Add a final instruction to ensure the model processes all transformations
    final_instruction = "\nApply ALL of the above transformations to the user's input text."
    
    return concatenated + final_instruction
