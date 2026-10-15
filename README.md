# Solving the N-Queens Problem: SAT, CP, and ILP

A comparative framework for solving the N-Queens problem across three exact combinatorial paradigms:
1. **Propositional Satisfiability (SAT)**: CDCL solvers with 5 hand-crafted At-Most-One (AMO) encodings and 4 PySAT built-in cardinality encodings.
2. **Constraint Programming (CP)**: Google OR-Tools CP-SAT (Integer and Boolean models) and IBM CPLEX CP Optimizer (`AllDifferent`).
3. **Integer Linear Programming (ILP/MIP)**: Gurobi MIP and IBM CPLEX MIP (0/1 binary decision variables).

---

## 📌 Repository Structure

```
nqueens-solvers/
├── README.md                      # Documentation, usage guide, theoretical background
├── pyproject.toml                 # Package setup and build specification
├── requirements.txt               # Direct pip requirements
├── cli.py                         # Unified Command-Line Interface (CLI)
├── run_experiments.py             # Script to reproduce the paper's benchmark tables
├── nqueens/
│   ├── board.py                   # N-Queens geometry, lines generator, cell/var mapping
│   ├── validator.py               # Independent solution validator (no-attack checker)
│   ├── encodings/                 # At-Most-One (AMO) & At-Least-One (ALO) encodings
│   │   ├── base.py                # Base encoder and streaming clause consumer interface
│   │   ├── pairwise.py            # Binomial pairwise encoding: O(m^2) clauses, 0 aux vars
│   │   ├── binary.py              # Bitwise encoding: O(m log m) clauses, ceil(log2 m) aux vars
│   │   ├── seq_counter.py         # Sequential counter (Sinz): 3m-4 clauses, m-1 aux vars
│   │   ├── commander.py           # Commander encoding (k=3): ~3.5m clauses, ~m/2 aux vars
│   │   ├── product.py             # 2-Product grid encoding (Chen): ~2m clauses, ~2 sqrt(m) aux vars
│   │   └── pysat_enc.py           # PySAT CardEnc (pairwise, seqcounter, bitwise, ladder)
│   ├── solvers/                   # Solvers across the 3 paradigms
│   │   ├── base.py                # Base solver interface and standardized SolverResult
│   │   ├── sat_solver.py          # PySAT CDCL runner (CaDiCaL, Glucose, MiniSat, Kissat, etc.)
│   │   ├── cp_sat.py              # OR-Tools CP-SAT (Integer AllDifferent & Boolean models)
│   │   ├── gurobi_mip.py          # Gurobi MIP 0/1 binary formulation with license ceiling check
│   │   ├── cplex_cp.py            # IBM CP Optimizer AllDifferent model via docplex.cp
│   │   └── cplex_mip.py           # IBM CPLEX MIP 0/1 binary formulation via docplex.mp
│   └── analysis/
│       ├── counter.py             # Exhaustive solution counter (OEIS A000170 verification)
│       └── formula_stats.py       # Closed-form theoretical vs measured CNF size analysis
└── tests/
    ├── test_validator.py          # Validator unit tests (valid, row/col/diag conflicts)
    ├── test_encodings.py          # Correctness tests for all 9 AMO encodings
    ├── test_solvers.py            # End-to-end solving tests across SAT, CP, ILP
    └── test_counting.py           # Exhaustive counting tests for N=2..5
```

---

## 🚀 Installation & Quickstart

### 1. Prerequisites
- Python 3.9+
- Optional: IBM CPLEX Optimization Studio (for `cplex_cp` and `cplex_mip`)

### 2. Install Dependencies

Using `pip`:
```bash
pip install -r requirements.txt
```

Or using `uv` (recommended):
```bash
uv pip install -r requirements.txt
```

---

## 💻 CLI Usage

The project provides an intuitive CLI via `cli.py`:

### 1. Solve N-Queens
Solve for board size $N=8$ using the best SAT configuration (commander + CaDiCaL):
```bash
python cli.py solve -n 8 --solver sat --encoding commander --sat-solver cadical153 --print-board
```

Solve with Google OR-Tools CP-SAT (Integer `AllDifferent` formulation):
```bash
python cli.py solve -n 8 --solver cp_sat_int --print-board
```

Solve with Gurobi MIP:
```bash
python cli.py solve -n 8 --solver gurobi --print-board
```

### 2. Verify Encodings Against OEIS A000170
Exhaustively count all solutions for $N=2..9$ and verify against OEIS:
```bash
python cli.py verify-oeis
```

### 3. Verify Closed-Form CNF Formulas (Table 3)
Check theoretical formulas against actual measured sizes on $N=64, 256, 1024$:
```bash
python cli.py verify-formulas
```

### 4. Benchmark Multiple Solvers
Compare execution times across solvers on multiple board sizes:
```bash
python cli.py benchmark --solvers sat cp_sat_int gurobi --sizes 8 16 24 32 44
```

---

## 📊 Reproducing the Paper Tables

To reproduce the exact benchmark tables from the research report, run:

```bash
# Table 2: Exhaustive solution counting for N=2..9 across all 9 encodings
python run_experiments.py --table 2

# Table 3: CNF size (vars and clauses) across encodings for N=64, 256, 1024
python run_experiments.py --table 3

# Table 4: Solving time across AMO encodings on CaDiCaL 1.5.3
python run_experiments.py --table 4

# Table 7: Comparative benchmark across SAT, CP, and ILP paradigms
python run_experiments.py --table 7
```

---

## 🧪 Running the Test Suite

Run the complete test suite with `pytest`:
```bash
pytest -v
```
All 26 unit tests cover:
- Correctness of all 9 AMO encodings on all $2^m$ assignments.
- Independent solution validator on conflict cases.
- Solving across SAT, CP-SAT, and Gurobi.
- Exhaustive counting against OEIS A000170.

---

## 🔬 Mathematical Formulations

### 1. SAT Formulations
Given $N^2$ Boolean variables $x_{ij}$ ($1 \le i, j \le N$):
- **Rows**: $\bigvee_{j=1}^N x_{ij} \wedge \text{AMO}(x_{i1}, \dots, x_{iN}), \quad \forall i$
- **Columns**: $\bigvee_{i=1}^N x_{ij} \wedge \text{AMO}(x_{1j}, \dots, x_{Nj}), \quad \forall j$
- **Diagonals**: $\text{AMO}(\{x_{ij} \mid i - j = d\}), \quad \forall d \in [-(N-1), N-1]$ with length $\ge 2$
- **Anti-diagonals**: $\text{AMO}(\{x_{ij} \mid i + j = s\}), \quad \forall s \in [0, 2N-2]$ with length $\ge 2$

### 2. Constraint Programming Formulations
- **Integer Model (`CP-SAT int` / `CPLEX CP`)**:
  - $N$ variables $q_i \in \{0, \dots, N-1\}$ (column of queen in row $i$).
  - $\text{AllDifferent}(q_0, \dots, q_{N-1})$
  - $\text{AllDifferent}(q_0 + 0, \dots, q_{N-1} + N - 1)$
  - $\text{AllDifferent}(q_0 - 0, \dots, q_{N-1} - (N - 1))$

### 3. Integer Linear Programming Formulations
- **MIP Model (`Gurobi` / `CPLEX MIP`)**:
  - Binary variables $x_{ij} \in \{0, 1\}$.
  - $\sum_{j=1}^N x_{ij} = 1, \quad \forall i$
  - $\sum_{i=1}^N x_{ij} = 1, \quad \forall j$
  - $\sum_{(i,j) \in D} x_{ij} \le 1, \quad \forall \text{ diagonal } D \text{ with } |D| \ge 2$
