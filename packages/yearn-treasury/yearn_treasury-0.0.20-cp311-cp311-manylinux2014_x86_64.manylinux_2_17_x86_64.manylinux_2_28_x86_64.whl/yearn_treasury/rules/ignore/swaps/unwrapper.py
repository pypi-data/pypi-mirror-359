from dao_treasury import TreasuryTx
from y import Network

from yearn_treasury.rules.ignore.swaps import swaps


@swaps("Unwrapper", Network.Mainnet)
def is_unwrapper(tx: TreasuryTx) -> bool:
    return "Contract: Unwrapper" in [tx.from_nickname, tx.to_nickname]
