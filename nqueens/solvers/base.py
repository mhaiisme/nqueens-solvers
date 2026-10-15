"""Base abstractions for N-Queens solvers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

Cell = Tuple[int, int]


@dataclass
class SolverResult:
    """Standardized result returned by any N-Queens solver."""
    status: str  # 'SAT', 'UNSAT', 'TIMEOUT', 'MEMORY_OUT', 'LICENSE_LIMIT', 'ERROR'
    n: int
    queens: List[Cell] = field(default_factory=list)
    model_time: float = 0.0
    solve_time: float = 0.0
    total_time: float = 0.0
    num_vars: int = 0
    num_constraints: int = 0
    solver_name: str = ""
    error_message: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_sat(self) -> bool:
        return self.status == "SAT"

    def summary(self) -> str:
        s = f"[{self.solver_name}] N={self.n}: {self.status} in {self.total_time:.4f}s"
        if self.is_sat:
            s += f" (vars={self.num_vars}, constrs={self.num_constraints})"
        elif self.error_message:
            s += f" ({self.error_message})"
        return s


class BaseSolver(ABC):
    """Abstract interface implemented by all solvers across SAT, CP, and ILP."""

    name: str = "base_solver"

    @abstractmethod
    def solve(self, n: int, timeout: Optional[float] = None) -> SolverResult:
        """Solve the N-Queens problem for board size n.

        Args:
            n: Board size (number of queens).
            timeout: Optional wall-clock timeout in seconds.

        Returns:
            SolverResult containing status, timings, and queen placements.
        """
        pass
