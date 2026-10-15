"""Illustrative (conceptual) figures for the report."""
import itertools
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams.update({"font.family": "serif", "font.size": 9})

LIGHT, DARK = "#f0d9b5", "#b58863"


def draw_board(ax, n, highlight=None):
    for i in range(n):
        for j in range(n):
            ax.add_patch(Rectangle((j, n - 1 - i), 1, 1,
                                   color=LIGHT if (i + j) % 2 == 0 else DARK))
    if highlight:
        for (i, j), c in highlight.items():
            ax.add_patch(Rectangle((j, n - 1 - i), 1, 1, color=c, alpha=0.75))
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.set_xticks([k + 0.5 for k in range(n)])
    ax.set_xticklabels(range(n), fontsize=7)
    ax.set_yticks([k + 0.5 for k in range(n)])
    ax.set_yticklabels(reversed(range(n)), fontsize=7)
    ax.tick_params(length=0)
    ax.set_xlabel("column $j$")
    ax.set_ylabel("row $i$")


def queen(ax, n, i, j, color="black"):
    ax.text(j + 0.5, n - 1 - i + 0.47, "\u265B", ha="center", va="center",
            fontsize=15, color=color, fontfamily="DejaVu Sans")


# ------------------------------------------------------------- Fig: board + lines
N = 8
sol = [0, 4, 7, 5, 2, 6, 1, 3]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.4))
draw_board(axes[0], N)
for i, j in enumerate(sol):
    queen(axes[0], N, i, j)
axes[0].set_title("(a) A solution for $N=8$")

ci, cj = 3, 2
hl = {}
for k in range(N):
    hl[(ci, k)] = "#4c72b0"          # row
    hl[(k, cj)] = "#55a868"          # column
for i in range(N):
    for j in range(N):
        if (i, j) == (ci, cj):
            continue
        if i - j == ci - cj:
            hl[(i, j)] = "#c44e52"   # diagonal
        elif i + j == ci + cj:
            hl[(i, j)] = "#8172b2"   # anti-diagonal
draw_board(axes[1], N, hl)
queen(axes[1], N, ci, cj, "white")
axes[1].set_title("(b) The 4 lines through cell $(3,2)$")
handles = [Rectangle((0, 0), 1, 1, color=c, alpha=0.75) for c in
           ["#4c72b0", "#55a868", "#c44e52", "#8172b2"]]
axes[1].legend(handles, ["row: exactly one", "column: exactly one",
                         "diagonal $i-j$: at most one",
                         "anti-diagonal $i+j$: at most one"],
               loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=7.5,
               frameon=False)
fig.tight_layout()
fig.savefig("figures/board.pdf", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------- Fig: pipeline
fig, ax = plt.subplots(figsize=(8.0, 3.2))
ax.set_xlim(-2, 102)
ax.set_ylim(0, 42)
ax.axis("off")


def box(x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                fc=fc, ec="black", lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7)


def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=0.9))


box(0, 17, 11, 8, "Input:\nboard size $N$", "#eeeeee")
rows = [
    (31, "SAT model\n$N^2$ Boolean vars\nALO + AMO encoding", "#dbe9f6",
     "8 CDCL solvers\n(CaDiCaL, Glucose,\nKissat, MiniSat, ...)"),
    (17, "CP model\n$N$ integer vars\n3 x AllDifferent", "#e2f0d9",
     "CP-SAT\nCPLEX CP Optimizer"),
    (3, "ILP model\n$N^2$ binary vars\nlinear (in)equalities", "#fbe5d6",
     "Gurobi\nCPLEX MIP"),
]
for y, model, fc, solver in rows:
    box(17, y, 22, 8, model, fc)
    box(45, y, 22, 8, solver, fc)
    arrow(11.5, 21, 16.5, y + 4)
    arrow(39.5, y + 4, 44.5, y + 4)
    arrow(67.5, y + 4, 73.5, 21)
box(74, 17, 12, 8, "Independent\nvalidator", "#fff2cc")
box(90, 17, 10, 8, "Result:\ntime / TO / MO", "#eeeeee")
arrow(86.5, 21, 89.5, 21)
for x, t in [(28, "Modelling"), (56, "Solving"), (80, "Checking")]:
    ax.text(x, 41, t, ha="center", fontsize=8.5, style="italic")
