import brownie


def test_price_feed(eth_usd_price_feed):
    price: int = eth_usd_price_feed.latestRound()
    assert price > 0
