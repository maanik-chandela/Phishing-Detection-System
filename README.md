# Machine Learning-Based Phishing Website Detection

A BTech mini-project for detecting potentially malicious
websites using machine learning and interpretable risk assessment.

## Current capabilities

- URL feature extraction
- Logistic Regression
- Random Forest
- Gradient Boosting
- Domain-grouped model evaluation
- Phishing risk score
- Rule-based suspicious indicators
- Security recommendations
- FastAPI backend
- HTML/CSS/JavaScript dashboard

## Current limitation

The deployed model performs URL-only analysis.

Static HTML analysis, domain intelligence, and the full
hybrid model are planned extensions.

The risk score is not yet probability-calibrated.

## Dataset

CompPhish dataset.

The dataset is not redistributed in this repository.

## Model training

Place All_Features_threshold90.xlsx in data/raw/.

Run:

```bash
python -m scripts.train_live_model
```

## Start backend

```bash
python -m uvicorn backend.main:app --reload
```

## Start frontend

```bash
python -m http.server 5500 --directory frontend
```

## Testing

```bash
python -m pytest tests/ -v
```

## Disclaimer

This tool provides an automated assessment, not a guarantee
that a website is safe or malicious.