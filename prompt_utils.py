"""
Prompt utilities module for the AI Text Transformer Toolbox.
Handles loading, filtering, and managing transformation prompts.
"""

import os
import json


def load_prompts(prompts_file="default_prompts.json"):
    """Load transformation prompts from a JSON file."""
    try:
        with open(prompts_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading prompts: {e}")
        return {}


def get_prompt_by_id(prompt_id, prompts_data):
    """Get a specific prompt by its ID."""
    return prompts_data.get(prompt_id, {})


def get_prompt_text(prompt_id, prompts_data):
    """Get the prompt text for a specific prompt ID."""
    prompt_data = get_prompt_by_id(prompt_id, prompts_data)
    return prompt_data.get("prompt", "")


def get_default_prompt():
    """Get the default transformation prompt."""
    return {
        "name": "Basic Cleanup",
        "prompt": "Take the following text and refine it to add missing punctuation, resolve typos, add paragraph spacing, and generally enhance the presentation of the text while preserving the original meaning.",
        "requires_json": False,
        "description": "Transforms text using basic cleanup style or format"
    }


def filter_prompts(prompts_data, search_term=""):
    """Filter prompts based on a search term."""
    if not search_term:
        return prompts_data
    
    search_term = search_term.lower()
    filtered = {}
    
    for prompt_id, prompt_data in prompts_data.items():
        name = prompt_data.get("name", "").lower()
        description = prompt_data.get("description", "").lower()
        
        if search_term in name or search_term in description or search_term in prompt_id.lower():
            filtered[prompt_id] = prompt_data
    
    return filtered


def get_prompt_names_and_ids(prompts_data):
    """Get a list of prompt names and their IDs."""
    return [(prompt_id, data.get("name", "Unknown")) for prompt_id, data in prompts_data.items()]
