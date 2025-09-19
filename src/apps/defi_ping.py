from loguru import logger
from src.infra.config import load_config
from src.io.defi import snapshot

def main() -> None:
    load_config()  # carrega .env
    s = snapshot()
    logger.info(f"[DeFi] {s}")

if __name__ == "__main__":
    main()