fig.savefig("figures/pipeline.pdf", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------- Fig: AMO encodings
fig, axes = plt.subplots(2, 2, figsize=(6.4, 5.6))
axes = axes.ravel()
for ax in axes:
    ax.axis("off")
    ax.set_aspect("equal")

# (a) pairwise on 6 vars: complete graph
ax = axes[0]
m = 6
pts = [(math.cos(2 * math.pi * k / m + math.pi / 2),
        math.sin(2 * math.pi * k / m + math.pi / 2)) for k in range(m)]
for a, b in itertools.combinations(range(m), 2):
    ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color="#c44e52",
            lw=0.7)
for k, (x, y) in enumerate(pts):
    ax.add_patch(plt.Circle((x, y), 0.2, fc="#dbe9f6", ec="black", lw=0.7, zorder=3))
    ax.text(x, y, f"$x_{k + 1}$", ha="center", va="center", fontsize=8, zorder=4)
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
ax.set_title("(a) Pairwise\n15 clauses $\\neg x_i\\vee\\neg x_j$", fontsize=9)

# (b) sequential counter chain
ax = axes[1]
m = 5
for k in range(m):
    ax.add_patch(plt.Circle((k, 1), 0.28, fc="#dbe9f6", ec="black", lw=0.7))
    ax.text(k, 1, f"$x_{k + 1}$", ha="center", va="center", fontsize=7)
    if k < m - 1:
        ax.add_patch(Rectangle((k - 0.25, -0.25), 0.5, 0.5, fc="#fff2cc",
                               ec="black", lw=0.7))
        ax.text(k, 0, f"$s_{k + 1}$", ha="center", va="center", fontsize=7)
        ax.annotate("", xy=(k, 0.27), xytext=(k, 0.72),
                    arrowprops=dict(arrowstyle="->", lw=0.6))
        if k < m - 2:
            ax.annotate("", xy=(k + 0.75, 0), xytext=(k + 0.25, 0),
                        arrowprops=dict(arrowstyle="->", lw=0.6))
ax.annotate("", xy=(m - 1 - 0.2, 0.8), xytext=(m - 2 + 0.25, 0.1),
            arrowprops=dict(arrowstyle="-[", lw=0.6, ls="--", color="#c44e52"))
ax.text(m - 1.1, 0.3, "$\\neg x_5$", fontsize=7, color="#c44e52")
ax.set_xlim(-0.6, m - 0.4)
ax.set_ylim(-1.6, 2.2)
ax.text((m - 1) / 2, -0.95, "$s_i$ = \"some $x_1..x_i$ is true\"",
        ha="center", fontsize=7)
ax.set_title("(b) Sequential counter\nchain of $m-1$ counters", fontsize=9)

# (c) commander, groups of 3
ax = axes[2]
for g in range(3):
    cx = g * 1.6
    ax.add_patch(Rectangle((cx - 0.65, -0.35), 1.3, 0.7, fill=False,
                           ls="--", lw=0.6))
    for t in range(3):
        x = cx - 0.42 + 0.42 * t
        ax.add_patch(plt.Circle((x, 0), 0.17, fc="#dbe9f6", ec="black",
                                lw=0.6))
        ax.text(x, 0, f"{3 * g + t + 1}", ha="center", va="center",
                fontsize=6)
        ax.plot([x, cx], [0.17, 0.95], color="gray", lw=0.5)
    ax.add_patch(plt.Circle((cx, 1.15), 0.22, fc="#e2f0d9", ec="black",
                            lw=0.7))
    ax.text(cx, 1.15, f"$c_{g + 1}$", ha="center", va="center", fontsize=7)
ax.text(1.6, 1.85, "AMO($c_1,c_2,c_3$)", ha="center", fontsize=7)
ax.text(1.6, -0.85, "pairwise AMO inside each group", ha="center",
        fontsize=7)
ax.set_xlim(-0.9, 4.1)
ax.set_ylim(-1.4, 2.4)
ax.set_title("(c) Commander ($k=3$)", fontsize=9)

