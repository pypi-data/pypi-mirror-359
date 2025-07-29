import numpy as np


def auction(
    valuation_distributions,
    bidding_functions,
    allocation_rule,
    payment_rule,
    seed=None,
):
    """
    Runs a simulated auction

    Parameters
    ----------
    valuation_distributions: iterable
        A collection of N scipy.stats distributions (or any instance with a `rvs` method)
    bidding_functions: iterable
        A collection of N bidding functions that maps a value to a bid.
        All bidding functions must have a `value` keyword in its signature.
    allocation_rule: func
        A function that takes the collection of bids and returns an N simplex of allocations
        This function must have a `bids` keyword in its signature.
    payment_rule: func
        A function that takes the allocations and returns the payment made by each player
        This function must have `bids` keyword in its signature.
    seed: int
        A seed for the random number generation

    Returns
    -------
    allocation: an element of the simplex on N
    payments: the payments made by each individual
    valuations: the sampled valuations of each individual
    """
    assert len(valuation_distributions) == len(
        bidding_functions
    ), "Incorrect number of valuation distribution and bidding functions"

    np.random.seed(seed)
    valuations = [distribution.rvs() for distribution in valuation_distributions]
    bids = [
        function(value=value) for function, value in zip(bidding_functions, valuations)
    ]
    allocation = allocation_rule(bids=bids)
    payments = payment_rule(bids=bids)
    return np.array(allocation), np.array(payments), np.array(valuations)
