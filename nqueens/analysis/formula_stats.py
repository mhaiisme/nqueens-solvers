"""Theoretical closed-form formulas vs measured CNF size for N-Queens.

Reproduces and verifies Table 3 from the report:
- Pairwise: Theta(N^3) clauses. Exact formula: N*(N-1)*(5N-1)/3 + 2N.
- Sequential: Theta(N^2) clauses and aux vars.
  Exact clauses: 12*(N-1)^2 + 2N.
  Exact aux vars: 2*(2N-1)*(N-1).
"""
from typing import Dict, Tuple, Union

from ..board import cell_to_var, get_board_lines
from ..encodings import AMOEncoder, VarManager, get_encoder


def pairwise_clauses_closed_form(n: int) -> int:
    """Exact closed-form total clause count for Pairwise encoding on N-Queens.

    Sum of binom(|L|, 2) over all 6N-6 lines, plus 2N ALO clauses:
    = N * (N - 1) * (5N - 1) / 3 + 2N.
    """
    return n * (n - 1) * (5 * n - 1) // 3 + 2 * n


def sequential_clauses_closed_form(n: int) -> int:
    """Exact closed-form total clause count for Sequential Counter on N-Queens.

    Sum of (3|L| - 4) over all lines with |L| >= 2, plus 2N ALO clauses:
    = 12 * (N - 1)^2 + 2N.
    """
    return 12 * (n - 1) ** 2 + 2 * n


def sequential_aux_vars_closed_form(n: int) -> int:
    """Exact closed-form auxiliary variable count for Sequential Counter on N-Queens.

    Sum of (|L| - 1) over all lines with |L| >= 2:
    = 2 * (2N - 1) * (N - 1).
    """
    return 2 * (2 * n - 1) * (n - 1)


def measure_cnf_size(n: int, encoding: Union[str, AMOEncoder]) -> Tuple[int, int]:
    """Measure actual variable and clause counts by running the encoder.

    Returns:
        (num_vars, num_clauses)
    """
    encoder = get_encoder(encoding) if isinstance(encoding, str) else encoding
    var_mgr = VarManager(initial_top=n * n)
    clause_count = 0

    def sink(cl):
        nonlocal clause_count
        clause_count += 1

    all_lines = get_board_lines(n)
    for idx, line in enumerate(all_lines):
        lits = [cell_to_var(r, c, n) for r, c in line]
        if idx < 2 * n:
            sink(lits)
        encoder.encode_amo(lits, sink, var_mgr)

    return var_mgr.top, clause_count


def verify_table_3_counts() -> Dict[str, Dict[int, Dict[str, int]]]:
    """Generate and return CNF size table for N=64, 256, 1024 across encodings."""
    table = {}
    encodings = ["pairwise", "binary", "sequential", "commander", "product"]

    for enc_name in encodings:
        table[enc_name] = {}
        for n in (64, 256, 1024):
            if enc_name == "pairwise" and n > 64:
                # Closed-form theoretical counts as in paper (†)
                vars_cnt = n * n
                clauses_cnt = pairwise_clauses_closed_form(n)
            else:
                vars_cnt, clauses_cnt = measure_cnf_size(n, enc_name)
            table[enc_name][n] = {"vars": vars_cnt, "clauses": clauses_cnt}

    return table
