from __future__ import annotations
from typing import Dict, List, Tuple
from src.core.depth import execute, taker_fee
from src.core.graph import Edge

OrderBook = Dict[str, list]   # {"bids":[(px,sz),...], "asks":[(px,sz),...]}

def _apply(edge: Edge, qty_in: float, book: OrderBook, fee_bps: float) -> float:
    """
    edge.side == "buy":  paga QUOTE (qty_in), recebe BASE; taxa sobre QUOTE gasto
    edge.side == "sell": vende BASE (qty_in), recebe QUOTE; taxa sobre QUOTE recebido
    Retorna qty_out na moeda 'edge.to'
    """
    if edge.side == "buy":
        fee = taker_fee(qty_in, fee_bps)
        net_quote = max(qty_in - fee, 0.0)
        r = execute(book, "buy", net_quote)    # usa asks
        return r["qty_out"]                    # BASE
    else:
        r = execute(book, "sell", qty_in)      # usa bids
        fee = taker_fee(r["qty_out"], fee_bps)
        return max(r["qty_out"] - fee, 0.0)    # QUOTE líquido

def run_cycle(cycle: Tuple[Edge,Edge,Edge],
              start_ccy: str,
              start_qty: float,
              books: Dict[str, OrderBook],
              fee_bps: float) -> Tuple[float, float]:
    """
    Executa ciclo completo; retorna (qty_final, edge_relativo)
    """
    e1,e2,e3 = cycle
    q1 = _apply(e1, start_qty,   books[e1.pair], fee_bps)
    q2 = _apply(e2, q1,          books[e2.pair], fee_bps)
    q3 = _apply(e3, q2,          books[e3.pair], fee_bps)
    edge = (q3 - start_qty) / start_qty
    return q3, edge
