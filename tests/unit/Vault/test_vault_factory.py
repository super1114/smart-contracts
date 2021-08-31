from brownie import Contract, ImmutableVault, VaultFactory, interface, reverts
from brownie.network.account import Account

from ...utils.tokens import TOKEN_ADDRESSES


def test_deploy(owner: Account):
    vault_factory: Contract = VaultFactory.deploy({"from": owner})
    assert vault_factory.allVaultsLength() == 0


def test_create_vault(vault_factory: VaultFactory):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    tx_receipt = vault_factory.createVault([WBTC_addr, WETH_addr], [1, 2], WAVAX_addr)
    vault = ImmutableVault.at(tx_receipt.events["VaultCreated"]["vault"])
    assert vault_factory.allVaultsLength() == 1

    assert vault.address == vault_factory.getVaultAddress(
        [WBTC_addr, WETH_addr], [1, 2], WAVAX_addr
    )
    # token order matter, also does weights and trackingToken
    assert vault.address != vault_factory.getVaultAddress(
        [WETH_addr, WBTC_addr], [2, 1], WAVAX_addr
    )
    assert vault.address != vault_factory.getVaultAddress(
        [WETH_addr, WBTC_addr], [1, 2], WAVAX_addr
    )
    assert vault.address != vault_factory.getVaultAddress(
        [WETH_addr, WBTC_addr], [1, 2], WBTC_addr
    )
    assert vault.assetLength() == 2
    assert vault.assets(0) == WBTC_addr
    assert vault.assets(1) == WETH_addr
    assert vault.reserves(0) == 0
    assert vault.reserves(1) == 0
    assert vault.weights(0) == 1
    assert vault.weights(1) == 2
    assert vault.totalSupply() == 0
    assert vault.trackingToken() == WAVAX_addr


def test_cant_create_vault_with_repeating_token(vault_factory: VaultFactory):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    with reverts("Repeating token not supported"):
        vault_factory.createVault(
            [WBTC_addr, WETH_addr, WBTC_addr], [1, 2, 1], WAVAX_addr
        )


def test_cant_deploy_the_same_vault(vault_factory: VaultFactory):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    vault_factory.createVault([WBTC_addr, WETH_addr], [1, 2], WAVAX_addr)
    with reverts():
        vault_factory.createVault([WBTC_addr, WETH_addr], [1, 2], WAVAX_addr)


def test_can_deploy_many_vault(vault_factory: VaultFactory):
    WBTC_addr = TOKEN_ADDRESSES["WBTC"]
    WETH_addr = TOKEN_ADDRESSES["WETH"]
    WAVAX_addr = TOKEN_ADDRESSES["WAVAX"]
    vault_factory.createVault([WBTC_addr, WETH_addr], [1, 2], WAVAX_addr)
    vault_factory.createVault([WBTC_addr, WETH_addr], [1, 4], WAVAX_addr)

    vault_factory.createVault([WBTC_addr, WETH_addr], [2, 4], WAVAX_addr)

    vault_factory.createVault([WETH_addr, WBTC_addr], [1, 2], WAVAX_addr)

    vault_factory.createVault([WETH_addr, WBTC_addr], [1, 2], WBTC_addr)

    assert vault_factory.allVaultsLength() == 5
