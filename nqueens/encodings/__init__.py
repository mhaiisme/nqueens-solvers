"""Registry and factory for all At-Most-One (AMO) SAT encodings."""
from typing import Dict, List
from .base import AMOEncoder, VarManager
from .pairwise import PairwiseEncoder
from .binary import BinaryEncoder
from .seq_counter import SequentialCounterEncoder
from .commander import CommanderEncoder
from .product import ProductEncoder
from .pysat_enc import create_pysat_encoders

ENCODERS: Dict[str, AMOEncoder] = {
    "pairwise": PairwiseEncoder(),
    "binary": BinaryEncoder(),
    "sequential": SequentialCounterEncoder(),
    "seqcounter": SequentialCounterEncoder(),  # alias
    "commander": CommanderEncoder(k=3),
    "product": ProductEncoder(),
}

# Add PySAT encodings if available
ENCODERS.update(create_pysat_encoders())


def get_encoder(name: str) -> AMOEncoder:
    """Retrieve an AMO encoder by name."""
    norm = name.strip().lower().replace("-", "_")
    if norm not in ENCODERS:
        avail = ", ".join(sorted(ENCODERS.keys()))
        raise ValueError(f"Unknown encoding '{name}'. Available encodings: {avail}")
    return ENCODERS[norm]


def list_available_encodings() -> List[str]:
    """Return a list of all registered encoding names."""
    return sorted(ENCODERS.keys())


__all__ = [
    "AMOEncoder",
    "VarManager",
    "PairwiseEncoder",
    "BinaryEncoder",
    "SequentialCounterEncoder",
    "CommanderEncoder",
    "ProductEncoder",
    "get_encoder",
    "list_available_encodings",
    "ENCODERS",
]
