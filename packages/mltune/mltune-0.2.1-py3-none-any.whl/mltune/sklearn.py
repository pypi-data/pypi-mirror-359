from typing import Any, Callable
from sklearn.ensemble import RandomForestClassifier
from .base import BaseModelWrapper


class RandomForestModelWrapper(BaseModelWrapper):
    """
    Wrapper for sklearn.ensemble.RandomForestClassifier.

    Initializes the underlying RandomForestClassifier with given hyperparameters.

    Parameters
    ----------
    hyperparameters : dict of str to Any
        Model hyperparameters to configure RandomForestClassifier.
    features : list of str
        List of feature names to use during training and prediction.
    """

    def __init__(self, hyperparameters: dict[str, Any] = None, features: list[str] = None):
        super().__init__(hyperparameters, features)
        self.model = RandomForestClassifier(**self.hyperparameters)

    def get_model_factory(self) -> Callable[[dict[str, Any]], Any]:
        """
        Returns a factory function that creates new RandomForestClassifier instances.

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
            }
            return RandomForestClassifier(**params)

        return factory
