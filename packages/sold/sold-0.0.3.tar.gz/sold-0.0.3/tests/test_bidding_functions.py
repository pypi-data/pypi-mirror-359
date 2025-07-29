import sold.bid


def test_true_bid():
    """
    A test for the true bid function
    """
    value = 50
    bid = sold.bid.true_value(value)
    assert value == bid


def test_create_shaded_bid():
    """
    A text to check the generation of a shaded bid function
    """
    value = 1
    shade = 0.8
    bid_map = sold.bid.create_shaded_bid_map(shade=shade)
    bid = bid_map(value=value)
    assert bid == shade * value
