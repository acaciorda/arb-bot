import argparse
import importlib
import inspect

CANDIDATES = (
    "tri_paths_scan", "tri_scan", "tri_paths", "scan", "run", "main",
    "triangles", "build_edges",
)

def resolve_from(modname: str):
    mod = importlib.import_module(modname)
    for name in CANDIDATES:
        fn = getattr(mod, name, None)
        if callable(fn):
            return mod, fn
    return mod, None

def call_by_sig(fn, **kwargs):
    sig = inspect.signature(fn)
    args = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return fn(**args)

def _fallback_symbols(mod):
    """
    Constrói um conjunto mínimo de símbolos quando o módulo graph
    não expõe 'list()' nem atributo 'symbols'.
    Preferimos ETH/USDT, BTC/USDT, ETH/BTC (nomeados 'ETHUSDT', 'BTCUSDT', 'ETHBTC').
    """
    # tente usar atributo 'symbols' se existir
    if hasattr(mod, "symbols"):
        syms = getattr(mod, "symbols")
        if isinstance(syms, (list, tuple, set)) and syms:
            return list(syms)

    # tente usar currencies() só para validar ambiente (não dependemos do formato)
    curr_fn = getattr(mod, "currencies", None)
    if callable(curr_fn):
        try:
            _ = call_by_sig(curr_fn)
        except Exception:
            pass

    # fallback seguro e mínimo para tri-arb
    return ["ETHUSDT", "BTCUSDT", "ETHBTC"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start_qty", type=float, required=True)
    p.add_argument("--min_edge", type=float, default=0.0005)
    p.add_argument("--fee_bps",   type=float, default=10.0)
    p.add_argument("--fast", action="store_true")
    args = p.parse_args()

    # 1) tenta no arb_engine (normal)
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

    fast_exec = True if args.fast else None

    # Caso especial do fallback: graph.triangles(edges=...)
    if getattr(fn, "__name__", "") == "triangles":
        be = getattr(mod, "build_edges", None)
        if not callable(be):
            raise ImportError("src.core.graph.triangles exige 'build_edges' disponível no módulo.")

        # monte 'symbols' de forma robusta
        symbols = None
        list_fn = getattr(mod, "list", None)
        if callable(list_fn):
            try:
                symbols = call_by_sig(list_fn)
            except Exception:
                symbols = None

        if not symbols:
            symbols = _fallback_symbols(mod)

        be_sig = inspect.signature(be)
        be_kwargs = {}
        if "symbols" in be_sig.parameters:
            be_kwargs["symbols"] = symbols

        # opcionalmente 'currencies' se a função aceitar
        if "currencies" in be_sig.parameters and callable(getattr(mod, "currencies", None)):
            try:
                be_kwargs["currencies"] = call_by_sig(getattr(mod, "currencies"))
            except Exception:
                pass

        edges = be(**be_kwargs)

        tri_sig = inspect.signature(fn)
        tri_kwargs = {}
        if "edges" in tri_sig.parameters:
            tri_kwargs["edges"] = edges

        tris = fn(**tri_kwargs)
        print(f"[tri_scan] triangles={len(tris)}")
        for i, t in enumerate(tris[:10]):
            print(f"[tri_scan] tri[{i}]: {t}")
        return

    # Caso geral (arb_engine ou outro export no graph)
    _ = call_by_sig(
        fn,
        start_qty=args.start_qty,
        min_edge=args.min_edge,
        fee_bps=args.fee_bps,
        fast=args.fast,
        fast_exec=fast_exec,
        send_alert=True,
        once=True,
    )

if __name__ == "__main__":
    main()
