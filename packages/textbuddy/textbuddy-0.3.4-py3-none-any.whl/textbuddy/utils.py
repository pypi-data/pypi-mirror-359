# textbuddy/utils.py

import re
from datetime import datetime

# --- CORRECTED format_rupee function ---
def format_rupee(amount, include_symbol=True):
    """
    Formats a number into Indian Rupees with comma separators (lakhs/crores).
    Handles both positive and negative numbers, and ensures two decimal places.

    Args:
        amount (int or float): The number to format.
        include_symbol (bool): True if you want the '₹ ' symbol, False otherwise.

    Returns:
        str: The formatted rupee string.
    """
    # Handle sign separately
    sign = ""
    if amount < 0:
        sign = "-"
        amount = abs(amount) # Work with the absolute value for formatting

    # Format to 2 decimal places as a string
    s = f"{amount:.2f}"
    parts = s.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else '00' # Ensure two decimals

    n = len(integer_part)
    if n <= 3:
        # For numbers like 1, 10, 100, 1000
        formatted_integer = integer_part
    else:
        # Take the last three digits for the first comma group
        last_three = integer_part[n-3:]
        # The remaining part of the number
        rest = integer_part[:n-3]

        formatted_rest_parts = []
        # Loop to group remaining digits by two (for lakhs, crores)
        while len(rest) > 0:
            if len(rest) >= 2:
                formatted_rest_parts.append(rest[-2:]) # Take last two digits
                rest = rest[:-2] # Remove them from the rest
            else: # If only one digit remains
                formatted_rest_parts.append(rest)
                rest = '' # Clear rest

        # Join the reversed two-digit groups with commas, then add the last three digits
        formatted_integer = ','.join(reversed(formatted_rest_parts)) + ',' + last_three

    # Combine integer and decimal parts
    result = f"{formatted_integer}.{decimal_part}"

    # Add symbol and sign
    if include_symbol:
        return f"{sign}₹ {result}"
    return f"{sign}{result}"

# --- standardize_indian_phone function ---
def standardize_indian_phone(phone_number_str, add_country_code=True):
    """
    Standardizes Indian phone numbers to a consistent format.
    Removes spaces, hyphens, and optionally adds the +91 country code.

    Args:
        phone_number_str (str): The phone number string to standardize.
        add_country_code (bool): If True, prepends '+91' to the number.

    Returns:
        str or None: The standardized phone number as a string, or None if invalid.
    """
    # Remove any non-digit characters
    cleaned_number = re.sub(r'\D', '', str(phone_number_str))

    # Remove leading '0' if present, but only if it's 10 or 11 digits long
    if len(cleaned_number) == 11 and cleaned_number.startswith('0'):
        cleaned_number = cleaned_number[1:]

    # Check if the number is exactly 10 digits after cleaning
    if len(cleaned_number) != 10:
        return None  # Not a valid 10-digit Indian phone number

    if add_country_code:
        return f"+91{cleaned_number}"
    return cleaned_number

# --- parse_indian_date function ---
def parse_indian_date(date_string, input_format='%d-%m-%Y'):
    """
    Parses an Indian date string into a datetime object.

    Args:
        date_string (str): The date string to parse.
        input_format (str): The format of the input date string (e.g., '%d-%m-%Y', '%d/%m/%Y').

    Returns:
        datetime.datetime or None: The parsed datetime object, or None if parsing fails.
    """
    try:
        return datetime.strptime(date_string, input_format)
    except ValueError:
        return None

# --- clean_text_basic function ---
def clean_text_basic(text_string):
    """
    Performs basic text cleaning: removes extra spaces, newlines, and strips leading/trailing whitespace.

    Args:
        text_string (str): The input text string.

    Returns:
        str: The cleaned text string.
    """
    # Replace multiple spaces/newlines/tabs with a single space
    cleaned_text = re.sub(r'\s+', ' ', text_string).strip()
    return cleaned_text

# --- remove_emoji function ---
def remove_emoji(text_string):
    """
    Removes emojis from a string.

    Args:
        text_string (str): The input text string.

    Returns:
        str: The text string with emojis removed.
    """
    # Regex to match most common emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text_string)

# --- Corrected about() function ---
def about():
    """
    Prints information about the textbuddy package and its author.
    Users can call this function to learn more.
    """
    package_version_str = "0.3.4" # <--- MAKE SURE THIS IS 0.3.1
    author_name = "Amit Dutta" # <--- Your name will show here
    github_link = "https://github.com/notamitgamer/" # <--- UPDATE THIS TO YOUR GITHUB LINK

    print("\n--------------------------------------------------")
    print(f"📦 textbuddy Package Information 📦")
    print("--------------------------------------------------")
    print(f"Version: {package_version_str}")
    print("Description: Simple string and text utilities for Indian contexts.")
    print(f"\n✨ Developed with ❤️ by {author_name} ✨")
    print("I hope this package proves useful in your Python journey!")
    print(f"For more details, source code, and to report issues, visit:")
    print(f"➡️ {github_link}")
    print("--------------------------------------------------\n")