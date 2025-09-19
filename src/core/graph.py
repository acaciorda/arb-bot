from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Set

@dataclass(frozen=True)
class Edge:
    pair: str          # ex: "ETHUSDT"
    side: str          # "buy"  (paga QUOTE, recebe BASE)  ou "sell" (vende BASE, recebe QUOTE)
    frm: str           # moeda de entrada
    to: str            # moeda de saída

def split_symbol(sym: str) -> Tuple[str,str]:
    # heurística simples p/ Binance (moedas comuns primeiro)
    SUFFIX = ("USDT","BTC","ETH","BNB","FDUSD","TUSD","USDC")
    for s in SUFFIX:
        if sym.endswith(s):
            return sym[:-len(s)], s
    # fallback: separa 3/4 letras finais
    return sym[:-4], sym[-4:]

def build_edges(symbols: Iterable[str]) -> List[Edge]:
    edges: List[Edge] = []
    for s in symbols:
        base, quote = split_symbol(s)
        edges.append(Edge(pair=s, side="buy",  frm=quote, to=base))
        edges.append(Edge(pair=s, side="sell", frm=base,  to=quote))
    return edges

def currencies(edges: Iterable[Edge]) -> Set[str]:
    cs: Set[str] = set()
    for e in edges:
        cs.add(e.frm); cs.add(e.to)
    return cs

def triangles(edges: List[Edge]) -> List[Tuple[Edge,Edge,Edge]]:
    # procura ciclos dirigidos de tamanho 3 (a->b->c->a)
    by_from: Dict[str, List[Edge]] = {}
    for e in edges:
        by_from.setdefault(e.frm, []).append(e)

    result: List[Tuple[Edge,Edge,Edge]] = []
    seen: Set[Tuple[str,str,str,str,str,str]] = set()

    for e1 in edges:
        for e2 in by_from.get(e1.to, []):
            for e3 in by_from.get(e2.to, []):
                if e3.to != e1.frm:  # precisa fechar o ciclo
                    continue
                key = tuple(sorted([e1.pair+e1.side, e2.pair+e2.side, e3.pair+e3.side]))
                if key in seen: 
                    continue
                seen.add(key)
                result.append((e1,e2,e3))
    return result