# (d) product 3x3
ax = axes[3]
for u in range(3):
    for v in range(3):
        ax.add_patch(plt.Circle((v, 2 - u), 0.22, fc="#dbe9f6", ec="black",
                                lw=0.6, zorder=2))
        ax.text(v, 2 - u, f"$x_{3 * u + v + 1}$", ha="center", va="center",
                fontsize=7, zorder=3)
    ax.add_patch(Rectangle((-1.15, 2 - u - 0.2), 0.4, 0.4, fc="#fbe5d6",
                           ec="black", lw=0.6))
    ax.text(-0.95, 2 - u, f"$r_{u + 1}$", ha="center", va="center",
            fontsize=7)
    ax.plot([-0.75, 1.78], [2 - u, 2 - u], color="#e8a07a", lw=0.6, zorder=0)
for v in range(3):
    ax.add_patch(Rectangle((v - 0.2, -1.15), 0.4, 0.4, fc="#e2f0d9",
                           ec="black", lw=0.6))
    ax.text(v, -0.95, f"$c_{v + 1}$", ha="center", va="center", fontsize=7)
    ax.plot([v, v], [-0.75, 2.22], color="#7fbf7f", lw=0.6, zorder=0)
ax.set_xlim(-1.5, 2.6)
ax.set_ylim(-1.6, 2.7)
ax.set_title("(d) Product ($3\\times3$ grid)\n$x_i\\rightarrow r_u,\\ x_i\\rightarrow c_v$",
             fontsize=9)
fig.tight_layout()
fig.savefig("figures/amo_encodings.pdf", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------- Fig: status map (Table 6)
enc = ["pairwise", "binary", "sequential", "commander", "product"]
Ns = [8, 16, 32, 64, 100, 128, 200, 256, 400, 512, 800, 1024]
data = {
    "pairwise": [0.10, 0.16, 0.95, 2.09, 5.46, 7.91, 17.40, "MO", "MO", "MO", "MO", "MO"],
    "binary": [0.08, 0.15, 0.47, 3.93, 2.18, 1.19, 3.82, 5.82, 13.27, 24.06, "MO", "MO"],
    "sequential": [0.13, 0.25, 0.44, 5.75, 4.22, 8.82, 19.09, "TO", "TO", "TO", "TO", "MO"],
    "commander": [0.12, 0.15, 0.20, 0.20, 0.58, 0.41, 2.66, 1.87, 7.47, 11.36, "TO", "TO"],
    "product": [0.09, 0.14, 0.44, 0.94, 2.91, 1.38, 1.97, 3.54, "TO", 23.90, "TO", "TO"],
}
code = {"fast": 0, "mid": 1, "slow": 2, "TO": 3, "MO": 4}
cmap = ListedColormap(["#a1d99b", "#ffeda0", "#fdae6b", "#bdbdbd", "#636363"])
grid, labels = [], []
for e in enc:
    row, lab = [], []
    for v in data[e]:
        if isinstance(v, str):
            row.append(code[v]); lab.append(v)
        else:
            row.append(code["fast"] if v < 1 else code["mid"] if v < 10 else code["slow"])
            lab.append(f"{v:.2f}")
    grid.append(row); labels.append(lab)
fig, ax = plt.subplots(figsize=(7.0, 2.2))
ax.imshow(grid, cmap=cmap, vmin=0, vmax=4, aspect="auto")
for r in range(len(enc)):
    for c in range(len(Ns)):
        ax.text(c, r, labels[r][c], ha="center", va="center", fontsize=7,
                color="white" if grid[r][c] == 4 else "black")
ax.set_xticks(range(len(Ns)))
ax.set_xticklabels(Ns)
ax.set_yticks(range(len(enc)))
ax.set_yticklabels(enc)
ax.set_xlabel("N")
ax.set_xticks([x - 0.5 for x in range(len(Ns) + 1)], minor=True)
ax.set_yticks([y - 0.5 for y in range(len(enc) + 1)], minor=True)
ax.grid(which="minor", color="white", lw=1.5)
ax.tick_params(which="minor", length=0)
handles = [Rectangle((0, 0), 1, 1, color=cmap(k)) for k in range(5)]
ax.legend(handles, ["< 1 s", "1-10 s", "10-30 s", "time-out", "memory-out"],
          loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=5,
          fontsize=7.5, frameon=False)
fig.tight_layout()
fig.savefig("figures/status_map.pdf", bbox_inches="tight")
plt.close(fig)
print("illustrations written")
