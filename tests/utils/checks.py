from contextlib import contextmanager
from typing import ContextManager, Mapping

from brownie import Contract
from brownie.network.account import Account


@contextmanager
def assert_balance_change(account: Account, tokens_diff: Mapping[Contract, int]):
    balances_before = {
        token: token.balanceOf(account.address) for token in tokens_diff.keys()
    }
    yield
    balances_after = {
        token: token.balanceOf(account.address) for token in tokens_diff.keys()
    }
    for token, diff in tokens_diff.items():
        assert (
            balances_after[token] - balances_before[token] == diff
        ), f"{token.name()}: {balances_after[token]}-{balances_before[token]}!={diff}"
