"""IBM CPLEX MIP solver for N-Queens via docplex.mp."""
import time
from typing import Optional

from ..board import get_board_lines
from ..validator import validate_or_raise
from .base import BaseSolver, SolverResult

try:
    from docplex.mp.model import Model as MPModel
    DOCPLEX_MP_AVAILABLE = True
except ImportError:
    DOCPLEX_MP_AVAILABLE = False


class NQueensCPLEXMIPSolver(BaseSolver):
    """IBM CPLEX MIP solver for N-Queens."""

    name: str = "cplex_mip"

    def __init__(self, check_license_cap: bool = True):
        self.check_license_cap = check_license_cap

    def solve(self, n: int, timeout: Optional[float] = 30.0) -> SolverResult:
        if not DOCPLEX_MP_AVAILABLE:
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message="docplex is not installed. Install with `pip install docplex`.",
            )

        # Community Edition rejects models with more than 1000 variables.
        # N^2 <= 1000  <=>  N <= floor(sqrt(1000)) = 31.
        if self.check_license_cap and n > 31:
            return SolverResult(
                status="LICENSE_LIMIT",
                n=n,
                solver_name=self.name,
                num_vars=n * n,
                error_message=(
                    f"Board size N={n} requires {n*n} variables, exceeding CPLEX MIP "
                    "Community Edition ceiling of 1000 variables (N <= 31)."
                ),
            )

        t0 = time.perf_counter()

        try:
            model = MPModel(f"nqueens_mip_{n}")
            model.context.cplex_parameters.threads = 1  # Single-threaded protocol
            if timeout is not None:
                model.set_time_limit(timeout)

            # 1. Binary variables x[i, j]
            x = {}
            for i in range(n):
                for j in range(n):
                    x[i, j] = model.binary_var(name=f"x_{i}_{j}")

            all_lines = get_board_lines(n)
            num_constrs = 0

            # 2. Linear constraints
            for idx, line in enumerate(all_lines):
                expr = model.sum(x[r, c] for r, c in line)
                if idx < 2 * n:
                    model.add_constraint(expr == 1)
                else:
                    model.add_constraint(expr <= 1)
                num_constrs += 1

            t_model_done = time.perf_counter()
            model_time = t_model_done - t0

            # 3. Solve
            t_solve_start = time.perf_counter()
            msol = model.solve(log_output=False)
            t_solve_done = time.perf_counter()

            solve_time = t_solve_done - t_solve_start
            total_time = t_solve_done - t0

            if msol:
                queens = [
                    (i, j)
                    for i in range(n)
                    for j in range(n)
                    if msol.get_value(x[i, j]) > 0.5
                ]
                validate_or_raise(queens, n)

                return SolverResult(
                    status="SAT",
                    n=n,
                    queens=sorted(queens),
                    model_time=model_time,
                    solve_time=solve_time,
                    total_time=total_time,
                    num_vars=n * n,
                    num_constraints=num_constrs,
                    solver_name=self.name,
                )
            elif model.solve_details.status == "time limit exceeded":
                return SolverResult(
                    status="TIMEOUT",
                    n=n,
                    model_time=model_time,
                    solve_time=solve_time,
                    total_time=total_time,
                    num_vars=n * n,
                    num_constraints=num_constrs,
                    solver_name=self.name,
                    error_message=f"Time limit of {timeout}s exceeded.",
                )
            else:
                return SolverResult(
                    status="UNSAT",
                    n=n,
                    model_time=model_time,
                    solve_time=solve_time,
                    total_time=total_time,
                    num_vars=n * n,
                    num_constraints=num_constrs,
                    solver_name=self.name,
                )

        except Exception as e:
            msg = str(e)
            if "no cplex runtime found" in msg.lower():
                return SolverResult(
                    status="ERROR",
                    n=n,
                    solver_name=self.name,
                    error_message=(
                        "IBM ILOG CPLEX runtime not found. "
                        "Install CPLEX Optimization Studio and ensure cplex is linked to Python."
                    ),
                )
            if "license" in msg.lower() or "size limit" in msg.lower():
                return SolverResult(
                    status="LICENSE_LIMIT",
                    n=n,
                    solver_name=self.name,
                    error_message=msg,
                )
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message=msg,
            )
