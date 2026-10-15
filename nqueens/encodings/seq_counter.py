"""Sequential Counter At-Most-One (AMO) encoding (Sinz, CP 2005).

Introduces m - 1 auxiliary variables s_0, ..., s_{m-2} where s_i indicates
that at least one of x_0, ..., x_i is true.

Clauses:
- (-x_0 v s_0)
- For 1 <= i < m - 1:
    (-x_i v s_i)
    (-s_{i-1} v s_i)
    (-s_{i-1} v -x_i)
- (-s_{m-2} v -x_{m-1})

Properties:
- Auxiliary variables: m - 1
- Clauses: 3m - 4 (for m >= 2)
"""
from typing import List
from .base import AMOEncoder, ClauseConsumer, VarManager


class SequentialCounterEncoder(AMOEncoder):
    name: str = "sequential"

    def encode_amo(self, literals: List[int], emit: ClauseConsumer, var_mgr: VarManager) -> None:
        m = len(literals)
        if m <= 1:
            return

        s = var_mgr.new_vars(m - 1)

        # Base clause: x_0 -> s_0
        emit([-literals[0], s[0]])

        # Middle steps: 1 <= i < m - 1
        for i in range(1, m - 1):
            emit([-literals[i], s[i]])
            emit([-s[i - 1], s[i]])
            emit([-s[i - 1], -literals[i]])

        # Final clause: s_{m-2} -> not x_{m-1}
        emit([-s[m - 2], -literals[m - 1]])
