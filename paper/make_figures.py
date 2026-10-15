"""Regenerate report figures from the measured values in the report tables.

All numbers below are copied verbatim from the original experimental report.
None = failed run (TO / MO / N/A) and is omitted from the plot.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "legend.fontsize": 8,
    "figure.dpi": 150,
})

ENC_STYLE = {
    "pairwise": ("o", "-"),
    "binary": ("s", "-"),
    "sequential": ("^", "-"),
    "commander": ("D", "-"),
    "product": ("v", "-"),
}

# ---------------------------------------------------------------- Figure 1: CNF size (Table 3)
size_N = [64, 256, 1024]
clauses = {
    "pairwise": [428_864, 27_831_552, 1_787_474_944],
    "binary": [95_576, 2_053_464, 41_243_992],
    "sequential": [47_756, 780_812, 12_560_396],
    "commander": [54_918, 907_754, 14_645_478],
    "product": [45_620, 631_720, 9_324_048],
}
variables = {
    "pairwise": [4_096, 65_536, 1_048_576],
    "binary": [6_136, 76_788, 1_105_904],
    "sequential": [20_098, 326_146, 5_236_738],
    "commander": [11_906, 195_214, 3_142_708],
    "product": [12_476, 125_800, 1_578_860],
}
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
for name, (m, ls) in ENC_STYLE.items():
    axes[0].loglog(size_N, clauses[name], marker=m, ls=ls, label=name)
    axes[1].loglog(size_N, variables[name], marker=m, ls=ls, label=name)
axes[0].set_title("(a) Number of clauses")
axes[1].set_title("(b) Number of variables")
for ax in axes:
    ax.set_xlabel("N")
    ax.set_xticks(size_N)
    ax.set_xticklabels([str(n) for n in size_N])
axes[0].legend(loc="upper left")
fig.tight_layout()
fig.savefig("figures/cnf_size.pdf")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2: time by encoding (Table 4)
enc_N = [8, 16, 32, 64, 100, 128, 200, 256, 400, 512, 800, 1024]
enc_time = {
    "pairwise": [0.10, 0.16, 0.95, 2.09, 5.46, 7.91, 17.40, None, None, None, None, None],
    "binary": [0.08, 0.15, 0.47, 3.93, 2.18, 1.19, 3.82, 5.82, 13.27, 24.06, None, None],
    "sequential": [0.13, 0.25, 0.44, 5.75, 4.22, 8.82, 19.09, None, None, None, None, None],
    "commander": [0.12, 0.15, 0.20, 0.20, 0.58, 0.41, 2.66, 1.87, 7.47, 11.36, None, None],
    "product": [0.09, 0.14, 0.44, 0.94, 2.91, 1.38, 1.97, 3.54, None, 23.90, None, None],
}
fig, ax = plt.subplots(figsize=(5.0, 3.0))
for name, (m, ls) in ENC_STYLE.items():
    xs = [n for n, t in zip(enc_N, enc_time[name]) if t is not None]
    ys = [t for t in enc_time[name] if t is not None]
    ax.loglog(xs, ys, marker=m, ls=ls, label=name)
ax.axhline(30, color="red", ls="--", lw=1)
ax.text(9, 33, "30 s time limit", color="red", fontsize=8)
ax.set_xlabel("N")
ax.set_ylabel("Total time (s)")
ax.set_ylim(0.05, 60)
ax.legend(loc="lower right", ncol=2)
fig.tight_layout()
fig.savefig("figures/time_encoding.pdf")
plt.close(fig)

# ---------------------------------------------------------------- Figure 3: SAT vs CP vs ILP (Table 7)
cmp_N = [8, 16, 24, 31, 32, 44, 64, 100, 128, 200, 256, 512, 1000]
cmp_time = {
    "SAT (commander + MiniSat)": [0.03, 0.02, 0.03, 0.06, 0.04, 0.05, 0.10, 0.18, 0.31, 0.72, 1.10, 6.60, 27.69],
    "CP-SAT (int)": [0.18, 0.02, 0.03, 0.06, 0.06, 0.12, 0.30, 1.03, 1.97, 16.11, None, None, None],
    "CP-SAT (bool)": [0.01, 0.01, 0.03, 0.05, 0.05, 0.10, 0.28, 0.81, 1.78, 2.47, 3.54, None, None],
    "CPLEX CP": [1.31, 0.01, 0.01, 0.01, 0.01, 0.02, 0.01, 0.01, 0.02, None, None, None, None],
    "Gurobi (MIP)": [0.33, 0.005, 0.04, 0.01, 0.02, 0.01, None, None, None, None, None, None, None],
    "CPLEX MIP": [0.43, 0.01, 0.01, 0.01, None, None, None, None, None, None, None, None, None],
}
markers = ["D", "o", "s", "^", "v", "P"]
fig, ax = plt.subplots(figsize=(5.0, 3.0))
for (name, ts), m in zip(cmp_time.items(), markers):
    xs = [n for n, t in zip(cmp_N, ts) if t is not None]
    ys = [t for t in ts if t is not None]
    ax.loglog(xs, ys, marker=m, label=name)
ax.axhline(30, color="red", ls="--", lw=1)
ax.set_xlabel("N")
ax.set_ylabel("Total time (s)")
ax.legend(loc="upper left", fontsize=7)
fig.tight_layout()
fig.savefig("figures/time_paradigms.pdf")
plt.close(fig)

print("figures written")
