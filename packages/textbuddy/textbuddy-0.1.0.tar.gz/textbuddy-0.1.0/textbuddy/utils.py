# textbuddy/utils.py

import re # This line imports a special tool for searching patterns in text
from datetime import datetime # This line imports a tool for working with dates and times

# --- 1. Rupee Formatting ---
def format_rupee(amount, include_symbol=True):
    """
    Formats a number into Indian Rupees with comma separators (lakhs/crores).

    Args:
        amount (int or float): The number to format.
        include_symbol (bool): True if you want the '₹ ' symbol, False otherwise.

    Returns:
        str: The formatted rupee string.
    """
    # Convert the number to a string, handling decimals for floats
    if isinstance(amount, int):
        s = str(amount)
    else:
        s = f"{amount:,.2f}" # Format to 2 decimal places with default commas

    # Separate the integer part and decimal part
    if '.' in s:
        integer_part, decimal_part = s.split('.')
    else:
        integer_part, decimal_part = s, ''

    # Apply Indian comma system (e.g., 1,00,000 instead of 100,000)
    formatted_integer = ''
    n = len(integer_part)
    if n > 3:
        formatted_integer = integer_part[n-3:] # Take last three digits (e.g., 456)
        integer_part = integer_part[:n-3]     # Remaining digits (e.g., 123)
        # Loop to add commas every two digits for the remaining part
        while len(integer_part) > 2:
            formatted_integer = integer_part[-2:] + ',' + formatted_integer
            integer_part = integer_part[:-2]
    # Add the final remaining digits (if any) and combine
    formatted_integer = integer_part + (',' if integer_part and formatted_integer else '') + formatted_integer

    final_amount_str = formatted_integer
    if decimal_part:
        # Ensure decimal part always has 2 digits, padding with '0' if needed
        final_amount_str += '.' + decimal_part.ljust(2, '0') 

    # Add the Rupee symbol if requested
    if include_symbol:
        return '₹ ' + final_amount_str
    return final_amount_str

# --- 2. Indian Phone Number Standardization ---
def standardize_indian_phone(number_string, add_country_code=True):
    """
    Standardizes an Indian phone number to a consistent format.

    Args:
        number_string (str): The phone number string (e.g., "98765 43210", "09876543210").
        add_country_code (bool): True to add '+91' prefix, False otherwise.

    Returns:
        str: The standardized 10-digit phone number with or without '+91'.
             Returns None if the number cannot be recognized as a valid 10-digit Indian number.
    """
    # Remove any non-digit characters (spaces, hyphens, etc.)
    digits = re.sub(r'\D', '', number_string)

    # If it's an 11-digit number starting with '0', remove the '0'
    if len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]

    # Check if it's now exactly 10 digits long and contains only digits
    if len(digits) == 10 and digits.isdigit():
        if add_country_code:
            return '+91' + digits
        return digits
    return None # If it's not a valid 10-digit number, return None

# --- 3. Indian Date Parsing ---
def parse_indian_date(date_string, input_format='%d-%m-%Y'):
    """
    Parses an Indian date string into a datetime object.

    Args:
        date_string (str): The date string (e.g., '15-08-2024').
        input_format (str): The expected format of the input string.
                            Common formats: '%d-%m-%Y', '%d/%m/%Y', '%d %b %Y' (e.g., '15 Aug 2024')

    Returns:
        datetime.datetime: The parsed datetime object.
                           Returns None if the date string doesn't match the format.
    """
    try:
        # Try to convert the string to a date object using the specified format
        return datetime.strptime(date_string, input_format)
    except ValueError: # If the format doesn't match, an error occurs
        return None    # So we return None to indicate failure

# --- 4. Basic Text Cleaning ---
def clean_text_basic(text):
    """
    Performs basic text cleaning: removes extra spaces, leading/trailing whitespace.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned text.
    """
    # Ensure the input is treated as a string, even if it's a number
    if not isinstance(text, str):
        text = str(text) 

    # Replace sequences of one or more whitespace characters (spaces, tabs, newlines)
    # with a single space.
    cleaned_text = re.sub(r'\s+', ' ', text)

    # Remove any spaces at the very beginning or end of the text
    cleaned_text = cleaned_text.strip()
    return cleaned_text

# --- 5. Remove Emoji ---
def remove_emoji(text):
    """
    Removes emojis from a string.

    Args:
        text (str): The input text.

    Returns:
        str: The text without emojis.
    """
    if not isinstance(text, str):
        text = str(text)

    # This is a complex pattern (regex) that matches many common emojis.
    # It looks for specific unicode ranges where emojis are found.
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons like 🙂😂
        "\U0001F300-\U0001F5FF"  # symbols & pictographs like ☀️💡
        "\U0001F680-\U0001F6FF"  # transport & map symbols like 🚗✈️
        "\U0001F1E0-\U0001F1FF"  # flags (iOS) like 🇮🇳
        "\U00002702-\U000027B0"  # common dingbats like ✅✨
        "\U000024C2-\U0001F251"  # miscellaneous symbols
        "]+", flags=re.UNICODE # flags=re.UNICODE makes it work with unicode characters
    )
    return emoji_pattern.sub(r'', text) # Replace any found emoji with an empty string (remove them)