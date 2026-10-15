"""Unit tests for the independent N-Queens validator."""
import pytest
from nqueens.validator import ValidationError, validate_or_raise, validate_solution


def test_valid_8_queens():
    # Known 8-queens solution
    sol = [(0, 0), (1, 4), (2, 7), (3, 5), (4, 2), (5, 6), (6, 1), (7, 3)]
    is_valid, err = validate_solution(sol, 8)
    assert is_valid
    assert err is None
    validate_or_raise(sol, 8)


def test_wrong_count():
    sol = [(0, 0), (1, 4)]
    is_valid, err = validate_solution(sol, 4)
    assert not is_valid
    assert "Expected 4 queens" in err


def test_row_conflict():
    sol = [(0, 0), (0, 1), (2, 2), (3, 3)]
    is_valid, err = validate_solution(sol, 4)
    assert not is_valid
    assert "Row conflict" in err


def test_column_conflict():
    sol = [(0, 0), (1, 0), (2, 2), (3, 3)]
    is_valid, err = validate_solution(sol, 4)
    assert not is_valid
    assert "Column conflict" in err


def test_diagonal_conflict():
    sol = [(0, 0), (1, 1), (2, 3), (3, 2)]
    is_valid, err = validate_solution(sol, 4)
    assert not is_valid
    assert "Diagonal" in err


def test_antidiagonal_conflict():
    sol = [(0, 3), (1, 2), (2, 0), (3, 1)]
    is_valid, err = validate_solution(sol, 4)
    assert not is_valid
    assert "Anti-diagonal" in err
