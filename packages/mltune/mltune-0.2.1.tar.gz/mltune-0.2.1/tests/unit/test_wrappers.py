import pytest
from mltune.wrappers import RandomForestModelWrapper, XGBoostModelWrapper, LightGBMModelWrapper
from sklearn.ensemble import RandomForestClassifier

if XGBoostModelWrapper:
    from xgboost import XGBClassifier

if LightGBMModelWrapper:
    from lightgbm import LGBMClassifier


def test_sklearn_wrapper_json():
    params = {"n_estimators": 10}
    features = ["age", "fare"]
    wrapper = RandomForestModelWrapper(params, features)

    # check model type
    assert isinstance(wrapper.model, RandomForestClassifier)

    data = wrapper.to_json()
    wrapper2 = RandomForestModelWrapper.from_json(data)

    assert wrapper2.hyperparameters == params
    assert wrapper2.features == features
    # check model created on reload
    assert isinstance(wrapper2.model, RandomForestClassifier)


@pytest.mark.skipif(XGBoostModelWrapper is None, reason="xgboost not installed")
def test_xgboost_wrapper_json():
    params = {"n_estimators": 10}
    features = ["pclass", "sex"]
    wrapper = XGBoostModelWrapper(params, features)

    assert isinstance(wrapper.model, XGBClassifier)

    data = wrapper.to_json()
    wrapper2 = XGBoostModelWrapper.from_json(data)

    assert wrapper2.hyperparameters == params
    assert wrapper2.features == features
    assert isinstance(wrapper2.model, XGBClassifier)


@pytest.mark.skipif(LightGBMModelWrapper is None, reason="lightgbm not installed")
def test_lightgbm_wrapper_json():
    params = {"n_estimators": 10}
    features = ["sibsp", "parch"]
    wrapper = LightGBMModelWrapper(params, features)

    assert isinstance(wrapper.model, LGBMClassifier)

    data = wrapper.to_json()
    wrapper2 = LightGBMModelWrapper.from_json(data)

    assert wrapper2.hyperparameters == params
    assert wrapper2.features == features
    assert isinstance(wrapper2.model, LGBMClassifier)
