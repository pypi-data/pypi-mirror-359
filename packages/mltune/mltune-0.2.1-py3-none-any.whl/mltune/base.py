import json
from typing import Any, Callable
import pandas as pd

from mltune.tuning import tune_model_parameters_and_features


class BaseModelWrapper:
    """
    Base wrapper for ML models.

    Stores hyperparameters and feature list, and provides
    JSON serialization and basic fit/predict interface.

    Subclasses must set `self.model` to the actual model instance.

    Attributes
    ----------
    hyperparameters : dict
        Hyperparameters for the model.
    features : list of str
        List of feature names to use.
    model : Any
        Underlying ML model instance (set by subclass).
    """

    def __init__(self, hyperparameters: dict[str, Any] = None, features: list[str] = None):
        """
        Initialize the wrapper.

        Parameters
        ----------
        hyperparameters : dict of str to Any
            Dictionary of hyperparameters to configure the model.
        features : list of str
            List of feature names to use during training and prediction.
        """
        self.hyperparameters = hyperparameters or {}
        self.features = features or []
        self.model = None  # to be set in subclass

    def get_model_factory(self) -> Callable[[dict[str, Any]], Any]:
        """
        Returns a factory function that creates new model instances
        with fixed hyperparameters and dynamic hyperparameters.

        The returned factory takes a dictionary of dynamic hyperparameters
        (those to be tuned, e.g., via grid search) and returns a new
        model instance ready to fit.

        Returns
        -------
        Callable[[dict[str, Any]], Any]
            A factory function: dynamic_params → model instance.

        Raises
        ------
        NotImplementedError
            If the method is not overridden by a subclass.
        """
        raise NotImplementedError("Subclasses must implement get_model_factory()")

    def to_json(self) -> str:
        """
        Serialize the wrapper's configuration to a JSON string.

        Returns
        -------
        str
            JSON string representing model class, hyperparameters, and features.
        """
        return json.dumps({
            "model_class": self.__class__.__name__,
            "hyperparameters": self.hyperparameters,
            "features": self.features
        })

    @classmethod
    def from_json(cls, json_string: str) -> 'BaseModelWrapper':
        """
        Deserialize from JSON string to create a new wrapper instance.

        Parameters
        ----------
        json_string : str
            JSON string created by `to_json`.

        Returns
        -------
        BaseModelWrapper
            A new instance of the wrapper with loaded hyperparameters and features.
        """
        data = json.loads(json_string)
        return cls(data["hyperparameters"], data["features"])

    def fit(self, X: pd.DataFrame, y: pd.Series) -> Any:
        """
        Fit the underlying model to training data.

        Parameters
        ----------
        X : pd.DataFrame
            Training feature data.
        y : pd.Series
            Training target labels.

        Returns
        -------
        Any
            Result of the model's fit method.
        """
        return self.model.fit(X[self.features], y)

    def predict(self, X: pd.DataFrame) -> Any:
        """
        Predict target values using the trained model.

        Parameters
        ----------
        X : pd.DataFrame
            Input feature data.

        Returns
        -------
        Any
            Predicted target values.
        """
        return self.model.predict(X[self.features])

    def autotune(
            self,
            X: pd.DataFrame,
            y: pd.Series,
            hyperparam_initial_info: Any,
            splits: int = 5,
            feature_selection_strategy: str = "none",
            hyperparam_tuning_strategy: str = "grid_search",
            verbose: bool = False,
            plot: bool = False
    ) -> None:
        """
        Auto-tune model hyperparameters and feature set.

        Parameters
        ----------
        X : pd.DataFrame
            Full feature dataset.
        y : pd.Series
            Target labels.
        hyperparam_initial_info : Amy
            Initial info for hyperparameter tuning (e.g. Parameter grid for "grid_search" strategy).
        splits : int
            Number of CV folds.
        feature_selection_strategy : str
            Strategy for feature elimination ("greedy_backward" or "none").
        hyperparam_tuning_strategy : str
            Strategy for hyperparameter tuning (currently only "grid_search").
        verbose : bool
            Print logs during tuning.
        plot : bool, default=False
            If true, show plot with cv/train accuracy
        """
        # call function from tuning.py
        best_params, best_features = tune_model_parameters_and_features(
            X, y,
            model_factory=self.get_model_factory(),
            features=self.features,
            hyperparam_initial_info=hyperparam_initial_info,
            splits=splits,
            feature_selection_strategy=feature_selection_strategy,
            hyperparam_tuning_strategy=hyperparam_tuning_strategy,
            verbose=verbose,
            plot=plot
        )
        # Update internal state:
        self.hyperparameters = best_params
        self.features = best_features

        self.model = self.get_model_factory()(best_params)
        self.model.fit(X[self.features], y)
