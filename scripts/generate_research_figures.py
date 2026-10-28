from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path("reports/research_balanced/figures")
OUT.mkdir(parents=True, exist_ok=True)


def save_figure(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {name}.png and {name}.pdf")


# Figure 1: Dataset split audit.
fig, ax = plt.subplots(figsize=(8, 5))
splits = ["Train", "Validation", "Test"]
original = np.array([10659, 2379, 2320])
usable = np.array([10656, 2377, 2317])
excluded = original - usable
x = np.arange(len(splits))

ax.bar(x, usable, label="Usable HTML records")
ax.bar(x, excluded, bottom=usable, label="Excluded: empty HTML")
ax.set_xticks(x, splits)
ax.set_ylabel("Number of records")
ax.set_title("Dataset Split and HTML Availability Audit")
ax.legend()
ax.bar_label(ax.containers[0], fmt="%.0f", padding=3)
for i, count in enumerate(excluded):
    ax.annotate(
        f"{count} excluded",
        (i, original[i]),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        fontsize=9,
    )
ax.set_ylim(0, max(original) * 1.12)
fig.tight_layout()
save_figure(fig, "fig1_dataset_html_availability")


# Figure 2: Offline workbook-feature experiments.
# These are the previously reported offline experiments, NOT the new
# live HTML feature experiment. Verify against the saved report before
# publication.
models = ["URL-only", "HTML-only", "Hybrid"]
offline_metrics = {
    "Phishing F1": [0.7807, 0.8087, 0.9645],
    "Average precision": [0.9167, 0.9242, 0.9928],
    "ROC-AUC": [0.9183, 0.9336, 0.9935],
}

fig, ax = plt.subplots(figsize=(9, 5.5))
x = np.arange(len(models))
width = 0.24

for i, (metric, values) in enumerate(offline_metrics.items()):
    bars = ax.bar(
        x + (i - 1) * width,
        values,
        width,
        label=metric,
    )
    ax.bar_label(bars, fmt="%.3f", padding=2, fontsize=8)

ax.set_xticks(x, models)
ax.set_ylim(0.65, 1.04)
ax.set_ylabel("Score")
ax.set_title("Offline Workbook-Feature Experiment Comparison")
ax.legend(loc="lower right")
ax.text(
    0.01, -0.19,
    "Separate from the live HTML-only experiment; confirm provenance and "
    "evaluation comparability before drawing direct conclusions.",
    transform=ax.transAxes,
    fontsize=8,
    wrap=True,
)
fig.tight_layout()
save_figure(fig, "fig2_offline_model_comparison")


# Figure 3: Live HTML-only test confusion matrix.
# Matrix order: rows = actual class, columns = predicted class.
# Class order: legitimate, phishing.
cm = np.array([
    [705, 529],
    [209, 874],
])

fig, ax = plt.subplots(figsize=(6.5, 5.5))
im = ax.imshow(cm, interpolation="nearest")
ax.set_title("Live HTML-Only Model: Test Confusion Matrix")
ax.set_xlabel("Predicted label")
ax.set_ylabel("Actual label")
ax.set_xticks([0, 1], ["Legitimate", "Phishing"])
ax.set_yticks([0, 1], ["Legitimate", "Phishing"])

threshold = cm.max() / 2
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(
            j, i, f"{cm[i, j]:,}",
            ha="center", va="center",
            color="white" if cm[i, j] > threshold else "black",
            fontsize=12,
        )

fig.colorbar(im, ax=ax, label="Number of samples")
fig.tight_layout()
save_figure(fig, "fig3_live_html_confusion_matrix")


# Figure 4: Live HTML-only test metrics.
live_metrics = {
    "Accuracy": 0.6814846785,
    "Phishing precision": 0.6229508197,
    "Phishing recall": 0.8070175439,
    "Phishing F1": 0.7031375704,
    "Average precision": 0.7067829737,
    "ROC-AUC": 0.7835462900,
}

fig, ax = plt.subplots(figsize=(9, 5.5))
names = list(live_metrics.keys())
values = list(live_metrics.values())
bars = ax.barh(names[::-1], values[::-1])
ax.bar_label(bars, fmt="%.3f", padding=4)
ax.set_xlim(0, 1.0)
ax.set_xlabel("Score")
ax.set_title("Live HTML-Only Model: Held-Out Test Metrics")
ax.text(
    0.01, -0.17,
    "Logistic Regression, threshold = 0.5; eight records with empty HTML "
    "excluded across the dataset splits.",
    transform=ax.transAxes,
    fontsize=8,
    wrap=True,
)
fig.tight_layout()
save_figure(fig, "fig4_live_html_test_metrics")


# Figure 5: Research workflow diagram.
fig, ax = plt.subplots(figsize=(12, 3.8))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4)
ax.axis("off")

steps = [
    (0.2, "Dataset\nand labels"),
    (2.2, "Domain-disjoint\ntrain / validation / test"),
    (4.5, "Feature extraction\nand quality audit"),
    (6.8, "Train candidate\nmodels"),
    (9.0, "Select using\nvalidation data"),
    (10.9, "Final test\nevaluation"),
]

for x0, label in steps:
    ax.text(
        x0, 2, label,
        ha="center", va="center",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.55", fc="white", ec="black"),
    )

for i in range(len(steps) - 1):
    x1 = steps[i][0] + 0.7
    x2 = steps[i + 1][0] - 0.7
    ax.annotate(
        "",
        xy=(x2, 2),
        xytext=(x1, 2),
        arrowprops=dict(arrowstyle="->", lw=1.3),
    )

ax.set_title("Phishing Detection Research Evaluation Workflow", pad=12)
fig.tight_layout()
save_figure(fig, "fig5_research_workflow")


# Figure captions for the research report.
captions = """# Research Report Figures

Place these figures in the corresponding methodology and results sections.

1. **Figure 1 — Dataset split and HTML availability audit.**
   The original and usable record counts for the train, validation, and test
   splits. Eight records with empty HTML were excluded from the live HTML-only
   experiment. The split counts and exclusions should be checked against the
   saved audit report before publication.

2. **Figure 2 — Offline workbook-feature experiment comparison.**
   Previously reported URL-only, HTML-only, and hybrid results using offline
   workbook-derived features. These figures are provisional until checked
   against reports/research_balanced/experiment_summary.json and the provenance
   of the feature workbook is established. Do not treat this chart as a direct
   comparison with Figure 4.

3. **Figure 3 — Live HTML-only model confusion matrix.**
   Held-out test counts at threshold 0.5. Rows represent actual labels and
   columns predicted labels. The class order is legitimate, then phishing.

4. **Figure 4 — Live HTML-only held-out test metrics.**
   Logistic Regression test metrics from the live HTML feature experiment.
   The model was selected using validation data; the test set was used for
   final evaluation.

5. **Figure 5 — Research evaluation workflow.**
   Summary of the domain-disjoint evaluation process, from dataset preparation
   through final held-out test evaluation.

**Important limitation:** Figures 2 and 4 represent different experiments.
The offline workbook feature provenance and comparability must be verified
before making a direct performance claim. The live HTML-only experiment uses
five extracted HTML features and excludes records without usable HTML.
"""

(OUT / "figure_captions.md").write_text(captions)
print(f"\nAll figures saved in: {OUT}")
print(f"Captions saved in: {OUT / 'figure_captions.md'}")
