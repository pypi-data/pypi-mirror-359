import numpy as np


def first_price(bids):
    """
    Returns the payments for a first price payment auction

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
    payments = np.zeros_like(bids)
    payments[winner_index] = first_price
    return payments


def second_price(bids):
    """
    Returns the payments for a second price payment auction

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
    second_price = np.max([bid for bid in bids if bid != first_price])
    winner_index = np.where(bids == first_price)[0][0]
    payments = np.zeros_like(bids)
    payments[winner_index] = second_price
    return payments
