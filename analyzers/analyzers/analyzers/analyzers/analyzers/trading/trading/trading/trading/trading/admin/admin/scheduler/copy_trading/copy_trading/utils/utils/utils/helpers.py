import re
from config import SUPPORTED_NETWORKS

def is_valid_address(address, network):
    if network == "bsc":
        return re.match(r'^0x[a-fA-F0-9]{40}$', address) is not None
    elif network == "solana":
        return len(address) >= 32 and len(address) <= 44
    elif network == "ton":
        return address.startswith(('EQD', 'UQD')) and len(address) > 30
    return False

def get_explorer_link(network, tx_hash):
    return f"{SUPPORTED_NETWORKS[network]['explorer']}{tx_hash}"
