import pandas as pd
from metric_learn import SCML
from sklearn.impute import SimpleImputer



class PipelineSCML(SCML):
    '''
    a wrapper for the SCML estimator in the metric-learn package, so it can be
    used in a sklearn Pipeline
    '''
    # add an optional y=None
    def fit(self, triplets, y=None):
        super().fit(triplets)



class PandasSimpleImputer(SimpleImputer):
    """A wrapper around `SimpleImputer` to return data frames with columns.
    https://stackoverflow.com/questions/62191643/is-there-a-way-to-force-simpleimputer-to-return-a-pandas-dataframe
    """

    def fit(self, X, y=None):
        self.columns = X.columns
        return super().fit(X, y)

    def transform(self, X):
        return pd.DataFrame(super().transform(X), columns=self.columns)