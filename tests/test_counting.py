"""Unit tests for solution counting against OEIS A000170."""
import pytest
from nqueens.analysis import count_all_solutions


@pytest.mark.parametrize("n, expected", [(2, 0), (3, 0), (4, 2), (5, 10)])
def test_solution_counting_small(n, expected):
    cnt, _ = count_all_solutions(n, encoding="pairwise", sat_solver_name="cadical153")
    assert cnt == expected, f"Failed for N={n}: got {cnt}, expected {expected}"
