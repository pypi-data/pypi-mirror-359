import decimal
from typing import Final

from dao_treasury import TreasuryTx
from y import Network

from yearn_treasury.constants import YCHAD_MULTISIG
from yearn_treasury.rules.ignore.swaps import swaps


buying_yfi: Final = swaps("Buying YFI")

VYPER_BUYERS: Final = (
    "0xdf5e4E54d212F7a01cf94B3986f40933fcfF589F",  # buys YFI for DAI at the current chainlink price
    "0x6903223578806940bd3ff0C51f87aa43968424c8",  # buys YFI for DAI at the current chainlink price. Can be funded via llamapay stream.
)
"""These contracts, now retired, previously were used to purchase YFI for DAI at the current chainlink market price."""

Decimal: Final = decimal.Decimal


@buying_yfi("Top-up Buyer Contract", Network.Mainnet)
def is_buyer_top_up(tx: TreasuryTx) -> bool:
    """
    The sell side of these transactions is in :func:`is_buying_with_buyer`.
    The buyer is topped up with DAI regularly and buys YFI at the current chainlink market price.

    # TODO: amortize this into a daily expense
    """
    return tx.symbol == "DAI" and tx.to_address.address in VYPER_BUYERS  # type: ignore [union-attr]


@buying_yfi("Buyer Contract", Network.Mainnet)
def is_buying_with_buyer(tx: TreasuryTx) -> bool:
    """
    The buy side of these transactions is in :func:`is_buyer_top_up`.
    The buyer is topped up with DAI regularly and buys YFI at the current chainlink market price
    """
    if tx.symbol == "YFI" and tx.to_address.address == YCHAD_MULTISIG:  # type: ignore [union-attr]
        try:
            events = tx.events
        except KeyError as e:
            if "components" in str(e):
                return False
            raise

        if "Buyback" in events:
            buyback_event = events["Buyback"]
            if buyback_event.address in VYPER_BUYERS and all(
                arg in buyback_event for arg in ("buyer", "yfi", "dai")
            ):
                buyback_amount = Decimal(buyback_event["yfi"]) / 10**18  # type: ignore [arg-type]
                if tx.amount == buyback_amount:
                    return True
                print(
                    f"from node: {buyback_amount} from db: {tx.amount} diff: {buyback_amount - tx.amount}"
                )
                # raise ValueError(f'from node: {buyback_amount} from db: {tx.amount} diff: {buyback_amount - tx.amount}')
    return False
