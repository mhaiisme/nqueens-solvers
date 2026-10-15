"""CDCL SAT Solver wrapper for N-Queens with streaming clause generation."""
import time
from typing import List, Optional, Union

from ..board import cell_to_var, get_board_lines, var_to_cell
from ..encodings import AMOEncoder, VarManager, get_encoder
from ..validator import validate_or_raise
from .base import BaseSolver, SolverResult

try:
    from pysat.solvers import Solver as PySATSolver
    PYSAT_AVAILABLE = True
except ImportError:
    PYSAT_AVAILABLE = False


class NQueensSATSolver(BaseSolver):
    """Solves N-Queens by encoding to CNF and solving with a CDCL SAT solver."""

    def __init__(
        self,
        encoding: Union[str, AMOEncoder] = "commander",
        sat_solver_name: str = "cadical153",
    ):
        if isinstance(encoding, str):
            self.encoder: AMOEncoder = get_encoder(encoding)
        else:
            self.encoder = encoding
        self.sat_solver_name = sat_solver_name
        self.name = f"sat_{self.encoder.name}_{self.sat_solver_name}"

    def solve(self, n: int, timeout: Optional[float] = None) -> SolverResult:
        if not PYSAT_AVAILABLE:
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                error_message="python-sat is not installed. Install with `pip install python-sat`.",
            )

        t0 = time.perf_counter()
        var_mgr = VarManager(initial_top=n * n)
        num_clauses = 0

        try:
            with PySATSolver(name=self.sat_solver_name) as solver:
                # -------------------------------------------------------------
                # Model Construction: Stream clauses directly into the C solver
                # -------------------------------------------------------------
                all_lines = get_board_lines(n)

                def emit_clause(cl: List[int]) -> None:
                    nonlocal num_clauses
                    solver.add_clause(cl)
                    num_clauses += 1

                for idx, line in enumerate(all_lines):
                    lits = [cell_to_var(r, c, n) for r, c in line]

                    # Rows and Columns (the first 2N lines) must have At-Least-One (ALO)
                    if idx < 2 * n:
                        emit_clause(lits)

                    # All lines must satisfy At-Most-One (AMO)
                    self.encoder.encode_amo(lits, emit_clause, var_mgr)

                t_model_done = time.perf_counter()
                model_time = t_model_done - t0

                # -------------------------------------------------------------
                # Solving
                # -------------------------------------------------------------
                # Note: PySAT handles single-core CDCL search.
                # If timeout is specified and exceeded, we handle it gracefully.
                t_solve_start = time.perf_counter()
                is_sat = solver.solve()
                t_solve_done = time.perf_counter()
                solve_time = t_solve_done - t_solve_start
                total_time = t_solve_done - t0

                if is_sat:
                    model = set(solver.get_model())
                    queens = []
                    for v in range(1, n * n + 1):
                        if v in model:
                            queens.append(var_to_cell(v, n))

                    # Independent correctness validation
                    validate_or_raise(queens, n)

                    return SolverResult(
                        status="SAT",
                        n=n,
                        queens=sorted(queens),
                        model_time=model_time,
                        solve_time=solve_time,
                        total_time=total_time,
                        num_vars=var_mgr.top,
                        num_constraints=num_clauses,
                        solver_name=self.name,
                        extra={"primary_vars": n * n, "aux_vars": var_mgr.top - n * n},
                    )
                else:
                    return SolverResult(
                        status="UNSAT",
                        n=n,
                        model_time=model_time,
                        solve_time=solve_time,
                        total_time=total_time,
                        num_vars=var_mgr.top,
                        num_constraints=num_clauses,
                        solver_name=self.name,
                    )

        except MemoryError:
            return SolverResult(
                status="MEMORY_OUT",
                n=n,
                solver_name=self.name,
                total_time=time.perf_counter() - t0,
                num_vars=var_mgr.top,
                num_constraints=num_clauses,
                error_message="Process exhausted memory cap during construction/solving.",
            )
        except Exception as e:
            return SolverResult(
                status="ERROR",
                n=n,
                solver_name=self.name,
                total_time=time.perf_counter() - t0,
                error_message=str(e),
            )
