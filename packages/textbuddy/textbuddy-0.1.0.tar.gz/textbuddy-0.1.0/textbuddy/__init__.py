# textbuddy/__init__.py

# Import specific functions from the 'utils.py' file within this package.
# This makes them directly accessible when someone imports 'textbuddy'.
from .utils import ( # The '.' means "from a file within this same package"
    format_rupee,
    standardize_indian_phone,
    parse_indian_date,
    clean_text_basic,
    remove_emoji
)

# The __all__ variable controls what gets imported when someone uses `from textbuddy import *`.
# It's good practice to list your public functions here.
__all__ = [
    'format_rupee',
    'standardize_indian_phone',
    'parse_indian_date',
    'clean_text_basic',
    'remove_emoji'
]

# You can also set a version for your package here.
# This helps users know which version they have.
__version__ = "0.1.0"