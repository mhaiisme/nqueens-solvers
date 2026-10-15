"""Unit tests for all At-Most-One (AMO) encodings."""
import itertools
import pytest
from nqueens.encodings import ENCODERS, AMOEncoder, VarManager

try:
    from pysat.solvers import Solver as PySATSolver
    PYSAT_AVAILABLE = True
except ImportError:
    PYSAT_AVAILABLE = False


@pytest.mark.skipif(not PYSAT_AVAILABLE, reason="python-sat not installed")
@pytest.mark.parametrize("enc_name", list(ENCODERS.keys()))
def test_amo_correctness_small(enc_name):
    encoder: AMOEncoder = ENCODERS[enc_name]
    m = 5
    lits = list(range(1, m + 1))

    # Test all 2^m assignments
    for bits in itertools.product([False, True], repeat=m):
        true_count = sum(bits)
        clauses, top = encoder.get_clauses(lits, initial_top=m)

        with PySATSolver(name="cadical153") as s:
            for cl in clauses:
                s.add_clause(cl)

            # Fix the inputs according to bits
            for idx, bit in enumerate(bits):
                var = lits[idx]
                s.add_clause([var if bit else -var])

            sat = s.solve()
            if true_count <= 1:
                assert sat, f"Encoding {enc_name} failed: should be SAT for {bits}"
            else:
                assert not sat, f"Encoding {enc_name} failed: should be UNSAT for {bits}"
