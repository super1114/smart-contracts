import pytest
from brownie import Contract, Vault, VaultFactory
from brownie.network.account import Accounts

from .abis import PRICE_FEED_ABI

ETH_USD_PRICE_FEED: str = "0x976B3D034E162d8bD72D6b9C989d545b839003b0"


@pytest.fixture(scope="session")
def eth_usd_price_feed():
    yield Contract.from_abi("ChainlinkFeed", ETH_USD_PRICE_FEED, PRICE_FEED_ABI)


@pytest.fixture(scope="session")
def alice(accounts: Accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def bob(accounts: Accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def charlie(accounts: Accounts):
    yield accounts[3]


@pytest.fixture(scope="session")
def dave(accounts: Accounts):
    yield accounts[4]


@pytest.fixture(scope="session")
def erin(accounts: Accounts):
    yield accounts[5]


@pytest.fixture(scope="session")
def owner(accounts: Accounts):
    yield accounts[0]


@pytest.fixture(scope="function")
def vault(Vault, owner):
    yield Vault.deploy({"from": owner})


@pytest.fixture(scope="function")
def vault_factory(owner):
    yield VaultFactory.deploy({"from": owner})
