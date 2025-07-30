import pandas as pd
from mltune.wrappers import RandomForestModelWrapper


def test_autotune_without_feature_selection_on_titanic():
    # Tiny dummy Titanic-like dataset
    X = pd.DataFrame({
        "Pclass": [3, 1, 3, 1, 2, 3, 2, 1],
        "Sex_male": [1, 0, 1, 0, 1, 1, 0, 0],
        "Age": [22, 38, 26, 35, 28, 2, 30, 54],
        "Fare": [7.25, 71.28, 7.92, 53.1, 8.05, 21.07, 13.0, 51.86]
    })
    y = pd.Series([0, 1, 1, 1, 0, 0, 1, 1])

    initial_features = list(X.columns)

    param_grid = {
        "n_estimators": [5, 10],
        "max_depth": [2, 3]
    }

    wrapper = RandomForestModelWrapper(
        features=initial_features
    )

    wrapper.autotune(
        X, y,
        hyperparam_initial_info=param_grid,
        feature_selection_strategy="none",  # ✅ only tune hyperparameters
        splits=2,
        verbose=True,
        plot=False
    )

    # Check that hyperparameters were tuned (i.e., set)
    assert isinstance(wrapper.hyperparameters, dict)
    assert "n_estimators" in wrapper.hyperparameters

    # Check that features list remains the same
    assert wrapper.features == initial_features


def test_greedy_backward_autotune_on_titanic(capsys):
    # 🐋 Tiny Titanic-like dataset just for testing; replace with real one if you want
    X = pd.DataFrame({
        "Pclass": [3, 1, 3, 1, 2, 3, 2, 1],
        "Sex_male": [1, 0, 1, 0, 1, 1, 0, 0],
        "Age": [22, 38, 26, 35, 28, 2, 30, 54],
        "Fare": [7.25, 71.28, 7.92, 53.1, 8.05, 21.07, 13.0, 51.86]
    })
    y = pd.Series([0, 1, 1, 1, 0, 0, 1, 1])

    # ⚙ Initial hyperparameter grid: very small, quick test
    param_grid = {
        "n_estimators": [5, 10],
        "max_depth": [2, 3]
    }

    # Create wrapper with all features
    wrapper = RandomForestModelWrapper(features=list(X.columns))

    # Autotune; should mutate wrapper.hyperparameters & wrapper.features
    wrapper.autotune(
        X, y,
        hyperparam_initial_info=param_grid,
        splits=2,
        feature_selection_strategy='greedy_backward',
        verbose=True,
        plot=False
    )

    # ✅ Check: should find at least 1 hyperparam and subset of features
    assert isinstance(wrapper.hyperparameters, dict)
    assert wrapper.hyperparameters  # not empty
    assert isinstance(wrapper.features, list)
    assert wrapper.features  # not empty
    # Check model fitted
    assert wrapper.model is not None

    # Check model can predict
    preds = wrapper.model.predict(X[wrapper.features])
    assert len(preds) == len(y)

    captured = capsys.readouterr()
    # captured.out contains stdout, captured.err stderr

    assert "🔰 Initial CV score" in captured.out
    assert "Try removing 'Pclass'" in captured.out
    assert "✅ Removed 'Fare'" in captured.out
    assert "🎯 Final feature set:" in captured.out
    assert "✅ Best CV Accuracy:" in captured.out
