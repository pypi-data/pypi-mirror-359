import pandas as pd
from matplotlib import pyplot as plt


def plot_feature_importances(importances: pd.Series, title: str = "Feature Importances") -> None:
    """
    Plot a horizontal bar chart of feature importances.

    Parameters
    ----------
    importances : pd.Series
        Feature importances indexed by feature names.
    title : str, default="Feature Importances"
        Plot title.
    """
    importances.plot(kind='barh')
    plt.title(title)
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.show()


def plot_feature_elimination_progression(score_log: list[tuple[int, float, float]]) -> None:
    """
    Plot CV and train accuracy progression during feature elimination.

    Parameters
    ----------
    score_log : list of tuple of (int, float, float)
        Each tuple contains:
        - number of features remaining (int)
        - cross-validation accuracy score (float)
        - training accuracy score (float)
    """
    if not score_log:
        return
    counts, cv_scores, train_scores = zip(*score_log)
    plt.plot(counts, cv_scores, label="CV Accuracy", marker='o')
    plt.plot(counts, train_scores, label="Train Accuracy", marker='x')
    plt.xlabel("Number of Features")
    plt.ylabel("Accuracy")
    plt.title("Train vs CV Accuracy During Feature Elimination")
    plt.legend()
    plt.grid(True)
    plt.gca().invert_xaxis()
    plt.tight_layout()
    plt.show()
