"""Worked example of CDCL on 4-Queens (pairwise encoding)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "serif", "font.size": 9})
N = 4
LIGHT, DARK = "#f0d9b5", "#b58863"


def attacked(queens):
    out = set()
    for qi, qj in queens:
        for i in range(N):
            for j in range(N):
                if (i, j) != (qi, qj) and (
                        i == qi or j == qj or i - j == qi - qj or i + j == qi + qj):
                    out.add((i, j))
    return out


def panel(ax, decided, forced, conflict_row, title, note):
    att = attacked(decided + forced)
    for i in range(N):
        for j in range(N):
            ax.add_patch(Rectangle((j, N - 1 - i), 1, 1,
                                   color=LIGHT if (i + j) % 2 == 0 else DARK))
            if (i, j) in att:
                ax.add_patch(Rectangle((j, N - 1 - i), 1, 1, color="#777777",
                                       alpha=0.55))
                ax.text(j + 0.5, N - 1 - i + 0.5, "\u00d7", ha="center",
                        va="center", fontsize=12, color="white")
    if conflict_row is not None:
        ax.add_patch(Rectangle((0, N - 1 - conflict_row), N, 1, fill=False,
                               ec="red", lw=2.2))
        ax.text(N + 0.1, N - 1 - conflict_row + 0.5, "conflict", color="red",
                va="center", fontsize=8)
    for (i, j) in decided:
        ax.text(j + 0.5, N - 1 - i + 0.47, "\u265B", ha="center",
                va="center", fontsize=17, color="black",
                fontfamily="DejaVu Sans")
    for (i, j) in forced:
        ax.text(j + 0.5, N - 1 - i + 0.47, "\u265B", ha="center",
                va="center", fontsize=17, color="#1f5fbf",
                fontfamily="DejaVu Sans")
    ax.set_xlim(0, N)
    ax.set_ylim(0, N)
    ax.set_aspect("equal")
    ax.set_xticks([k + 0.5 for k in range(N)])
    ax.set_xticklabels(range(N), fontsize=7)
    ax.set_yticks([k + 0.5 for k in range(N)])
    ax.set_yticklabels(reversed(range(N)), fontsize=7)
    ax.tick_params(length=0)
    ax.set_title(title, fontsize=8.5)
    ax.text(N / 2, -0.75, note, ha="center", va="top", fontsize=7.5)


fig, axes = plt.subplots(1, 4, figsize=(7.4, 2.9))
panel(axes[0], [(0, 0)], [], None,
      "(a) Level 1: decide $x_{00}$",
      "UP falsifies row 0, column 0\nand the main diagonal")
panel(axes[1], [(0, 0), (1, 2)], [], 2,
      "(b) Level 2: decide $x_{12}$",
      "row 2 has no free cell:\nits ALO clause is violated")
panel(axes[2], [(0, 0)], [(1, 3), (2, 1)], 3,
      "(c) Learn, backjump to level 1",
      "learned clause forces $\\neg x_{12}$;\nUP forces $x_{13}$, $x_{21}$; row 3 empty")
panel(axes[3], [], [(0, 1), (1, 3), (2, 0), (3, 2)], None,
      "(d) Learn $(\\neg x_{00})$, level 0",
      "search continues and finds\na solution")
fig.tight_layout(w_pad=1.2)
fig.savefig("figures/cdcl_example.pdf", bbox_inches="tight")
plt.close(fig)
print("cdcl figure written")
