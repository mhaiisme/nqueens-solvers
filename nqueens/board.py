"""Board representation and geometry for the N-Queens problem."""
from typing import List, Tuple

Cell = Tuple[int, int]
Line = List[Cell]


def cell_to_var(i: int, j: int, n: int) -> int:
    """Map cell (i, j) on an N x N board (0-indexed) to a 1-based DIMACS variable.

    Convention: variable index = i * N + j + 1 (1 <= var <= N^2).
    """
    return i * n + j + 1


def var_to_cell(v: int, n: int) -> Cell:
    """Map 1-based DIMACS variable back to (row, col) cell (0-indexed)."""
    idx = v - 1
    return idx // n, idx % n


def get_board_lines(n: int) -> List[Line]:
    """Return all lines on an N x N board that require constraints.

    Returns:
        A list of lines, where each line is a list of (i, j) coordinates.
        - First N lines: rows (length N).
        - Next N lines: columns (length N).
        - Next 2N - 3 lines: main diagonals (i - j = d) with length >= 2.
        - Next 2N - 3 lines: anti-diagonals (i + j = s) with length >= 2.
        Total lines: 6N - 6.
        Total line length: 4N^2 - 4.
    """
    lines: List[Line] = []

    # 1. Rows
    for i in range(n):
        lines.append([(i, j) for j in range(n)])

    # 2. Columns
    for j in range(n):
        lines.append([(i, j) for i in range(n)])

    # 3. Diagonals (i - j = const), length >= 2
    for d in range(-(n - 1), n):
        diag = [(i, i - d) for i in range(n) if 0 <= i - d < n]
        if len(diag) >= 2:
            lines.append(diag)

    # 4. Anti-diagonals (i + j = const), length >= 2
    for s in range(2 * n - 1):
        adiag = [(i, s - i) for i in range(n) if 0 <= s - i < n]
        if len(adiag) >= 2:
            lines.append(adiag)

    return lines


def format_board(n: int, queens: List[Cell], unicode_chars: bool = False) -> str:
    """Format an N x N board with queens as a readable text grid."""
    q_set = set(queens)
    q_sym = "Q "
    empty_sym = ". "
    res = []
    for i in range(n):
        row_str = "".join(q_sym if (i, j) in q_set else empty_sym for j in range(n))
        res.append(row_str)
    return "\n".join(res)
