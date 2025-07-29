import numpy as np

import sold.allocate


def test_first_price_allocation():
    bids = (5, 3, 2, 1, 8)
    allocation = sold.allocate.first_price(bids=bids)
    assert np.array_equal(allocation, np.array([0, 0, 0, 0, 1]))


def test_second_price_allocation_with_tie():
    """
    With a tie, the allocation is given to the first
    """
    bids = (5, 3, 2, 1, 8, 2, 8)
    allocation = sold.allocate.first_price(bids=bids)
    assert np.array_equal(allocation, np.array([0, 0, 0, 0, 1, 0, 0]))
