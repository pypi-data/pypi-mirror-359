from .base_model_api import BaseModelAPI
from abc import abstractmethod


class BaseEstimatorAPI(BaseModelAPI):
    """Abstract base class for sklearn-like estimators/classifiers."""

    @abstractmethod
    def fit(self, args, X_train, y_train, X_test, y_test):
        pass

    @abstractmethod
    def predict(self, X):
        pass
