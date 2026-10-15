"""Registry and factory for all N-Queens solvers across SAT, CP, and ILP."""
from typing import Dict, List
from .base import BaseSolver, SolverResult
from .sat_solver import NQueensSATSolver
from .cp_sat import NQueensCPSATSolver
from .gurobi_mip import NQueensGurobiSolver
from .cplex_cp import NQueensCPLEXCPSolver
from .cplex_mip import NQueensCPLEXMIPSolver


def get_solver(name: str, **kwargs) -> BaseSolver:
    """Retrieve an initialized solver instance by name.

    Supported names:
    - SAT solvers: 'sat' (default commander+cadical153),
      'cadical153', 'cadical195', 'glucose4', 'minisat22', 'kissat404', 'lingeling', 'maplechrono'
    - CP solvers: 'cp_sat' / 'cp_sat_int', 'cp_sat_bool', 'cplex_cp'
    - ILP solvers: 'gurobi' / 'gurobi_mip', 'cplex_mip'
    """
    norm = name.strip().lower().replace("-", "_")

    # CP Solvers
    if norm in ("cp_sat", "cp_sat_int", "cpsat_int"):
        return NQueensCPSATSolver(model_type="int")
    if norm in ("cp_sat_bool", "cpsat_bool"):
        return NQueensCPSATSolver(model_type="bool")
    if norm in ("cplex_cp", "cpo", "cp_optimizer"):
        return NQueensCPLEXCPSolver(**kwargs)

    # ILP Solvers
    if norm in ("gurobi", "gurobi_mip"):
        return NQueensGurobiSolver(**kwargs)
    if norm in ("cplex", "cplex_mip"):
        return NQueensCPLEXMIPSolver(**kwargs)

    # SAT Solvers
    known_sat_solvers = [
        "cadical153", "cadical195", "glucose4", "minisat22",
        "kissat404", "lingeling", "maplechrono", "cryptosat"
    ]
    if norm in known_sat_solvers:
        return NQueensSATSolver(sat_solver_name=norm, **kwargs)

    if norm == "sat":
        return NQueensSATSolver(**kwargs)

    raise ValueError(
        f"Unknown solver '{name}'. Supported options: 'sat' (with --sat-solver), "
        "'cp_sat_int', 'cp_sat_bool', 'cplex_cp', 'gurobi', 'cplex_mip'."
    )


__all__ = [
    "BaseSolver",
    "SolverResult",
    "NQueensSATSolver",
    "NQueensCPSATSolver",
    "NQueensGurobiSolver",
    "NQueensCPLEXCPSolver",
    "NQueensCPLEXMIPSolver",
    "get_solver",
]
