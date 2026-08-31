"""Generate publication-ready fuzzy output graphs for experimental Case C1."""

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


OUTPUT_DIR = ROOT / "paper_figures" / "case1"
COLORS = {
    "low": "#2a9d4b",
    "moderate": "#e6a700",
    "high": "#d43f3a",
    "combined": "#2867b2",
    "centroid": "#222222",
}


def case1_results():
    fuzzy_inputs = {
        "apgar": fuzzify_apgar(10),
        "birth_week": fuzzify_birth_week(39),
        "birth_weight": fuzzify_birth_weight(3200),
        "maternal_age": fuzzify_maternal_age(28),
        "delivery_comp": fuzzify_delivery_comp(0),
    }

    immediate = apply_immediate_condition_rules(fuzzy_inputs)
    birth = apply_birth_related_rules(fuzzy_inputs)
    family = apply_family_history_rules({"status": "no", "affected_relative": ""})

    indices = {
        "Immediate Condition Risk": defuzzify_risk(immediate),
        "Birth-Related Risk": defuzzify_risk(birth),
        "Family-History Risk": defuzzify_risk(family),
    }
    final = apply_hierarchical_risk_rules(*indices.values())
    return {
        "Immediate Condition Risk": immediate,
        "Birth-Related Risk": birth,
        "Family-History Risk": family,
        "Final Risk": final,
    }, indices


def draw_risk_graph(ax, title, levels):
    x, low, moderate, high, combined = risk_output_curves(levels)
    denominator = simpson(combined, x=x)
    centroid = simpson(x * combined, x=x) / denominator

    for label, curve in (("Low", low), ("Moderate", moderate), ("High", high)):
        color = COLORS[label.lower()]
        ax.plot(x, curve, color=color, linewidth=2, label=label)
        ax.fill_between(x, 0, curve, color=color, alpha=0.12)

    ax.plot(x, combined, color=COLORS["combined"], linewidth=2.2,
            linestyle="--", label="Aggregated output")
    ax.axvline(centroid, color=COLORS["centroid"], linewidth=1.8,
               linestyle=":", label=f"Centroid = {centroid:.2f}")
    ax.annotate(
        f"{centroid:.2f}",
        xy=(centroid, 0.03),
        xytext=(centroid + 5, 0.25),
        arrowprops={"arrowstyle": "->", "color": COLORS["centroid"]},
        fontsize=9,
    )
    ax.set_title(f"Case C1: {title}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Risk index (0-100)")
    ax.set_ylabel("Membership degree")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(np.arange(0, 101, 20))
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.grid(True, color="#d9d9d9", linewidth=0.6, alpha=0.8)
    ax.legend(loc="upper right", fontsize=8, frameon=True)
    return centroid


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    levels_by_graph, _indices = case1_results()

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })

    for title, levels in levels_by_graph.items():
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        draw_risk_graph(ax, title, levels)
        fig.tight_layout()
        filename = title.lower().replace("-", "_").replace(" ", "_") + ".png"
        fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
        plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (title, levels) in zip(axes.flat, levels_by_graph.items()):
        draw_risk_graph(ax, title, levels)
    fig.tight_layout(pad=2.0)
    fig.savefig(OUTPUT_DIR / "case1_fuzzy_risk_relationships.png", dpi=300,
                bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
