from brownie import Contract
from brownie.network.account import Account

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ONE_ADDRESS = "0x0000000000000000000000000000000000000001"

TOKEN_ADDRESSES = {
    "WAVAX": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    "PNG": "0x60781c2586d68229fde47564546784ab3faca982",
    "LINK": "0xb3fe5374f67d7a22886a0ee082b2e2f9d2651651",
    "USDT": "0xde3a24028580884448a5397872046a019649b084",
    "1INCH": "0xe54eb2c3009fa411bf24fb017f9725b973ce36f0",
    "AAVE": "0x8ce2dee54bb9921a2ae0a63dbb2df8ed88b91dd9",
    "BAT": "0x6b329326e0f6b95b93b52229b213334278d6f277",
    "BUSD": "0xaeb044650278731ef3dc244692ab9f64c78ffaea",
    "DAI": "0xba7deebbfc5fa1100fb055a87773e1e99cd3507a",
    "GRT": "0x46c54b16af7747067f412c78ebadae203a26ada0",
    "RUNE": "0xcfcec62d7c459c55e4c2ed29814f17153d113ce6",
    "SNX": "0x68e44c4619db40ae1a0725e77c02587bc8fbd1c9",
    "SUSHI": "0x39cf1bd5f15fb22ec3d9ff86b0727afc203427cc",
    "UMA": "0xc84d7bff2555955b44bdf6a307180810412d751b",
    "UNI": "0xf39f9671906d8630812f9d9863bbef5d523c84ab",
    "WBTC": "0x408d4cd0adb7cebd1f1a1c33a0ba2098e1295bab",
    "WETH": "0xf20d962a6c8f70c731bd838a3a388d7d48fa6e15",
    "YFI": "0x99519acb025a0e0d44c3875a4bbf03af65933627",
}


def clean_balance(account: Account, token: Contract):
    balance = token.balanceOf(account.address)
    if balance > 0:
        token.transfer(ONE_ADDRESS, balance, {"from": account})
