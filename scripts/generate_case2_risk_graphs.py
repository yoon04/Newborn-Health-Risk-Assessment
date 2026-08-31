"""Generate full-size fuzzy output graphs for experimental Case C2."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fuzzy_logic import (  # noqa: E402
    apply_birth_related_rules,
    apply_family_history_rules,
    apply_hierarchical_risk_rules,
    apply_immediate_condition_rules,
    defuzzify_risk,
    fuzzify_apgar,
    fuzzify_birth_week,
    fuzzify_birth_weight,
    fuzzify_delivery_comp,
    fuzzify_maternal_age,
    risk_output_curves,
)


OUTPUT_DIR = ROOT / "paper_figures" / "case2"
COLORS = {
    "low": "#2a9d4b",
    "moderate": "#e6a700",
    "high": "#d43f3a",
    "combined": "#2867b2",
    "centroid": "#222222",
}


def case2_results():
    fuzzy_inputs = {
        "apgar": fuzzify_apgar(7),
        "birth_week": fuzzify_birth_week(36),
        "birth_weight": fuzzify_birth_weight(2400),
        "maternal_age": fuzzify_maternal_age(31),
        "delivery_comp": fuzzify_delivery_comp(1),
    }

    immediate = apply_immediate_condition_rules(fuzzy_inputs)
    birth = apply_birth_related_rules(fuzzy_inputs)
    family = apply_family_history_rules({"status": "unknown", "affected_relative": ""})
    module_indices = [
        defuzzify_risk(immediate),
        defuzzify_risk(birth),
        defuzzify_risk(family),
    ]
    final = apply_hierarchical_risk_rules(*module_indices)
    return {
        "Immediate Condition Risk": immediate,
        "Birth-Related Risk": birth,
        "Family-History Risk": family,
        "Final Risk": final,
    }


def full_output_shapes(x):
    low = np.clip((50 - x) / 25, 0, 1)
    moderate = np.clip(np.minimum((x - 25) / 25, (75 - x) / 25), 0, 1)
    high = np.clip((x - 50) / 25, 0, 1)
    return {"low": low, "moderate": moderate, "high": high}


def draw_risk_graph(ax, title, levels):
    x, low, moderate, high, combined = risk_output_curves(levels)
    clipped = {"low": low, "moderate": moderate, "high": high}
    full = full_output_shapes(x)
    denominator = simpson(combined, x=x)
    centroid = simpson(x * combined, x=x) / denominator

    for label in ("low", "moderate", "high"):
        color = COLORS[label]
        display = label.title()
        ax.plot(x, full[label], color=color, linewidth=1.5, linestyle=":",
                alpha=0.75, label=f"{display} membership")
        ax.plot(x, clipped[label], color=color, linewidth=2.4,
                label=f"{display} activation = {levels[label]:.2f}")
        ax.fill_between(x, 0, clipped[label], color=color, alpha=0.20)

    ax.plot(x, combined, color=COLORS["combined"], linewidth=2.6,
            linestyle="--", label="Aggregated output")
    ax.axvline(centroid, color=COLORS["centroid"], linewidth=2,
               linestyle="-.", label=f"Centroid = {centroid:.2f}")
    ax.annotate(
        f"Risk index = {centroid:.2f}",
        xy=(centroid, 0.02),
        xytext=(centroid - 23 if centroid > 50 else centroid + 6, 0.15),
        arrowprops={"arrowstyle": "->", "color": COLORS["centroid"]},
        fontsize=10,
        fontweight="bold",
    )
    ax.set_title(f"Case C2: {title}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Risk index (0-100)", fontsize=11)
    ax.set_ylabel("Membership degree", fontsize=11)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.08)
    ax.set_xticks(np.arange(0, 101, 10))
    ax.set_yticks(np.arange(0, 1.01, 0.1))
    ax.grid(True, color="#d9d9d9", linewidth=0.6, alpha=0.8)
    ax.legend(loc="upper right", fontsize=8.5, ncol=2, frameon=True)
    return centroid


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    levels_by_graph = case2_results()
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })

    for title, levels in levels_by_graph.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        draw_risk_graph(ax, title, levels)
        fig.tight_layout()
        filename = title.lower().replace("-", "_").replace(" ", "_") + ".png"
        fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
        plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(17, 11))
    for ax, (title, levels) in zip(axes.flat, levels_by_graph.items()):
        draw_risk_graph(ax, title, levels)
    fig.tight_layout(pad=2.5)
    fig.savefig(OUTPUT_DIR / "case2_fuzzy_risk_relationships.png", dpi=300,
                bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
