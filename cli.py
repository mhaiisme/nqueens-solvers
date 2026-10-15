"""Command-Line Interface (CLI) for N-Queens Solvers and Benchmarking."""
import argparse
import sys
import time

from nqueens.board import format_board
from nqueens.encodings import list_available_encodings
from nqueens.solvers import get_solver
from nqueens.analysis import (
    count_all_solutions,
    verify_against_oeis,
    verify_table_3_counts,
    pairwise_clauses_closed_form,
    sequential_clauses_closed_form,
    sequential_aux_vars_closed_form,
)


def cmd_solve(args):
    """Solve N-Queens for a specific size and solver."""
    kwargs = {}
    if args.solver == "sat":
        kwargs["encoding"] = args.encoding
        kwargs["sat_solver_name"] = args.sat_solver

    solver = get_solver(args.solver, **kwargs)
    print(f"Solving N={args.n} with solver '{solver.name}' (timeout={args.timeout}s)...")

    res = solver.solve(args.n, timeout=args.timeout)
    print(res.summary())

    if res.is_sat:
        print(f"Model time: {res.model_time:.4f}s | Solve time: {res.solve_time:.4f}s | Total: {res.total_time:.4f}s")
        print(f"Variables: {res.num_vars} | Constraints/Clauses: {res.num_constraints}")
        if args.print_board and args.n <= 32:
            print("\nSolution Board:")
            print(format_board(args.n, res.queens))
        elif args.print_board:
            print("\n(Board printing suppressed for N > 32)")
        print(f"Queens (row, col): {res.queens[:10]}{' ...' if len(res.queens) > 10 else ''}")
    else:
        print(f"Result: {res.status} ({res.error_message or 'No solution'})")


def cmd_count(args):
    """Count all solutions for N and compare with OEIS A000170."""
    print(f"Exhaustively counting all solutions for N={args.n} using '{args.encoding}' + '{args.sat_solver}'...")
    t0 = time.perf_counter()
    count, _ = count_all_solutions(args.n, encoding=args.encoding, sat_solver_name=args.sat_solver)
    dt = time.perf_counter() - t0
    print(f"Found {count} solutions in {dt:.2f}s.")


def cmd_verify_oeis(args):
    """Verify that solution counts match OEIS A000170 for N=2..9."""
    print("Verifying solution enumeration against OEIS A000170 (N=2..9)...")
    res = verify_against_oeis(encoding=args.encoding, sat_solver_name=args.sat_solver)
    print(f"{'N':>3} | {'Found':>7} | {'Expected':>8} | Status")
    print("-" * 32)
    all_ok = True
    for n, d in sorted(res.items()):
        status = "PASSED" if d["correct"] else "FAILED"
        if not d["correct"]:
            all_ok = False
        print(f"{n:>3} | {d['found']:>7} | {d['expected']:>8} | {status}")
    if all_ok:
        print("\nAll solution counts match OEIS A000170 perfectly!")
    else:
        print("\nVerification FAILED on some instances.")
        sys.exit(1)


def cmd_verify_formulas(args):
    """Verify closed-form formulas vs measured CNF size."""
    print("Checking closed-form formulas vs implementation...")
    for n in (8, 64):
        pw_c = pairwise_clauses_closed_form(n)
        sq_c = sequential_clauses_closed_form(n)
        sq_v = n * n + sequential_aux_vars_closed_form(n)
        print(f"N={n:2d}: Pairwise clauses formula = {pw_c:,}")
        print(f"N={n:2d}: Sequential total clauses formula = {sq_c:,} | total vars formula = {sq_v:,}")

    print("\nMeasuring CNF sizes across encodings (Table 3 in report):")
    tbl = verify_table_3_counts()
    print(f"{'Encoding':<12} | {'N=64 vars':>9} {'clauses':>10} | {'N=256 vars':>10} {'clauses':>12} | {'N=1024 vars':>11} {'clauses':>14}")
    print("-" * 80)
    for enc, vals in tbl.items():
        v64, c64 = vals[64]["vars"], vals[64]["clauses"]
        v256, c256 = vals[256]["vars"], vals[256]["clauses"]
        v1024, c1024 = vals[1024]["vars"], vals[1024]["clauses"]
        print(f"{enc:<12} | {v64:>9,d} {c64:>10,d} | {v256:>10,d} {c256:>12,d} | {v1024:>11,d} {c1024:>14,d}")


