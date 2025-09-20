import argparse
import importlib
import inspect

CANDIDATES = ("tri_paths_scan", "tri_scan", "tri_paths", "scan", "run", "main")

def resolve_from(modname: str):
    mod = importlib.import_module(modname)
    for name in CANDIDATES:
        fn = getattr(mod, name, None)
        if callable(fn):
            return mod, fn
    return mod, None

def call_by_sig(fn, **kwargs):
    sig = inspect.signature(fn)
    return fn(**{k: v for k, v in kwargs.items() if k in sig.parameters})

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start_qty", type=float, required=True)
    p.add_argument("--min_edge", type=float, default=0.0005)
    p.add_argument("--fee_bps",   type=float, default=10.0)
    p.add_argument("--fast", action="store_true")
    args = p.parse_args()

    # 1) tenta no arb_engine
    mod, fn = resolve_from("src.core.arb_engine")
    if not fn:
        # 2) fallback para graph
        mod, fn = resolve_from("src.core.graph")
        if not fn:
            raise ImportError(
                f"Nenhuma função de scan encontrada em "
                f"src.core.arb_engine ou src.core.graph. "
                f"Tente expor uma das: {CANDIDATES}"
            )

    # parâmetro de execução rápida (se o destino aceitar)
    fast_exec = None
    if args.fast:
        try:
            from src.core.fastbook import taker_roundtrip as fast_roundtrip
            fast_exec = fast_roundtrip
        except Exception:
            fast_exec = True  # sinaliza “modo rápido” genérico se a função aceitar

    result = call_by_sig(
        fn,
        start_qty=args.start_qty,
        min_edge=args.min_edge,
        fee_bps=args.fee_bps,
        send_alert=True,
        once=True,
        fast_exec=fast_exec,
        fast=args.fast,   # cobre o caso em que a função usa --fast
    )
    return result

if __name__ == "__main__":
    main()
