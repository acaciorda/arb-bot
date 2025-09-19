from loguru import logger
from src.core.depth import execute, taker_fee

def fake_book(mid: float, spread_bps: float = 5, depth: float = 10.0):
    spread = mid * spread_bps * 1e-4
    ask = mid + spread / 2
    bid = mid - spread / 2
    asks = [(ask * (1 + 0.0001 * i), depth) for i in range(10)]
    bids = [(bid * (1 - 0.0001 * i), depth) for i in range(10)]
    return {"asks": asks, "bids": bids}

def main():
    usdt_eth = fake_book(3500)      # USDT/ETH
    eth_btc  = fake_book(0.06)      # ETH/BTC
    btc_usdt = fake_book(60000)     # BTC/USDT

    q_usdt = 1_000.0

    # Leg 1: USDT -> ETH (compra ETH)
    leg1 = execute(usdt_eth, "buy", q_usdt)
    fee1 = taker_fee(leg1["qty_in"], 2.0)

    # Leg 2: ETH -> BTC (vende ETH)
    leg2 = execute(eth_btc, "sell", leg1["qty_out"])
    fee2 = taker_fee(leg2["qty_out"], 2.0)

    # Leg 3: BTC -> USDT (vende BTC)
    leg3 = execute(btc_usdt, "sell", leg2["qty_out"])
    fee3 = taker_fee(leg3["qty_out"], 2.0)

    out_usdt = leg3["qty_out"] - fee3
    edge = (out_usdt - q_usdt) / q_usdt
    logger.info(f"cycle_out={out_usdt:.2f}  edge={edge:.6f}  "
                f"avg_px: leg1={leg1['avg']:.4f} leg2={leg2['avg']:.8f} leg3={leg3['avg']:.2f}")

if __name__ == "__main__":
    main()
