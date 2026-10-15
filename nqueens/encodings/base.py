"""Base abstractions for At-Most-One (AMO) SAT encodings."""
from abc import ABC, abstractmethod
from typing import Callable, List, Tuple

ClauseConsumer = Callable[[List[int]], None]


class VarManager:
    """Manages allocation of fresh Boolean variable IDs."""

    def __init__(self, initial_top: int = 0):
        self._top = initial_top

    @property
    def top(self) -> int:
        return self._top

    def new_var(self) -> int:
        self._top += 1
        return self._top

    def new_vars(self, count: int) -> List[int]:
        res = [self._top + 1 + i for i in range(count)]
        self._top += count
        return res


class AMOEncoder(ABC):
    """Abstract base class for an At-Most-One (AMO) encoding."""

    name: str = "base"

    @abstractmethod
    def encode_amo(self, literals: List[int], emit: ClauseConsumer, var_mgr: VarManager) -> None:
        """Generate CNF clauses enforcing that at most one literal in `literals` is true.

        Clauses are streamed directly to the `emit` callable to minimize memory overhead.
        Auxiliary variables must be allocated via `var_mgr.new_var()`.
        """
        pass

    def get_clauses(self, literals: List[int], initial_top: int) -> Tuple[List[List[int]], int]:
        """Convenience method to collect clauses into a Python list."""
        clauses: List[List[int]] = []
        var_mgr = VarManager(initial_top)
        self.encode_amo(literals, clauses.append, var_mgr)
        return clauses, var_mgr.top
