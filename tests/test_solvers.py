"""Unit tests for N-Queens solvers across SAT, CP, and ILP."""
import pytest
from nqueens.solvers import get_solver
from nqueens.validator import validate_solution


@pytest.mark.parametrize("solver_name", ["cadical153", "minisat22", "glucose4"])
def test_sat_solvers(solver_name):
    solver = get_solver("sat", sat_solver_name=solver_name, encoding="commander")
    res = solver.solve(8, timeout=10.0)
    assert res.is_sat
    assert len(res.queens) == 8
    is_valid, err = validate_solution(res.queens, 8)
    assert is_valid, err


def test_cp_sat_int():
    try:
        import ortools
    except ImportError:
        pytest.skip("ortools not installed")

    solver = get_solver("cp_sat_int")
    res = solver.solve(8, timeout=10.0)
    assert res.is_sat
    assert len(res.queens) == 8
    is_valid, err = validate_solution(res.queens, 8)
    assert is_valid, err


def test_cp_sat_bool():
    try:
        import ortools
    except ImportError:
        pytest.skip("ortools not installed")

    solver = get_solver("cp_sat_bool")
    res = solver.solve(8, timeout=10.0)
    assert res.is_sat
    assert len(res.queens) == 8
    is_valid, err = validate_solution(res.queens, 8)
    assert is_valid, err


def test_gurobi_mip():
    try:
        import gurobipy
    except ImportError:
        pytest.skip("gurobipy not installed")

    solver = get_solver("gurobi")
    res = solver.solve(8, timeout=10.0)
    assert res.is_sat
    assert len(res.queens) == 8
    is_valid, err = validate_solution(res.queens, 8)
    assert is_valid, err
