# 🧰 mltune

![Unit Tests](https://github.com/birrgrrim/mltune/actions/workflows/unit.yml/badge.svg)
![Integration Tests](https://github.com/birrgrrim/mltune/actions/workflows/integration.yml/badge.svg)
[![Release](https://img.shields.io/github/v/release/birrgrrim/mltune)](https://github.com/birrgrrim/mltune/releases)


# mltune

**Flexible ML hyperparameter tuning and feature selection toolkit**  
Supports scikit-learn models and optionally XGBoost / LightGBM.

---

## ✨ Features

- Auto-tune hyperparameters (GridSearch)
- Optional greedy backward feature elimination
- Modular `Wrapper` classes for scikit-learn, XGBoost, LightGBM
- Unit & integration tested, Python 3.12+
- Lightweight, simple API

---

## 📦 Installation

Install base (requires Python ≥3.8):

```bash
pip install mltune
```

For optional XGBoost / LightGBM support:

```bash
pip install mltune[xgboost,lgbm]
```

---

## 🚀 Example usage

```python
from mltune.wrappers import RandomForestModelWrapper

# Load or prepare data
X, y, X_test = load_data()

# Initialize wrapper with all features
wrapper = RandomForestModelWrapper(features=list(X.columns))

# Auto-tune hyperparameters & feature set
wrapper.autotune(
    X, y,
    hyperparam_initial_info={
        'n_estimators': [90, 95, 100, 105, 110],
        'max_depth': [9, 10, 11]
    },
    feature_selection_strategy="greedy_backward",
    verbose=True,
    plot=True
)

# Wrapper will use calculated hyperparameters & feature set
predictions = wrapper.predict(X_test)

```

---

## ✅ Implemented
 - Wrappers:
  - RandomForestModelWrapper
  - XGBoostModelWrapper
  - LightGBMModelWrapper
 - Auto hyperparameter tuning: 
  - grid_search
 - Feature selection strategy: 
  - none (skip feature elimination)
  - greedy_backward

---

## 🧭 Planned / Roadmap
 - Add other feature selection strategies (e.g. forward, recursive)
 - Add other hyperparameter tuning strategies (e.g. Bayesian optimization)
 - Voting strategies

---

## 📦 Development

Clone repo, install dev deps:

```bash
uv pip install -e .[dev] --system
```

Run tests:

```bash
pytest -v
```

---

## 📚 Documentation

[API Reference (HTML)](https://birrgrrim.github.io/mltune/)

---

## 📜 License

Released under the [MIT License](LICENSE).

---

## 📌 Status

Beta: Work in progress. Contributions and ideas welcome!