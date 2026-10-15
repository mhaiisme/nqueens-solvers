"""2-Product (Grid) At-Most-One (AMO) encoding (Chen, ModRef 2010).

Arranges the m variables on a p x q 2D grid, with p = ceil(sqrt(m)), q = ceil(m / p).
Introduces p row variables r_0, ..., r_{p-1} and q column variables c_0, ..., c_{q-1}.

For each literal x at position (u, v):
- (-x v r_u)
- (-x v c_v)

Then AMO is applied recursively to the row variables r, and to the column variables c,
with base case <= 4 variables using pairwise encoding.

Properties:
- Auxiliary variables: ~ 2 * sqrt(m)
- Clauses: ~ 2m + O(sqrt(m))
"""
import itertools
import math
from typing import List
from .base import AMOEncoder, ClauseConsumer, VarManager


class ProductEncoder(AMOEncoder):
    name: str = "product"

    def encode_amo(self, literals: List[int], emit: ClauseConsumer, var_mgr: VarManager) -> None:
        m = len(literals)
        if m <= 1:
            return
        if m <= 4:
            for a, b in itertools.combinations(literals, 2):
                emit([-a, -b])
            return

        p = math.ceil(math.sqrt(m))
        q = math.ceil(m / p)

        r = var_mgr.new_vars(p)
        c = var_mgr.new_vars(q)

        for idx, x in enumerate(literals):
            u = idx // q
            v = idx % q
            emit([-x, r[u]])
            emit([-x, c[v]])

        # Recurse on rows and cols
        self.encode_amo(r, emit, var_mgr)
        self.encode_amo(c, emit, var_mgr)
