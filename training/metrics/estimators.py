import pandas as pd
from .scml import _BaseSCMLNoCheck
from metric_learn.base_metric import _TripletsClassifierMixin
from sklearn.impute import SimpleImputer


class PipelineSCML(_BaseSCMLNoCheck, _TripletsClassifierMixin):
    '''
    a wrapper for the SCML estimator in the metric-learn package, so it can be
    used in a sklearn Pipeline. also inherits from the _BaseSCMLNoCheck class so
    estimator doesn't reconstruct the array when a preprocessor is used
    '''
    def fit(self, triplets, y=None):
        self._fit(triplets)


class PandasSimpleImputer(SimpleImputer):
    """A wrapper around `SimpleImputer` to return data frames with columns.
    https://stackoverflow.com/questions/62191643/is-there-a-way-to-force-simpleimputer-to-return-a-pandas-dataframe
    """

    def fit(self, X, y=None):
        self.columns = X.columns
        return super().fit(X, y)

    def transform(self, X):
        return pd.DataFrame(super().transform(X), columns=self.columns)