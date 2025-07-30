from typing import Any, Callable

try:
    from xgboost import XGBClassifier
except ImportError as e:
    raise ImportError("XGBoostModelWrapper requires 'xgboost'. Install with: pip install mltune[xgboost]") from e

from .base import BaseModelWrapper


class XGBoostModelWrapper(BaseModelWrapper):
    """
    Wrapper for xgboost.XGBClassifier.

    Initializes the underlying XGBClassifier with given hyperparameters.

    Parameters
    ----------
    hyperparameters : dict of str to Any
        Model hyperparameters to configure RandomForestClassifier.
    features : list of str
        List of feature names to use during training and prediction.
    """

    def __init__(self, hyperparameters: dict[str, Any] = None, features: list[str] = None):
        super().__init__(hyperparameters, features)
        self.model = XGBClassifier(**self.hyperparameters)

    def get_model_factory(self) -> Callable[[dict[str, Any]], Any]:
        """
        Returns a factory function that creates new XGBClassifier instances.

        Returns
        -------
        Callable[[dict[str, Any]], Any]
            A factory function: dynamic_params → model instance.
        """

        def factory(dynamic_params: dict[str, Any] = None) -> Any:
            if dynamic_params is None:
                dynamic_params = {}
            params = {
                **dynamic_params,
                "random_state": 1,
                "eval_metric": "logloss"
            }
            return XGBClassifier(**params)

        return factory
