from typing import List, Tuple, Literal, Dict

Side = Literal["buy","sell"]
Level = Tuple[float, float]              # (price, size)
OrderBook = Dict[str, List[Level]]       # {"bids": [...], "asks": [...]}

def _take(qty: float, levels: List[Level]) -> tuple[float, float, float]:
    filled = 0.0
    cash = 0.0
    for px, sz in levels:
        if qty <= 0:
            break
        use = qty if qty < sz else sz
        filled += use
        cash += use * px
        qty -= use
    avg = cash / filled if filled else 0.0
    return filled, cash, avg

def execute(book: OrderBook, side: Side, qty: float) -> Dict[str, float]:
    if side == "buy":                    # paga QUOTE, recebe BASE
        filled, cash, avg = _take(qty, book["asks"])
        return {"side": "buy",  "qty_in": cash,  "qty_out": filled, "avg": avg}
    else:                                # vende BASE, recebe QUOTE
        filled, cash, avg = _take(qty, book["bids"])
        return {"side": "sell", "qty_in": filled,"qty_out": cash,   "avg": avg}

def taker_fee(amount_quote: float, bps: float) -> float:
    return abs(amount_quote) * (bps * 1e-4)
