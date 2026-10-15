"""Experiment runner script to reproduce the tables from the report."""
import argparse
import time

from nqueens.analysis import count_all_solutions, verify_table_3_counts
from nqueens.encodings import ENCODERS
from nqueens.solvers import get_solver


def run_table_2():
    """Reproduce Table 2: Solutions found by exhaustive enumeration (CaDiCaL 1.5.3)."""
    print("\n" + "=" * 80)
    print("Table 2: Solutions found by exhaustive enumeration (CaDiCaL 1.5.3)")
    print("=" * 80)

    n_values = [2, 3, 4, 5, 6, 7, 8, 9]
    oeis = {2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352}

    enc_list = [
        "pairwise", "binary", "sequential", "commander", "product",
        "pysat_pairwise", "pysat_seqcounter", "pysat_bitwise", "pysat_ladder"
    ]

    header = f"{'Encoding':<18} | " + " | ".join(f"{n:>5}" for n in n_values)
    print(header)
    print("-" * len(header))
    print(f"{'Known count (OEIS)':<18} | " + " | ".join(f"{oeis[n]:>5}" for n in n_values))
    print("-" * len(header))

    for enc_name in enc_list:
        counts = []
        for n in n_values:
            cnt, _ = count_all_solutions(n, encoding=enc_name, sat_solver_name="cadical153")
            counts.append(f"{cnt:>5}")
        print(f"{enc_name:<18} | " + " | ".join(counts))


def run_table_3():
    """Reproduce Table 3: CNF size (vars and clauses) across encodings for N=64, 256, 1024."""
    print("\n" + "=" * 80)
    print("Table 3: Variables and clauses by encoding for N=64, 256, 1024")
    print("=" * 80)
    tbl = verify_table_3_counts()
    print(f"{'Encoding':<12} | {'N=64 vars':>9} {'clauses':>10} | {'N=256 vars':>10} {'clauses':>12} | {'N=1024 vars':>11} {'clauses':>14}")
    print("-" * 80)
    for enc, vals in tbl.items():
        v64, c64 = vals[64]["vars"], vals[64]["clauses"]
        v256, c256 = vals[256]["vars"], vals[256]["clauses"]
        v1024, c1024 = vals[1024]["vars"], vals[1024]["clauses"]
        print(f"{enc:<12} | {v64:>9,d} {c64:>10,d} | {v256:>10,d} {c256:>12,d} | {v1024:>11,d} {c1024:>14,d}")


def run_table_4(sizes=None):
    """Reproduce Table 4: Time (s) by AMO encoding with CaDiCaL 1.5.3."""
    if sizes is None:
        sizes = [8, 16, 32, 64, 100, 128]
    print("\n" + "=" * 80)
    print(f"Table 4: Time (s) by AMO encoding with CaDiCaL 1.5.3 (sizes={sizes})")
    print("=" * 80)

    enc_list = ["pairwise", "binary", "sequential", "commander", "product"]
    header = f"{'N':>5} | " + " | ".join(f"{e:>12}" for e in enc_list)
    print(header)
    print("-" * len(header))

    for n in sizes:
        row = [f"{n:>5}"]
        for e in enc_list:
            solver = get_solver("sat", encoding=e, sat_solver_name="cadical153")
            res = solver.solve(n, timeout=30.0)
            if res.is_sat:
                row.append(f"{res.total_time:>11.2f}s")
            elif res.status == "TIMEOUT":
                row.append(f"{'TO':>12}")
            elif res.status == "MEMORY_OUT":
                row.append(f"{'MO':>12}")
            else:
                row.append(f"{res.status:>12}")
        print(" | ".join(row))


def run_table_7(sizes=None):
    """Reproduce Table 7: SAT vs CP vs ILP comparison."""
    if sizes is None:
        sizes = [8, 16, 24, 31, 32, 44, 64]
    print("\n" + "=" * 80)
    print(f"Table 7: Time (s) across paradigms (sizes={sizes})")
    print("=" * 80)

    solvers = ["sat", "cp_sat_int", "cp_sat_bool", "gurobi", "cplex_cp", "cplex_mip"]
    header = f"{'N':>5} | " + " | ".join(f"{s:>14}" for s in solvers)
    print(header)
    print("-" * len(header))

    for n in sizes:
        row = [f"{n:>5}"]
        for s_name in solvers:
            try:
                solver = get_solver(s_name)
                res = solver.solve(n, timeout=30.0)
                if res.is_sat:
                    row.append(f"{res.total_time:>13.3f}s")
                elif res.status == "LICENSE_LIMIT":
                    row.append(f"{'N/A':>14}")
                elif res.status == "TIMEOUT":
                    row.append(f"{'TO':>14}")
                elif res.status == "MEMORY_OUT":
                    row.append(f"{'MO':>14}")
                else:
                    row.append(f"{res.status:>14}")
            except Exception as e:
                row.append(f"{'ERR':>14}")
        print(" | ".join(row))


def main():
    parser = argparse.ArgumentParser(description="Reproduce experiment tables from paper")
    parser.add_argument("--table", type=str, choices=["2", "3", "4", "7", "all"], default="3",
                        help="Table number to reproduce (2: Counting, 3: CNF size, 4: Encodings, 7: Paradigms, all: Run all)")
    args = parser.parse_args()

    if args.table in ("2", "all"):
        run_table_2()
    if args.table in ("3", "all"):
        run_table_3()
    if args.table in ("4", "all"):
        run_table_4()
    if args.table in ("7", "all"):
        run_table_7()


if __name__ == "__main__":
    main()
