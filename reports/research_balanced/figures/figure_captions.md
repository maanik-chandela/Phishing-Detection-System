# Research Report Figures

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
