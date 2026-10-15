"""Independent solution validator for the N-Queens problem.

Verifies that any proposed solution satisfies all game rules:
- Exactly N queens placed on an N x N board.
- No two queens share a row.
- No two queens share a column.
- No two queens share a diagonal (i - j).
- No two queens share an anti-diagonal (i + j).
"""
from typing import List, Optional, Set, Tuple

Cell = Tuple[int, int]


class ValidationError(ValueError):
    """Raised when an N-Queens solution is invalid."""
    pass


def validate_solution(queens: List[Cell], n: int) -> Tuple[bool, Optional[str]]:
    """Validate that `queens` is a valid N-Queens solution on an N x N board.

    Args:
        queens: List of (row, col) coordinates (0-indexed).
        n: Board size.

    Returns:
        (is_valid, error_message): Tuple where error_message is None if valid.
    """
    if len(queens) != n:
        return False, f"Expected {n} queens, but got {len(queens)}."

    rows: Set[int] = set()
    cols: Set[int] = set()
    diags: Set[int] = set()
    adiags: Set[int] = set()

    for idx, (r, c) in enumerate(queens):
        if not (0 <= r < n and 0 <= c < n):
            return False, f"Queen #{idx+1} at ({r}, {c}) is outside the {n}x{n} board."

        if r in rows:
            return False, f"Row conflict: multiple queens in row {r}."
        rows.add(r)

        if c in cols:
            return False, f"Column conflict: multiple queens in column {c}."
        cols.add(c)

        d = r - c
        if d in diags:
            return False, f"Diagonal (i - j = {d}) conflict."
        diags.add(d)

        s = r + c
        if s in adiags:
            return False, f"Anti-diagonal (i + j = s = {s}) conflict."
        adiags.add(s)

    return True, None


def validate_or_raise(queens: List[Cell], n: int) -> None:
    """Validate solution and raise ValidationError if invalid."""
    is_valid, msg = validate_solution(queens, n)
    if not is_valid:
        raise ValidationError(msg)
