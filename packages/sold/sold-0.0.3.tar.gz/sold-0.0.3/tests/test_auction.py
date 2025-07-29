import scipy.stats
import numpy as np

import sold
import sold.allocate
import sold.bid
import sold.pay


def test_auction_with_seed_0():
    N = 2
    seed = 0
    valuation_distributions = [scipy.stats.uniform() for _ in range(N)]
    bidding_functions = [sold.bid.true_value for _ in range(N)]
    allocation, payments, valuations = sold.auction(
        valuation_distributions=valuation_distributions,
        bidding_functions=bidding_functions,
        allocation_rule=sold.allocate.first_price,
        payment_rule=sold.pay.first_price,
        seed=seed,
    )
    assert np.array_equal(allocation, [0, 1])
    assert np.allclose(payments, [0, 0.71518937])
    assert np.allclose(valuations, [0.5488135, 0.71518937])


def test_auction_with_seed_2():
    N = 2
    seed = 2
    valuation_distributions = [scipy.stats.uniform() for _ in range(N)]
    bidding_functions = [sold.bid.true_value for _ in range(N)]
    allocation, payments, valuations = sold.auction(
        valuation_distributions=valuation_distributions,
        bidding_functions=bidding_functions,
        allocation_rule=sold.allocate.first_price,
        payment_rule=sold.pay.first_price,
        seed=seed,
    )
    assert np.array_equal(allocation, [1, 0])
    assert np.allclose(payments, [0.4359949, 0])
    assert np.allclose(valuations, [0.4359949, 0.02592623])


def test_auction_works_with_seed_function():
    """
    Create an auction with 3 players, two use a true value and the third use the
    theoretic weakly dominated strategy of 2/3 value.

    In expectation this third player should do better.
    """
    N = 3
    repetitions = 100
    valuation_distributions = [scipy.stats.uniform() for _ in range(N)]
    bidding_functions = [sold.bid.true_value for _ in range(N - 1)] + [
        sold.bid.create_shaded_bid_map(2 / 3)
    ]
    utilities = []
    for seed in range(repetitions):
        allocation, payments, valuations = sold.auction(
            valuation_distributions=valuation_distributions,
            bidding_functions=bidding_functions,
            allocation_rule=sold.allocate.first_price,
            payment_rule=sold.pay.first_price,
            seed=seed,
        )
        utilities.append(valuations - allocation * payments)
    mean_utilities = np.mean(utilities, axis=0)
    assert np.allclose(mean_utilities, [0.17535816, 0.18842919, 0.47175621])
