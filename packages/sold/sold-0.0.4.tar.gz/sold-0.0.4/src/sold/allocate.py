import numpy as np


def first_price(bids):
    """
    Returns an allocation giving the item to the highest bid.

    Note that in the case of ties it returns the first highest bid.

    Parameters
    ----------
    bids: iterable
        The collection of bids

    Returns
    -------
    np array
    """
    bids = np.array(bids)
    first_price = np.max(bids)
    winner_index = np.where(bids == first_price)[0][0]
    allocation = np.zeros_like(bids)
    allocation[winner_index] = 1
    return allocation
