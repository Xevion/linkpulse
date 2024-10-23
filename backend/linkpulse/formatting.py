def pluralize(count: int) -> str:
    """
    Pluralize a word based on count.
    """
    return 's' if count != 1 else ''