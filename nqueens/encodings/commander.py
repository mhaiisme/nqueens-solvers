"""Commander At-Most-One (AMO) encoding (Klieber & Kwon, 2007).

Partitions the m variables into groups of size k (default k = 3).
For each group:
- A commander variable c is introduced representing the disjunction of the group.
- An AMO constraint (pairwise) is enforced among the group members.
- If c is true, at least one group member is true: (-c v x_{g,1} v ... v x_{g,k}).
- If any group member is true, c is true: (-x_{g,i} v c).
Then AMO is applied recursively to the commander variables until <= 4 remain,
which are encoded pairwise.

Properties:
- Auxiliary variables: ~ m / (k - 1) = O(m)
- Clauses: ~ 3.5m = O(m)
"""
import itertools
from typing import List
from .base import AMOEncoder, ClauseConsumer, VarManager


class CommanderEncoder(AMOEncoder):
    name: str = "commander"

    def __init__(self, k: int = 3):
        self.k = k

    def encode_amo(self, literals: List[int], emit: ClauseConsumer, var_mgr: VarManager) -> None:
        m = len(literals)
        if m <= 1:
            return
        if m <= 4:
            for a, b in itertools.combinations(literals, 2):
                emit([-a, -b])
            return

        cmds: List[int] = []
        for g in range(0, m, self.k):
            grp = literals[g : g + self.k]
            if len(grp) == 1:
                cmds.append(grp[0])
                continue

            c = var_mgr.new_var()

            # 1. At most one in this group
            for a, b in itertools.combinations(grp, 2):
                emit([-a, -b])

            # 2. c <-> at least one in grp: (-c v grp)
            emit([-c] + grp)

            # 3. For each x in grp: x -> c  <=>  (-x v c)
            for x in grp:
                emit([-x, c])

            cmds.append(c)

        # Recurse on the commanders
        self.encode_amo(cmds, emit, var_mgr)
