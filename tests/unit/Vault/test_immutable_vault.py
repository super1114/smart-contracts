from brownie import Contract, ImmutableVault, SlashingERC20, interface, reverts
from brownie.network.account import Account

from ...utils.checks import assert_balance_change
from ...utils.dex import fund_token
from ...utils.tokens import TOKEN_ADDRESSES, clean_balance


def test_deploy(owner: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WBTC_addr, WETH_addr], [1, 15], WAVAX_addr, {"from": owner}
    )
    WBTC: Contract = interface.IERC20(WBTC_addr)
    WETH: Contract = interface.IERC20(WETH_addr)

    assert my_vault.assetLength() == 2
    assert my_vault.assets(0) == WBTC_addr
    assert my_vault.assets(1) == WETH_addr
    assert my_vault.reserves(0) == 0
    assert my_vault.reserves(1) == 0
    assert my_vault.weights(0) == 1
    assert my_vault.weights(1) == 15
    assert my_vault.totalSupply() == 0
    assert my_vault.trackingToken() == WAVAX_addr
    expected_name = f"PGVault: {WBTC.symbol()}-{WETH.symbol()}"
    assert my_vault.name() == expected_name


def test_needs_more_than_one_token(owner: Account, bob: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    with reverts("At least 2 tokens are needed"):
        ImmutableVault.deploy([WBTC_addr], [1], WAVAX_addr, {"from": owner})


def test_assets_and_weights_must_match(owner: Account, bob: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    with reverts("Assets and Weights are not matching"):
        ImmutableVault.deploy(
            [WBTC_addr, WAVAX_addr], [1, 2, 3], WAVAX_addr, {"from": owner}
        )


def test_deposit(owner: Account, bob: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WBTC_addr, WETH_addr], [1, 15e10], WAVAX_addr, {"from": owner}
    )
    WBTC: Contract = interface.IERC20(WBTC_addr)
    WETH: Contract = interface.IERC20(WETH_addr)
    PGV: Contract = interface.IERC20(my_vault.address)
    # wbtc has only 8 decimals opposed to the default 18 decimals
    # funds 1 wbtc
    wbtc_amount = int(1e8)
    fund_token(WBTC_addr, bob, wbtc_amount)
    # funds 15 weth
    weth_amount = int(15e18)
    fund_token(WETH_addr, bob, weth_amount)
    WBTC.approve(my_vault.address, 1e40, {"from": bob})
    WETH.approve(my_vault.address, 1e40, {"from": bob})
    with assert_balance_change(
        bob, {WBTC: -wbtc_amount, WETH: -weth_amount, PGV: wbtc_amount}
    ):
        my_vault.deposit(wbtc_amount, {"from": bob})
    assert my_vault.reserves(0) == wbtc_amount
    assert my_vault.reserves(1) == weth_amount
    assert my_vault.balanceOf(bob.address) == wbtc_amount
    assert my_vault.totalSupply() == wbtc_amount
    assert my_vault.symbol() == "PGV"


def test_deposit_from_to(owner: Account, bob: Account, alice: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WBTC_addr, WETH_addr], [1, 15e10], WAVAX_addr, {"from": owner}
    )
    WBTC: Contract = interface.IERC20(WBTC_addr)
    WETH: Contract = interface.IERC20(WETH_addr)
    PGV: Contract = interface.IERC20(my_vault.address)
    # wbtc has only 8 decimals opposed to the default 18 decimals
    # funds 1 wbtc
    wbtc_amount = int(1e8)
    fund_token(WBTC_addr, bob, wbtc_amount)
    # funds 15 weth
    weth_amount = int(15e18)
    fund_token(WETH_addr, bob, weth_amount)
    WBTC.approve(my_vault.address, 1e40, {"from": bob})
    WETH.approve(my_vault.address, 1e40, {"from": bob})
    bob_expected_balance = {WBTC: -wbtc_amount, WETH: -weth_amount, PGV: 0}
    alice_expected_balance = {WBTC: 0, WETH: 0, PGV: wbtc_amount}
    with assert_balance_change(bob, bob_expected_balance):
        with assert_balance_change(alice, alice_expected_balance):
            my_vault.depositTo(alice.address, wbtc_amount, {"from": bob})
    assert my_vault.reserves(0) == wbtc_amount
    assert my_vault.reserves(1) == weth_amount
    assert my_vault.balanceOf(alice.address) == wbtc_amount
    assert my_vault.totalSupply() == wbtc_amount


def test_withdraw_from_to(owner: Account, bob: Account, alice: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WBTC_addr, WETH_addr], [1, 15e10], WAVAX_addr, {"from": owner}
    )
    WBTC: Contract = interface.IERC20(WBTC_addr)
    WETH: Contract = interface.IERC20(WETH_addr)
    PGV: Contract = interface.IERC20(my_vault.address)
    # wbtc has only 8 decimals opposed to the default 18 decimals
    # funds 1 wbtc
    wbtc_amount = int(1e8)
    fund_token(WBTC_addr, bob, wbtc_amount)
    # funds 15 weth
    weth_amount = int(15e18)
    fund_token(WETH_addr, bob, weth_amount)
    WBTC.approve(my_vault.address, 1e40, {"from": bob})
    WETH.approve(my_vault.address, 1e40, {"from": bob})
    my_vault.depositTo(alice.address, wbtc_amount, {"from": bob})
    with assert_balance_change(alice, {WBTC: 0, WETH: 0, PGV: -wbtc_amount}):
        with assert_balance_change(bob, {WBTC: wbtc_amount, WETH: weth_amount, PGV: 0}):
            my_vault.withdrawTo(bob.address, wbtc_amount, {"from": alice})
    assert my_vault.reserves(0) == 0
    assert my_vault.reserves(1) == 0
    assert my_vault.balanceOf(alice.address) == 0
    assert my_vault.balanceOf(bob.address) == 0
    assert my_vault.totalSupply() == 0


