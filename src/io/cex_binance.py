import os
from typing import Dict, List, Tuple
from binance.client import Client

OrderBook = Dict[str, List[Tuple[float,float]]]

class BinancePublic:
    def __init__(self, testnet: bool = False):
        self.client = Client(api_key=None, api_secret=None, testnet=testnet)

    def depth(self, symbol: str, limit: int = 50) -> OrderBook:
        d = self.client.get_order_book(symbol=symbol, limit=limit)
        bids = [(float(px), float(sz)) for px,sz in d.get("bids",[])]
        asks = [(float(px), float(sz)) for px,sz in d.get("asks",[])]
        return {"bids": bids, "asks": asks}
