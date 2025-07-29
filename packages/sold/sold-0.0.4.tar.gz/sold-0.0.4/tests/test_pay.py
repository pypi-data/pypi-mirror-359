import numpy as np

import sold.pay


def test_first_price_pay_function():
    bids = (5, 3, 2, 1, 8)
    payments = sold.pay.first_price(bids)
    assert np.array_equal(payments, np.array((0, 0, 0, 0, 8)))


def test_first_price_pay_function_with_ties():
    bids = (5, 3, 2, 1, 8, 2, 8)
    payments = sold.pay.first_price(bids)
    assert np.array_equal(payments, np.array((0, 0, 0, 0, 8, 0, 0)))


def test_second_price_pay_function():
    bids = (5, 3, 2, 1, 8)
    payments = sold.pay.second_price(bids)
    assert np.array_equal(payments, np.array((0, 0, 0, 0, 5)))
