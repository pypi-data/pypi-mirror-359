Join [the Game Theory Discord](https://github.com/drvinceknight/equilibrium_explorers)
server to chat — [direct invite link](https://discord.gg/NfTAkhAeyc).

# Sold

A python library for the study of Auctions

## Tutorial

Let us consider an auction with $N=10$ bidders. The Auction is a [sealed second
price auction](https://en.wikipedia.org/wiki/Vickrey_auction) which means that
the highest bidder wins but pays the price of the second auction.

We will use `sold` to simulate this auction.

The value of the good is independently sampled from the uniform distribution on
$[0, 1]$.

Let us build these distributions:

```python
>>> import scipy.stats
>>> N = 10
>>> valuation_distributions = [scipy.stats.uniform for _ in range(N)]
>>> valuation_distributions
[<scipy.stats._continuous_distns.uniform_gen...]

```

The first 9 participants plan to bid by shading their value $v_i$ by
some increasing parameter $\sigma_i$ ($\sigma_1=1/10, \sigma_2=2/10, \dots,
\sigma_9 = 9/10). The last participants aims to bid their
true value.

Let us build all these bidding strategies:

```python
>>> import sold.bid
>>> bidding_functions = [sold.bid.create_shaded_bid_map((i + 1) / N) for i in range(N - 1)] + [sold.bid.true_value]
>>> bidding_functions
[<function create_shaded_bid_map...]

```

`sold` has functions for allocating to the highest bidder and to make them pay
the second highest bid:

```python
>>> import sold.allocate
>>> import sold.pay
>>> allocation_rule=sold.allocate.first_price
>>> payment_rule=sold.pay.second_price

```

Now we can run a single instance of this auction:

```python
>>> import sold
>>> seed = 0
>>> allocation, payments, valuations = sold.auction(
...     valuation_distributions=valuation_distributions,
...     bidding_functions=bidding_functions,
...     allocation_rule=allocation_rule,
...     payment_rule=payment_rule,
...     seed=seed,
... )
>>> allocation
array([0., 0., 0., 0., 0., 0., 0., 0., 1., 0.])
>>> payments
array([0.       , 0.       , 0.       , 0.       , 0.       , 0.       ,
       0.       , 0.       , 0.7134184, 0.       ])
>>> valuations
array([0.5488135 , 0.71518937, 0.60276338, 0.54488318, 0.4236548 ,
       0.64589411, 0.43758721, 0.891773  , 0.96366276, 0.38344152])
>>> utility = allocation * valuations - payments
>>> utility
array([0.        , 0.        , 0.        , 0.        , 0.        ,
       0.        , 0.        , 0.        , 0.25024436, 0.        ])

```

We can see that the winner was in fact the penultimate player (who bid $8/10$ of their valuation and bid the second highest bid)
they valued their item $.96366276$ and obtained a utility of $0.25024436$.

The Bayesian Nash equilibrium for this type of auction is in fact for all player
to bid their true value. Let us repeat the auction and observe the median
utilities of each player.

```python
>>> import numpy as np
>>> repetitions = 10_000
>>> utility = np.zeros(N)
>>> for seed in range(repetitions):
...     allocation, payments, valuations = sold.auction(
...         valuation_distributions=valuation_distributions,
...         bidding_functions=bidding_functions,
...         allocation_rule=allocation_rule,
...         payment_rule=payment_rule,
...         seed=seed,
...     )
...     utility += allocation * valuations - payments
>>> utility /= repetitions
>>> utility
array([0.        , 0.        , 0.00019114, 0.00252914, 0.00717527,
       0.02088046, 0.03997725, 0.05441776, 0.07010232, 0.07945485])

```

We see that indeed the last individual bidding truthfully gets the highest
utility.

## How To?

### How to use common valuation distributions

Most common distributions are implemented in `scipy.stats` and can be used
directly in `sold`:

```python
>>> import scipy.stats
>>> valuation_distributions = [scipy.stats.truncnorm(a=1, b=10), scipy.stats.triang(c=.5), scipy.stats.expon()]

```

**Note: Any Python object with an `rvs` method can be used as a valuation
distribution.**

### How to create a truthful bidding function

`sold` has a true value bidding function:

```python
>>> import sold.bid
>>> function = sold.bid.true_value
>>> function(5)
5

```

### How to create a shaded bidding function

`sold` has a function to build shaded bidding functions

```python
>>> import sold.bid
>>> function = sold.bid.create_shaded_bid_map(shade = 1 / 5)
>>> function(5)
1.0

```

### How to create a custom bidding function

You can use any Python function that takes a single keyword parameter `value` as
a bidding function in `sold`:

```python
>>> import numpy as np
>>> def random_bid(value):
...     return np.random.random()

```

### How to allocate to the highest bidder

To allocate to the highest bidder use `sold.allocate.first.price` as the
`sold.auction` `allocation_rule` value.

```python
>>> import sold.allocate
>>> bids = (2, 3, 1, 3)
>>> sold.allocate.first_price(bids=bids)
array([0, 1, 0, 0])

```

**In the case of a tie this allocates to the first instance of the highest price.**

### How to create a custom allocation rule

You can use any Python function that takes a single keyword parameter `bids`
(iterable) as the `allocation_rule`.

```python
>>> import numpy as np
>>> def allocate_first_price_with_random_tie_break(bids):
...     first_price = np.max(bids)
...     winner_index = np.random.choice(np.where(bids == first_price)[0])
...     allocation = np.zeros_like(bids)
...     allocation[winner_index] = 1
...     return allocation
>>> np.random.seed(1)
>>> allocate_first_price_with_random_tie_break(bids=(2, 3, 1, 3))
array([0, 0, 0, 1])

```

### How to pay the first price

To pay the first price given a set of bids use `sold.pay.first_price`:

```python
>>> import sold.pay
>>> sold.pay.first_price(bids=(2, 3, 1, 3))
array([0, 3, 0, 0])

```

**In the case of a tie this takes payment from the first instance of the highest price.**

### How to pay the second price

To pay the second price given a set of bids use `sold.pay.second_price`:

```python
>>> import sold.pay
>>> sold.pay.second_price(bids=(2, 3, 1, 3))
array([0, 2, 0, 0])

```

**In the case of a tie this takes payment from the first instance of the highest price.**

### How to run an auction

To run an auction use `sold.auction`:

```python
>>> N = 2
>>> seed = 0
>>> valuation_distributions = [scipy.stats.uniform() for _ in range(N)]
>>> bidding_functions = [sold.bid.true_value for _ in range(N)]
>>> allocation, payments, valuations = sold.auction(
...     valuation_distributions=valuation_distributions,
...     bidding_functions=bidding_functions,
...     allocation_rule=sold.allocate.first_price,
...     payment_rule=sold.pay.first_price,
...     seed=seed,
... )
>>> utilities = valuations * allocation - payments
>>> utilities
array([0., 0.])

```

## Discussion

### Definition of an Auction

An **auction game** with $N$ players (or bidders) is defined by:

- A set of random variables $V_i$, for $1 \leq i \leq N$, from which each player’s  
  private valuation $v_i$ for the good is drawn.
- A set of possible bids $b_i \in B_i$, where $b_i$ is typically the output of a  
  bidding strategy $\mathcal{b}_i: V_i \to B_i$ that maps valuations to bids.
- An **allocation rule**  
  $q: B_1 \times B_2 \times \dots \times B_N \to [0,1]^N$,  
  which determines the probability with which each player receives the good.  
  Often, this output is a deterministic vector with a single 1 (winner) and the  
  remaining entries 0.
- A **payment rule**  
  $p: B_1 \times B_2 \times \dots \times B_N \to \mathbb{R}^N$,  
  which determines how much each player pays as a function of all bids.

The utility of player $i$ is then given by:

$$
u_i = v_i \cdot q_i - p_i
$$

where $q_i$ is the allocation to player $i$, and $p_i$ is their payment.

## Reference

TBD
