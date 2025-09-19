import os
from web3 import Web3

def get_w3(timeout: int = 10) -> Web3:
    url = os.getenv("ETH_RPC_URL")
    if not url:
        raise RuntimeError("ETH_RPC_URL não definido no ambiente/.env")
    w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": timeout}))
    if not w3.is_connected():
        raise RuntimeError("Falha na conexão RPC")
    return w3

def snapshot() -> dict:
    w3 = get_w3()
    return {
        "connected": True,
        "chain_id": w3.eth.chain_id,
        "latest_block": w3.eth.block_number,
        "client": w3.client_version,
    }