def test_cant_withdraw_without_balance(owner: Account, bob: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WBTC_addr, WETH_addr], [1, 15e10], WAVAX_addr, {"from": owner}
    )
    with reverts():
        my_vault.withdraw(1e18, {"from": bob})


def test_cant_withdraw_corrupted_balance(owner: Account, bob: Account):
    """This test recreates a scenario where a malign token(SLASH) unbalances
    the vault proportion, and it verified users can't without due to this situation.

    This is one of those scenarios where we could discuss possibilities on how to recover
    from this situation. But so far, the test is here to achieve 100% coverage.
    """
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    wbtc_amount = int(1e8)
    slash_amount = int(15e18)
    SLASH: Contract = SlashingERC20.deploy(slash_amount, {"from": owner})
    WBTC: Contract = interface.IERC20(WBTC_addr)
    SLASH.transfer(bob.address, slash_amount, {"from": owner})
    my_vault: Contract = ImmutableVault.deploy(
        [WBTC_addr, SLASH.address], [1, 15e10], WAVAX_addr, {"from": owner}
    )
    fund_token(WBTC_addr, bob, wbtc_amount)
    WBTC.approve(my_vault.address, 1e40, {"from": bob})
    SLASH.approve(my_vault.address, 1e40, {"from": bob})
    my_vault.deposit(wbtc_amount, {"from": bob})
    SLASH.slash(my_vault.address, {"from": owner})
    assert SLASH.balanceOf(my_vault.address) == 0
    with reverts("Insufficient token to transfer"):
        my_vault.withdraw(wbtc_amount, {"from": bob})

    with reverts("Insufficient token to transfer"):
        my_vault.withdrawTo(owner.address, wbtc_amount, {"from": bob})


def test_cant_deposit_without_balance_on_all_tokens(owner: Account, bob: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WBTC_addr, WETH_addr], [1, 15e10], WAVAX_addr, {"from": owner}
    )
    WBTC: Contract = interface.IERC20(WBTC_addr)
    WETH: Contract = interface.IERC20(WETH_addr)
    PGV: Contract = interface.IERC20(my_vault.address)
    # wbtc has only 8 decimals opposed to the default 18 decimals
    # funds 1 wbtc
    wbtc_amount = int(1e8)
    fund_token(WBTC_addr, bob, wbtc_amount)
    clean_balance(bob, WETH)
    WBTC.approve(my_vault.address, 1e40, {"from": bob})
    WETH.approve(my_vault.address, 1e40, {"from": bob})
    with assert_balance_change(bob, {WBTC: 0, WETH: 0, PGV: 0}):
        with reverts():
            my_vault.deposit(wbtc_amount, {"from": bob})
    assert my_vault.reserves(0) == 0
    assert my_vault.reserves(1) == 0
    assert my_vault.balanceOf(bob.address) == 0
    assert my_vault.totalSupply() == 0


def test_balance_weights_guarantee_smallest_deposits_wont_be_lost(
    owner: Account, bob: Account
):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WETH_addr, WBTC_addr], [1, 15], WAVAX_addr, {"from": owner}
    )
    WBTC: Contract = interface.IERC20(WBTC_addr)
    WETH: Contract = interface.IERC20(WETH_addr)
    PGV: Contract = interface.IERC20(my_vault.address)
    assert my_vault.assets(0) == WETH_addr
    assert my_vault.weights(0) == 1
    assert my_vault.assets(1) == WBTC_addr
    assert my_vault.weights(1) == 15
    expected_btc = 15  # 15 satoshi
    expected_eth = 1
    fund_token(WBTC_addr, bob, expected_btc)
    fund_token(WETH_addr, bob, expected_eth)
    WBTC.approve(my_vault.address, 1e40, {"from": bob})
    WETH.approve(my_vault.address, 1e40, {"from": bob})
    with assert_balance_change(bob, {WBTC: -expected_btc, WETH: -expected_eth, PGV: 1}):
        my_vault.deposit(1, {"from": bob})


def test_deposit_for_non_normalized_weights_work(owner: Account, bob: Account):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    my_vault: Contract = ImmutableVault.deploy(
        [WETH_addr, WBTC_addr], [4, 15], WAVAX_addr, {"from": owner}
    )
    WBTC: Contract = interface.IERC20(WBTC_addr)
    WETH: Contract = interface.IERC20(WETH_addr)
    PGV: Contract = interface.IERC20(my_vault.address)
    assert my_vault.assets(0) == WETH_addr
    assert my_vault.weights(0) == 4
    assert my_vault.assets(1) == WBTC_addr
    assert my_vault.weights(1) == 15
    expected_btc = 15  # 15 satoshi
    expected_eth = 4
    fund_token(WBTC_addr, bob, expected_btc)
    fund_token(WETH_addr, bob, expected_eth)
    WBTC.approve(my_vault.address, 1e40, {"from": bob})
    WETH.approve(my_vault.address, 1e40, {"from": bob})
    with assert_balance_change(bob, {WBTC: -expected_btc, WETH: -expected_eth, PGV: 1}):
        my_vault.deposit(1, {"from": bob})
