"""Gurobi Integer Linear Programming (MIP) solver for N-Queens."""
import time
from typing import Optional

from ..board import get_board_lines
from ..validator import validate_or_raise
from .base import BaseSolver, SolverResult

try:
    import gurobipy as gp
    from gurobipy import GRB
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False


class NQueensGurobiSolver(BaseSolver):
    """Gurobi MIP solver for N-Queens."""

    name: str = "gurobi_mip"

    def __init__(self, check_license_cap: bool = True):
        self.check_license_cap = check_license_cap

    def solve(self, n: int, timeout: Optional[float] = 30.0) -> SolverResult:
        if not GUROBI_AVAILABLE:
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message="gurobipy is not installed. Install with `pip install gurobipy`.",
            )

        # Community / evaluation license allows at most 2000 decision variables.
        # N-Queens uses N^2 binary variables -> max N under community license is floor(sqrt(2000)) = 44.
        if self.check_license_cap and n > 44:
            return SolverResult(
                status="LICENSE_LIMIT",
                n=n,
                solver_name=self.name,
                num_vars=n * n,
                error_message=(
                    f"Board size N={n} requires {n*n} variables, exceeding Gurobi "
                    "community license ceiling of 2000 variables (N <= 44)."
                ),
            )

        t0 = time.perf_counter()

        try:
            with gp.Env(empty=True) as env:
                env.setParam("OutputFlag", 0)
                env.start()

                with gp.Model(f"nqueens_{n}", env=env) as model:
                    model.setParam("Threads", 1)  # Single-thread benchmark protocol
                    if timeout is not None:
                        model.setParam("TimeLimit", timeout)

                    # 1. Binary decision variables x[i, j]
                    x = {}
                    for i in range(n):
                        for j in range(n):
                            x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

                    all_lines = get_board_lines(n)
                    num_constrs = 0

                    # 2. Add linear constraints for rows, cols, diagonals
                    for idx, line in enumerate(all_lines):
                        expr = gp.quicksum(x[r, c] for r, c in line)
                        if idx < 2 * n:
                            # Rows and Columns: exactly one queen
                            model.addConstr(expr == 1, name=f"line_{idx}")
                        else:
                            # Diagonals and Anti-diagonals: at most one queen
                            model.addConstr(expr <= 1, name=f"line_{idx}")
                        num_constrs += 1

                    t_model_done = time.perf_counter()
                    model_time = t_model_done - t0

                    # 3. Optimize (feasibility)
                    t_solve_start = time.perf_counter()
                    model.optimize()
                    t_solve_done = time.perf_counter()

                    solve_time = t_solve_done - t_solve_start
                    total_time = t_solve_done - t0

                    if model.Status in (GRB.OPTIMAL, GRB.SUBOPTIMAL) and model.SolCount > 0:
                        queens = [
                            (i, j)
                            for i in range(n)
                            for j in range(n)
                            if x[i, j].X > 0.5
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
                            extra={"node_count": model.NodeCount},
                        )
                    elif model.Status == GRB.TIME_LIMIT:
                        return SolverResult(
                            status="TIMEOUT",
                            n=n,
                            model_time=model_time,
                            solve_time=solve_time,
                            total_time=total_time,
                            num_vars=n * n,
                            num_constraints=num_constrs,
                            solver_name=self.name,
                            error_message=f"Exceeded time limit of {timeout}s.",
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

        except gp.GurobiError as ge:
            if "size limit" in str(ge).lower():
                return SolverResult(
                    status="LICENSE_LIMIT",
                    n=n,
                    solver_name=self.name,
                    error_message=str(ge),
                )
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message=f"Gurobi error: {ge}",
            )
        except Exception as e:
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message=str(e),
            )
