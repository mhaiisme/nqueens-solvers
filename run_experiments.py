"""Experiment runner script to reproduce the benchmark tables from the report."""
import argparse

from nqueens.analysis import count_all_solutions, verify_table_3_counts
from nqueens.solvers import get_solver


def run_table_7_counting():
    """Reproduce Table 7 (tab:count): Number of solutions found by exhaustive enumeration."""
    print("\n" + "=" * 80)
    print("Table 7 (tab:count): Number of solutions found by exhaustive enumeration (CaDiCaL 1.5.3)")
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


def run_table_8_size():
    """Reproduce Table 8 (tab:size): Number of variables and clauses per encoding."""
    print("\n" + "=" * 80)
    print("Table 8 (tab:size): Number of variables and clauses per encoding (N=64, 256, 1024)")
    print("=" * 80)
    tbl = verify_table_3_counts()
    print(f"{'Encoding':<12} | {'N=64 vars':>9} {'clauses':>10} | {'N=256 vars':>10} {'clauses':>12} | {'N=1024 vars':>11} {'clauses':>14}")
    print("-" * 80)
    for enc, vals in tbl.items():
        v64, c64 = vals[64]["vars"], vals[64]["clauses"]
        v256, c256 = vals[256]["vars"], vals[256]["clauses"]
        v1024, c1024 = vals[1024]["vars"], vals[1024]["clauses"]
        print(f"{enc:<12} | {v64:>9,d} {c64:>10,d} | {v256:>10,d} {c256:>12,d} | {v1024:>11,d} {c1024:>14,d}")


def run_table_9_encodings(sizes=None):
    """Reproduce Table 9 (tab:enc): Total time (s) per AMO encoding, CaDiCaL 1.5.3."""
    if sizes is None:
        sizes = [8, 16, 32, 64, 100, 128]
    print("\n" + "=" * 80)
    print(f"Table 9 (tab:enc): Total time (s) per AMO encoding, CaDiCaL 1.5.3 (sizes={sizes})")
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


def run_table_10_pysat(sizes=None):
    """Reproduce Table 10 (tab:pysat): Total time (s) for PySAT built-in AMO encodings."""
    if sizes is None:
        sizes = [64, 128, 256]
    print("\n" + "=" * 80)
    print(f"Table 10 (tab:pysat): Total time (s) for PySAT built-in AMO encodings (sizes={sizes})")
    print("=" * 80)

    enc_list = ["pysat_pairwise", "pysat_seqcounter", "pysat_bitwise", "pysat_ladder"]
    header = f"{'N':>5} | " + " | ".join(f"{e:>16}" for e in enc_list)
    print(header)
    print("-" * len(header))

    for n in sizes:
        row = [f"{n:>5}"]
        for e in enc_list:
            solver = get_solver("sat", encoding=e, sat_solver_name="cadical153")
            res = solver.solve(n, timeout=30.0)
            if res.is_sat:
                row.append(f"{res.total_time:>15.2f}s")
            elif res.status == "TIMEOUT":
                row.append(f"{'TO':>16}")
            elif res.status == "MEMORY_OUT":
                row.append(f"{'MO':>16}")
            else:
                row.append(f"{res.status:>16}")
        print(" | ".join(row))


def run_table_11_solvers(sizes=None):
    """Reproduce Table 11 (tab:solvers): Total time (s) per SAT solver and encoding."""
    if sizes is None:
        sizes = [128, 256]
    print("\n" + "=" * 80)
    print(f"Table 11 (tab:solvers): Total time (s) per SAT solver on Commander & Product (sizes={sizes})")
    print("=" * 80)

    sat_solvers = ["cadical153", "glucose4", "minisat22", "maplechrono"]
    for enc in ("commander", "product"):
        print(f"\n--- Encoding: {enc} ---")
        header = f"{'Solver':<16} | " + " | ".join(f"{n:>10}" for n in sizes)
        print(header)
        print("-" * len(header))
        for s_name in sat_solvers:
            row = [f"{s_name:<16}"]
            for n in sizes:
                try:
                    solver = get_solver("sat", encoding=enc, sat_solver_name=s_name)
                    res = solver.solve(n, timeout=30.0)
                    if res.is_sat:
                        row.append(f"{res.total_time:>9.2f}s")
                    elif res.status == "TIMEOUT":
                        row.append(f"{'TO':>10}")
                    else:
                        row.append(f"{res.status:>10}")
                except Exception:
                    row.append(f"{'N/A':>10}")
            print(" | ".join(row))


def run_table_12_paradigms(sizes=None):
    """Reproduce Table 12 (tab:cmp): SAT vs CP vs ILP comparison."""
    if sizes is None:
        sizes = [8, 16, 24, 31, 32, 44, 64]
    print("\n" + "=" * 80)
    print(f"Table 12 (tab:cmp): Total time (s) of SAT, CP and ILP solvers (sizes={sizes})")
    print("=" * 80)

    solvers = ["sat", "cp_sat_int", "cp_sat_bool", "gurobi", "cplex_cp", "cplex_mip"]
    header = f"{'N':>5} | " + " | ".join(f"{s:>14}" for s in solvers)
    print(header)
    print("-" * len(header))

    for n in sizes:
        row = [f"{n:>5}"]
        for s_name in solvers:
            try:
                if s_name == "sat":
                    solver = get_solver("sat", encoding="commander", sat_solver_name="minisat22")
                else:
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
            except Exception:
                row.append(f"{'ERR':>14}")
        print(" | ".join(row))


def main():
    parser = argparse.ArgumentParser(description="Reproduce experiment tables from the paper")
    parser.add_argument(
        "--table",
        type=str,
        choices=[
            "7", "8", "9", "10", "11", "12",
            "counting", "size", "encodings", "pysat", "solvers", "paradigms",
            "2", "3", "4", "all"
        ],
        default="8",
        help=(
            "Table to reproduce: "
            "7/counting (OEIS solution counting), "
            "8/size (CNF size), "
            "9/encodings (AMO encoding times), "
            "10/pysat (PySAT built-in encodings), "
            "11/solvers (CDCL solvers comparison), "
            "12/paradigms (SAT vs CP vs ILP), "
            "all (Run all)"
        ),
    )
    args = parser.parse_args()

    if args.table in ("7", "2", "counting", "all"):
        run_table_7_counting()
    if args.table in ("8", "3", "size", "all"):
        run_table_8_size()
    if args.table in ("9", "4", "encodings", "all"):
        run_table_9_encodings()
    if args.table in ("10", "pysat", "all"):
        run_table_10_pysat()
    if args.table in ("11", "solvers", "all"):
        run_table_11_solvers()
    if args.table in ("12", "paradigms", "all"):
        run_table_12_paradigms()


if __name__ == "__main__":
    main()
