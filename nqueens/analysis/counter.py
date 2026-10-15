"""Exhaustive solution counting for N-Queens.

Reproduces Table 2 (and Table 4) from the paper:
Verifies encoding correctness by exhaustively enumerating all solutions
using SAT blocking clauses and comparing against OEIS A000170:
N=2: 0, N=3: 0, N=4: 2, N=5: 10, N=6: 4, N=7: 40, N=8: 92, N=9: 352.
"""
from typing import Dict, List, Optional, Tuple, Union

from ..board import cell_to_var, get_board_lines, var_to_cell
from ..encodings import AMOEncoder, VarManager, get_encoder
from ..validator import validate_or_raise

try:
    from pysat.solvers import Solver as PySATSolver
    PYSAT_AVAILABLE = True
except ImportError:
    PYSAT_AVAILABLE = False

OEIS_A000170: Dict[int, int] = {
    1: 1,
    2: 0,
    3: 0,
    4: 2,
    5: 10,
    6: 4,
    7: 40,
    8: 92,
    9: 352,
    10: 724,
    11: 2680,
    12: 14200,
}


def count_all_solutions(
    n: int,
    encoding: Union[str, AMOEncoder] = "pairwise",
    sat_solver_name: str = "cadical153",
    validate_each: bool = True,
) -> Tuple[int, List[List[Tuple[int, int]]]]:
    """Enumerate all solutions to N-Queens for a given board size N.

    Args:
        n: Board size.
        encoding: Name or instance of AMOEncoder.
        sat_solver_name: PySAT solver engine name.
        validate_each: If True, independently checks each solution found.

    Returns:
        (total_count, all_solutions)
    """
    if not PYSAT_AVAILABLE:
        raise RuntimeError("python-sat is required for solution counting.")

    encoder = get_encoder(encoding) if isinstance(encoding, str) else encoding
    var_mgr = VarManager(initial_top=n * n)

    solutions: List[List[Tuple[int, int]]] = []

    with PySATSolver(name=sat_solver_name) as solver:
        all_lines = get_board_lines(n)

        for idx, line in enumerate(all_lines):
            lits = [cell_to_var(r, c, n) for r, c in line]
            if idx < 2 * n:
                solver.add_clause(lits)
            encoder.encode_amo(lits, solver.add_clause, var_mgr)

        while solver.solve():
            model = set(solver.get_model())
            queens = []
            blocking_clause = []

            for v in range(1, n * n + 1):
                if v in model:
                    queens.append(var_to_cell(v, n))
                    # Invert the true primary variable for the blocking clause
                    blocking_clause.append(-v)

            if validate_each:
                validate_or_raise(queens, n)

            solutions.append(sorted(queens))

            # Add blocking clause: at least one queen must move
            solver.add_clause(blocking_clause)

    return len(solutions), solutions


def verify_against_oeis(
    n_values: Optional[List[int]] = None,
    encoding: Union[str, AMOEncoder] = "pairwise",
    sat_solver_name: str = "cadical153",
) -> Dict[int, Dict[str, Union[int, bool]]]:
    """Verify that all solution counts match OEIS A000170 for N=2..9."""
    if n_values is None:
        n_values = [2, 3, 4, 5, 6, 7, 8, 9]

    results = {}
    for n in n_values:
        expected = OEIS_A000170.get(n)
        found, _ = count_all_solutions(n, encoding=encoding, sat_solver_name=sat_solver_name)
        results[n] = {
            "found": found,
            "expected": expected,
            "correct": (found == expected),
        }
    return results