def cmd_benchmark(args):
    """Run benchmark over a set of solvers and sizes."""
    print(f"Running benchmark across solvers: {args.solvers}")
    print(f"Board sizes: {args.sizes}")
    print(f"Timeout: {args.timeout}s per run\n")

    header = f"{'N':>5} | " + " | ".join(f"{s:>18}" for s in args.solvers)
    print(header)
    print("-" * len(header))

    for n in args.sizes:
        row = [f"{n:>5}"]
        for s_name in args.solvers:
            solver = get_solver(s_name)
            res = solver.solve(n, timeout=args.timeout)
            if res.is_sat:
                val = f"{res.total_time:.3f}s"
            elif res.status == "TIMEOUT":
                val = "TO (>30s)"
            elif res.status == "LICENSE_LIMIT":
                val = "N/A (licence)"
            elif res.status == "MEMORY_OUT":
                val = "MO"
            else:
                val = res.status
            row.append(f"{val:>18}")
        print(" | ".join(row))


def main():
    parser = argparse.ArgumentParser(description="N-Queens Solver & Benchmark CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. solve
    p_solve = subparsers.add_parser("solve", help="Solve N-Queens for a specific N")
    p_solve.add_argument("-n", type=int, required=True, help="Board size")
    p_solve.add_argument("--solver", type=str, default="sat", help="Solver name (sat, cp_sat_int, cp_sat_bool, gurobi, cplex_cp, cplex_mip)")
    p_solve.add_argument("--encoding", type=str, default="commander", choices=list_available_encodings(), help="SAT AMO encoding")
    p_solve.add_argument("--sat-solver", type=str, default="cadical153", help="PySAT CDCL solver name")
    p_solve.add_argument("--timeout", type=float, default=30.0, help="Wall-clock timeout in seconds")
    p_solve.add_argument("--print-board", action="store_true", help="Print ASCII solution board")
    p_solve.set_defaults(func=cmd_solve)

    # 2. count
    p_count = subparsers.add_parser("count", help="Exhaustively count all solutions for N")
    p_count.add_argument("-n", type=int, required=True, help="Board size")
    p_count.add_argument("--encoding", type=str, default="pairwise", choices=list_available_encodings())
    p_count.add_argument("--sat-solver", type=str, default="cadical153")
    p_count.set_defaults(func=cmd_count)

    # 3. verify-oeis
    p_oeis = subparsers.add_parser("verify-oeis", help="Verify solution counts against OEIS A000170")
    p_oeis.add_argument("--encoding", type=str, default="pairwise", choices=list_available_encodings())
    p_oeis.add_argument("--sat-solver", type=str, default="cadical153")
    p_oeis.set_defaults(func=cmd_verify_oeis)

    # 4. verify-formulas
    p_form = subparsers.add_parser("verify-formulas", help="Verify closed-form formulas vs measured CNF size")
    p_form.set_defaults(func=cmd_verify_formulas)

    # 5. benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run benchmark across multiple solvers")
    p_bench.add_argument("--solvers", nargs="+", default=["sat", "cp_sat_int", "gurobi"], help="List of solvers to test")
    p_bench.add_argument("--sizes", nargs="+", type=int, default=[8, 16, 24, 32, 44, 64], help="Board sizes N to test")
    p_bench.add_argument("--timeout", type=float, default=30.0, help="Timeout in seconds")
    p_bench.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
