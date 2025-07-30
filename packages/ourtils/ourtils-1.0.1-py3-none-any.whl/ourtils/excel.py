"""
Anything to do with excel
"""


def excel_column_index(col_name: str) -> int:
    """
    Returns the column index (starting with 1) given an excel column name (e.g. "AA")
    - Thank you chatgpt
    """
    index = 0
    for char in col_name.upper():
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index


def index_to_excel_column(index: int) -> str:
    """
    Returns the excel column name based on an index (should start at 1)
    - Thank you chatgpt
    """
    if index < 1:
        raise ValueError("Index must be a positive integer.")

    column_name = []
    while index > 0:
        index -= 1  # Adjust for 0-based indexing
        column_name.append(chr(index % 26 + ord("A")))
        index //= 26

    return "".join(reversed(column_name))
