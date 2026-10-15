"""Pairwise (binomial) At-Most-One (AMO) encoding.

For every pair of literals (xi, xj) with i < j, adds the clause (-xi v -xj).
Properties:
- Auxiliary variables: 0
- Clauses: m * (m - 1) / 2 = O(m^2)
"""
import itertools
from typing import List
from .base import AMOEncoder, ClauseConsumer, VarManager


class PairwiseEncoder(AMOEncoder):
    name: str = "pairwise"

    def encode_amo(self, literals: List[int], emit: ClauseConsumer, var_mgr: VarManager) -> None:
        m = len(literals)
        if m <= 1:
            return
        for a, b in itertools.combinations(literals, 2):
            emit([-a, -b])
