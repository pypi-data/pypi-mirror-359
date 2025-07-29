# textbuddy/__init__.py

from .utils import (
    format_rupee,
    standardize_indian_phone,
    parse_indian_date,
    clean_text_basic,
    remove_emoji,
    about # <--- This ensures the about() function is accessible
)

__all__ = [
    'format_rupee',
    'standardize_indian_phone',
    'parse_indian_date',
    'clean_text_basic',
    'remove_emoji',
    'about' # <--- This makes 'about' part of what's exposed by 'import *'
]

__version__ = "0.3.1" # <--- MAKE SURE THIS IS 0.1.3

# This message will print to the console when the package is first imported in a session
print(f"\n✨ Welcome to 'textbuddy' v{__version__}! ✨")
print("Developed by [Your Full Name Here].") # <--- Your name will show here
print("Simplifying text tasks for an Indian context. Happy coding!\n")