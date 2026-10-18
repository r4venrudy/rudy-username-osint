def private_by_default(option):
    """Keep personal lookup results private unless the caller explicitly opts out."""
    return option is not False
