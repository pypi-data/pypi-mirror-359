# textbuddy/utils.py

# ... (all your other imports, if any) ...

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


# --- Corrected about() function ---
def about():
    """
    Prints information about the textbuddy package and its author.
    Users can call this function to learn more.
    """
    package_version_str = "0.3.1" # <--- MAKE SURE THIS IS 0.1.3
    author_name = "Amit Dutta" # <--- Your name will show here
    github_link = "https://github.com/notamitgamer" # <--- UPDATE THIS TO YOUR GITHUB LINK

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