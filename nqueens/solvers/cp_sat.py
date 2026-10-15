"""Google OR-Tools CP-SAT solver implementations for N-Queens.

Supports both:
1. Integer formulation: N variables with 3 x AddAllDifferent constraints.
2. Boolean formulation: N^2 binary variables with AddExactlyOne and AddAtMostOne.
"""
import time
from typing import Optional

from ..board import get_board_lines
from ..validator import validate_or_raise
from .base import BaseSolver, SolverResult

try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False


class NQueensCPSATSolver(BaseSolver):
    """OR-Tools CP-SAT solver for N-Queens."""

    def __init__(self, model_type: str = "int"):
        """
        Args:
            model_type: 'int' for AllDifferent integer model, or 'bool' for 0/1 boolean model.
        """
        norm_type = model_type.strip().lower()
        if norm_type not in ("int", "bool"):
            raise ValueError(f"model_type must be 'int' or 'bool', got '{model_type}'")
        self.model_type = norm_type
        self.name = f"cp_sat_{self.model_type}"

    def solve(self, n: int, timeout: Optional[float] = 30.0) -> SolverResult:
        if not ORTOOLS_AVAILABLE:
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message="ortools is not installed. Install with `pip install ortools`.",
            )

        t0 = time.perf_counter()
        model = cp_model.CpModel()

        if self.model_type == "int":
            # -------------------------------------------------------------
            # Integer formulation: q[i] is the column of the queen in row i
            # -------------------------------------------------------------
            q = [model.NewIntVar(0, n - 1, f"q_{i}") for i in range(n)]

            # 1. Columns distinct
            model.AddAllDifferent(q)

            # 2. Main diagonals distinct: q[i] - i
            model.AddAllDifferent([q[i] - i for i in range(n)])

            # 3. Anti-diagonals distinct: q[i] + i
            model.AddAllDifferent([q[i] + i for i in range(n)])

            num_vars = n
            num_constrs = 3
        else:
            # -------------------------------------------------------------
            # Boolean formulation: x[i, j] is 1 iff queen occupies (i, j)
            # -------------------------------------------------------------
            x = {}
            for i in range(n):
                for j in range(n):
                    x[i, j] = model.NewBoolVar(f"x_{i}_{j}")

            all_lines = get_board_lines(n)
            num_constrs = 0

            for idx, line in enumerate(all_lines):
                lits = [x[r, c] for r, c in line]
                if idx < 2 * n:
                    model.AddExactlyOne(lits)
                else:
                    model.AddAtMostOne(lits)
                num_constrs += 1

            num_vars = n * n

        t_model_done = time.perf_counter()
        model_time = t_model_done - t0

        # Configure solver to single-threaded mode matching benchmark protocol
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 1
        if timeout is not None:
            solver.parameters.max_time_in_seconds = timeout

        t_solve_start = time.perf_counter()
        status = solver.Solve(model)
        t_solve_done = time.perf_counter()
        solve_time = t_solve_done - t_solve_start
        total_time = t_solve_done - t0

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            if self.model_type == "int":
                queens = [(i, int(solver.Value(q[i]))) for i in range(n)]
            else:
                queens = [(i, j) for i in range(n) for j in range(n) if solver.Value(x[i, j]) == 1]

            validate_or_raise(queens, n)

            return SolverResult(
                status="SAT",
                n=n,
                queens=sorted(queens),
                model_time=model_time,
                solve_time=solve_time,
                total_time=total_time,
                num_vars=num_vars,
                num_constraints=num_constrs,
                solver_name=self.name,
                extra={"wall_time": solver.WallTime(), "branches": solver.NumBranches()},
            )
        elif status == cp_model.UNKNOWN:
            return SolverResult(
                status="TIMEOUT" if solve_time >= (timeout or 30.0) * 0.95 else "UNKNOWN",
                n=n,
                model_time=model_time,
                solve_time=solve_time,
                total_time=total_time,
                num_vars=num_vars,
                num_constraints=num_constrs,
                solver_name=self.name,
                error_message="Time limit exceeded or search interrupted.",
            )
        else:
            return SolverResult(
                status="UNSAT",
                n=n,
                model_time=model_time,
                solve_time=solve_time,
                total_time=total_time,
                num_vars=num_vars,
                num_constraints=num_constrs,
                solver_name=self.name,
            )
