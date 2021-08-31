from math import ceil

from brownie import Contract, interface
from brownie.network.account import Account

from .tokens import TOKEN_ADDRESSES, ZERO_ADDRESS


def pangolin_router() -> Contract:
    return interface.IPangolinRouter("0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106")


def pangolin_factory() -> Contract:
    return interface.IPangolinFactory("0xefa94DE7a4656D787667C749f7E1223D71E9FD88")


def WAVAX_contract() -> Contract:
    return interface.IWAVAX("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")


def get_liquidity_pair(liquidity_pair_addr: str) -> Contract:
    return interface.IPangolinPair(liquidity_pair_addr)


def fund_wavax(account: Account, amount: int):
    assert account.balance() >= amount, "Not enough AVAX to fund wavax"
    WAVAX_contract().deposit({"from": account, "amount": amount})
    assert WAVAX_contract().balanceOf(account.address) >= amount, "Deposit didn't work"


def get_swap_amount(amount_in: int, reserve_in: int, reserve_out: int) -> int:
    """Given an amount in, the reserves of the input token, the reserve sof the output token
    computes the amount of output token that the amount_in can provide
    """
    amount_after_fee = amount_in * 997
    numerator = amount_after_fee * reserve_out
    denominator = (reserve_in * 1000) + amount_after_fee
    return ceil(numerator / denominator)


def get_swap_amount_in(
    amount_out: int, reserve_in: int, reserve_out: int, slippage_tolerance: float
) -> int:
    """Given an amount out, the reserve of the input token, the reserve of the output
    computes the amount of input token for the swap to get the amount of the output token
    """
    numerator = amount_out * reserve_in * 1000
    denominator = 997 * (reserve_out - amount_out)
    return ceil((numerator / denominator) * slippage_tolerance)


def fund_token(token_address: str, account: Account, amount: int):
    """Funds the account with the token provided
    Adds enough WAVAX to funds the correct amount of the token
    """
    factory = pangolin_factory()
    liquidity_pair_addr = factory.getPair(TOKEN_ADDRESSES["WAVAX"], token_address)
    assert (
        liquidity_pair_addr != ZERO_ADDRESS
    ), "Liquidity pair for {token} and WAVAX doesn't exist, can't fund {token}"
    liquidity_pair = get_liquidity_pair(liquidity_pair_addr)
    reserve0, reserve1, _ = liquidity_pair.getReserves()
    if liquidity_pair.token0() == TOKEN_ADDRESSES["WAVAX"]:
        amount_out0, amount_out1 = 0, amount
    else:
        reserve0, reserve1 = reserve1, reserve0
        amount_out0, amount_out1 = amount, 0
    assert (
        amount_out0 + amount_out1 > 0
    ), "Not enough AVAX used, value is 0 due to rounding issues, use a bigger amountAvax"
    slippage_tolerance = 1.05  # 5%
    wavax_amount = get_swap_amount_in(amount, reserve0, reserve1, slippage_tolerance)
    assert (
        reserve0 > wavax_amount
    ), "Not enough liquidity in the reserves to fund the token"
    fund_wavax(account, wavax_amount)
    WAVAX_contract().transfer(liquidity_pair_addr, wavax_amount, {"from": account})
    liquidity_pair.swap(
        amount_out0, amount_out1, account.address, bytes(), {"from": account}
    )
    assert interface.IERC20(token_address).balanceOf(account.address) >= amount
