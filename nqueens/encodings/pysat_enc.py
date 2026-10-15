"""Wrappers for PySAT's built-in cardinality encodings (CardEnc)."""
from typing import List
from .base import AMOEncoder, ClauseConsumer, VarManager

try:
    from pysat.card import CardEnc, EncType
    PYSAT_AVAILABLE = True
except ImportError:
    PYSAT_AVAILABLE = False


class PySATCardinalityEncoder(AMOEncoder):
    """Wrapper around PySAT's CardEnc.atmost with bound=1."""

    def __init__(self, name: str, enc_type_id: int):
        self.name = name
        self.enc_type_id = enc_type_id

    def encode_amo(self, literals: List[int], emit: ClauseConsumer, var_mgr: VarManager) -> None:
        if not PYSAT_AVAILABLE:
            raise RuntimeError(
                f"PySAT is not installed. Cannot use PySAT encoding '{self.name}'. "
                "Install with `pip install python-sat`."
            )
        m = len(literals)
        if m <= 1:
            return

        cnf = CardEnc.atmost(
            lits=literals,
            bound=1,
            top_id=var_mgr.top,
            encoding=self.enc_type_id,
        )

        for clause in cnf.clauses:
            emit(clause)

        if cnf.nv > var_mgr.top:
            var_mgr._top = cnf.nv


def create_pysat_encoders():
    """Create instances for the supported PySAT cardinality encodings."""
    if not PYSAT_AVAILABLE:
        return {}
    return {
        "pysat_pairwise": PySATCardinalityEncoder("pysat_pairwise", EncType.pairwise),
        "pysat_seqcounter": PySATCardinalityEncoder("pysat_seqcounter", EncType.seqcounter),
        "pysat_bitwise": PySATCardinalityEncoder("pysat_bitwise", EncType.bitwise),
        "pysat_ladder": PySATCardinalityEncoder("pysat_ladder", EncType.ladder),
    }
