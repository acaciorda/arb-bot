import argparse
from loguru import logger
from src.infra.config import load_config
from src.io.cex_binance import BinancePublic
from src.core.graph import build_edges, triangles
from src.core.arb_engine import run_cycle

DEFAULT_PAIRS = ["ETHUSDT","BTCUSDT","ETHBTC"]  # pode expandir depois

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", default=DEFAULT_PAIRS)
    ap.add_argument("--start_ccy", default="USDT")
    ap.add_argument("--start_qty", type=float, default=1000.0)
    ap.add_argument("--fee_bps", type=float, default=10.0)       # taker ~0.10%
    ap.add_argument("--min_edge", type=float, default=0.0005)    # 5 bps
    args = ap.parse_args()

    cfg = load_config()
    testnet = (str(cfg.get("BINANCE_TESTNET","true")).lower() == "true")
    binance = BinancePublic(testnet=testnet)

    edges = build_edges(args.pairs)
    cycles = triangles(edges)
    if not cycles:
        logger.warning("Nenhum ciclo possível a partir dos pares fornecidos.")
        return

    # baixa order books necessários
    need = sorted({e.pair for c in cycles for e in c})
    books = {s: binance.depth(s, limit=50) for s in need}

    best = None
    for cyc in cycles:
        qty_out, edge = run_cycle(cyc, args.start_ccy, args.start_qty, books, args.fee_bps)
        logger.info(f"{[e.pair+'-'+e.side for e in cyc]} -> out={qty_out:.6f}  edge={edge:.6%}")
        if best is None or edge > best[2]:
            best = (cyc, qty_out, edge)

    if best:
        cyc, qout, edge = best
        msg = f"BEST {[e.pair+'-'+e.side for e in cyc]} | out={qout:.6f} | edge={edge:.6%}"
        if edge >= args.min_edge:
            try:
                from src.utils import telegram_alert
                telegram_alert(f"[ALFA] {msg}")
            except Exception as e:
                logger.error(f"telegram falhou: {e}")
        logger.info(msg)

if __name__ == "__main__":
    main()
