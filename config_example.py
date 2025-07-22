"""
Configuration example for Notetion workflow
Copy this to config.py and update with your settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Supported file types
SUPPORTED_FILE_TYPES = ['.txt', '.pdf', '.json']

# Default output settings
DEFAULT_OUTPUT_FILE = "generated_notes.md"

# LLM Configuration
LLM_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 4000
}

# File processing settings
MAX_FILE_SIZE_MB = 50
ENCODING = "utf-8"
