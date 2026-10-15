"""IBM CPLEX CP Optimizer solver for N-Queens via docplex.cp."""
import time
from typing import Optional

from ..validator import validate_or_raise
from .base import BaseSolver, SolverResult

try:
    from docplex.cp.model import CpoModel
    DOCPLEX_CP_AVAILABLE = True
except ImportError:
    DOCPLEX_CP_AVAILABLE = False


class NQueensCPLEXCPSolver(BaseSolver):
    """IBM ILOG CP Optimizer solver for N-Queens."""

    name: str = "cplex_cp"

    def __init__(self, check_license_cap: bool = True):
        self.check_license_cap = check_license_cap

    def solve(self, n: int, timeout: Optional[float] = 30.0) -> SolverResult:
        if not DOCPLEX_CP_AVAILABLE:
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message="docplex is not installed. Install with `pip install docplex`.",
            )

        # Community Edition refuses search spaces larger than 2^1000.
        # N^N <= 2^1000  <=>  N * log2(N) <= 1000 (allows up to N = 128; fails at N = 200).
        if self.check_license_cap and n > 128:
            return SolverResult(
                status="LICENSE_LIMIT",
                n=n,
                solver_name=self.name,
                num_vars=n,
                error_message=(
                    f"Board size N={n} search space N^N exceeds CP Optimizer "
                    "Community Edition ceiling of 2^1000 (N <= 128)."
                ),
            )

        t0 = time.perf_counter()

        try:
            model = CpoModel(f"nqueens_cp_{n}")

            # 1. Variables: q[i] is column of queen in row i
            q = [model.integer_var(0, n - 1, name=f"q_{i}") for i in range(n)]

            # 2. AllDifferent constraints
            model.add(model.all_diff(q))
            model.add(model.all_diff([q[i] + i for i in range(n)]))
            model.add(model.all_diff([q[i] - i for i in range(n)]))

            t_model_done = time.perf_counter()
            model_time = t_model_done - t0

            # 3. Solve with single-worker and timeout
            t_solve_start = time.perf_counter()
            msol = model.solve(
                TimeLimit=timeout,
                Workers=1,
                LogVerbosity="Quiet",
            )
            t_solve_done = time.perf_counter()

            solve_time = t_solve_done - t_solve_start
            total_time = t_solve_done - t0

            if msol and msol.is_solution():
                queens = [(i, int(msol[q[i]])) for i in range(n)]
                validate_or_raise(queens, n)

                return SolverResult(
                    status="SAT",
                    n=n,
                    queens=sorted(queens),
                    model_time=model_time,
                    solve_time=solve_time,
                    total_time=total_time,
                    num_vars=n,
                    num_constraints=3,
                    solver_name=self.name,
                )
            elif msol and msol.get_solve_status() == "JobStopped":
                return SolverResult(
                    status="TIMEOUT",
                    n=n,
                    model_time=model_time,
                    solve_time=solve_time,
                    total_time=total_time,
                    num_vars=n,
                    num_constraints=3,
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
                    num_vars=n,
                    num_constraints=3,
                    solver_name=self.name,
                )

        except Exception as e:
            msg = str(e)
            if "no cplex runtime found" in msg.lower() or "not found" in msg.lower():
                return SolverResult(
                    status="ERROR",
                    n=n,
                    solver_name=self.name,
                    error_message=(
                        "IBM ILOG CP Optimizer executable not found on PATH. "
                        "Install CPLEX Optimization Studio and ensure `cpoptimizer` is available."
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
