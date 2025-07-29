def true_value(value):
    """
    Returns the value as the bid

    Parameters
    ----------
    value: float
        The value of the good being auctioned.

    Returns
    -------
    float
    """
    return value


def create_shaded_bid_map(shade):
    """
    Returns a function that maps a value to shade * value

    Parameters
    ----------
    shade: float
        A scaling parameter, usually between 0 and 1.
    Returns
    -------
    func
    """

    def bid_map(value):
        return shade * value

    return bid_map
