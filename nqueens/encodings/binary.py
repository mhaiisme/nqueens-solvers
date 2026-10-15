"""Binary (bitwise) At-Most-One (AMO) encoding (Frisch & Giannaros, 2010).

Introduces k = ceil(log2(m)) auxiliary variables y_1, ..., y_k representing
the binary index of which literal (if any) is true.

For literal x_i (0 <= i < m) and each bit j (0 <= j < k):
- if bit j of i is 1: (-x_i v y_j)
- if bit j of i is 0: (-x_i v -y_j)

Properties:
- Auxiliary variables: ceil(log2(m))
- Clauses: m * ceil(log2(m))
"""
import math
from typing import List
from .base import AMOEncoder, ClauseConsumer, VarManager


class BinaryEncoder(AMOEncoder):
    name: str = "binary"

    def encode_amo(self, literals: List[int], emit: ClauseConsumer, var_mgr: VarManager) -> None:
        m = len(literals)
        if m <= 1:
            return
        k = math.ceil(math.log2(m))
        ys = var_mgr.new_vars(k)
        for i, lit in enumerate(literals):
            for j in range(k):
                bit = (i >> j) & 1
                y_lit = ys[j] if bit else -ys[j]
                emit([-lit, y_lit])
