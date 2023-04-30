import os
import sys

sys.path.append(os.getcwd())

from sklearn.preprocessing import OneHotEncoder, Normalizer
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD

from .estimators import PandasSimpleImputer, PipelineSCML
from enums import ProductPricing, ProductUnit

### which columns need which type of processing
def get_categories(categories):
    # Get all possible categories for unit columns
    # ppList = ["per 1kg", "per L", "per 100g", ...]
    ppList = [[item.value for item in list(ProductPricing)]]
    puList = [[item.value for item in list(ProductUnit)]]

    onehot_token_cols = ['brand']   # one-hot encoding
    binary_token_cols = ['name', 'variant', 'prep', 'pack']         # binary count encoding
    unit_cols = {'pricingPer': ppList,              # one-hot encoding,
                'productSizeUnits': puList}            # with given categories
    numerical_cols = ['pricePer', 'priceTotal',     # normalization
                    'productSize']
    
    if "noNum" in categories:
        numerical_cols = []
    if "noUnit" in categories:
        unit_cols = dict()
    if "noBrand" in categories:
        onehot_token_cols = []
    if "noPrepnoPack" in categories:
        binary_token_cols = ['name', 'variant']

    return (onehot_token_cols, binary_token_cols, unit_cols, numerical_cols)

def get_preprocessing_pipeline(num_dims, categories):

    onehot_token_cols, binary_token_cols, unit_cols, numerical_cols = get_categories(categories)

    # Fill empty string values (np.nan) with ""
    # No need to fill empty numerical values, these are filtered out by
    # the Coles website scraper.
    imputPipeline = Pipeline(
        steps = [
            ('imput', PandasSimpleImputer(strategy="constant", fill_value=""))
        ]
    )

    # one-hot token encoding
    ohtPipe = Pipeline(
        steps = [
            ('onehot_token', OneHotEncoder()),
        ]
    )

    # binary token encoding (bag-of-words but with counts either 0 or 1)
    binaryPipe = Pipeline(
        steps=[
            ('count_token', CountVectorizer(binary=True)),
        ]
    )

    # Have to set up OneHotEncoder estimators with specific categories,
    # so we use the ppList and puList above as categories
    unitPipes = dict()
    for column_name, categories in unit_cols.items():
        unitPipes[column_name] = Pipeline(
            steps = [
                ('onehot_token', OneHotEncoder(categories=categories)),
            ]
        )

    # Normalizer
    normPipe = Pipeline(
        steps = [
            ('normalize_num', Normalizer()),
        ]
    )

    # Construct a ColumnTransformer, which will encode different columns separately
    # Some text columns encode possible values in one-hot vectors
    # Some text columns encode token presence in a binary vector
    # Units are one-hot encoded (per kg, g, L, etc)
    # Numerical columns are normalized
    columnTransformers = ColumnTransformer(
        transformers=[
            (f'handle_onehot_text', ohtPipe, onehot_token_cols)
        ] + [
            (f'handle_binary_text_{tokenType}', binaryPipe, tokenType) 
            for tokenType in binary_token_cols
        ] + [
            (f'handle_onehot_unit_{column_name}', pipeline, [column_name]) for column_name, pipeline in unitPipes.items()
        ] + [
            ('handle_numerical', normPipe, numerical_cols)
        ]
    )

    # We need to reduce the number of dimensions in the data so that the
    # training examples > dimensions for metric learning (SCML, specifically)
    dimensional_reduction = TruncatedSVD(n_components=num_dims)

    # Construct the entire pre-processing pipeline
    preprocessing_pipeline = Pipeline(
        steps = [
            ('imput', imputPipeline),                       # replace missing values
            ('transformation', columnTransformers),         # encode columns
            ('dimension_reduction', dimensional_reduction), # reduce dimensions
        ]
    )

    return preprocessing_pipeline


def get_ingr_pipeline():

    ### which columns need which type of processing
    onehot_token_cols = []              # one-hot encoding
    binary_token_cols = ['NAME']        # binary count encoding

    # Fill empty string values (np.nan) with ""
    # No need to fill empty numerical values, these are filtered out by
    # the Coles website scraper.
    imputPipeline = Pipeline(
        steps = [
            ('imput', PandasSimpleImputer(strategy="constant", fill_value=""))
        ]
    )

    # one-hot token encoding
    ohtPipe = Pipeline(
        steps = [
            ('onehot_token', OneHotEncoder()),
        ]
    )

    # binary token encoding (bag-of-words but with counts either 0 or 1)
    binaryPipe = Pipeline(
        steps=[
            ('count_token', CountVectorizer(binary=True)),
        ]
    )

    # Construct a ColumnTransformer, which will encode different columns separately
    # Some text columns encode possible values in one-hot vectors
    # Some text columns encode token presence in a binary vector
    # Units are one-hot encoded (per kg, g, L, etc)
    # Numerical columns are normalized
    columnTransformers = ColumnTransformer(
        transformers=[
            (f'handle_onehot_text', ohtPipe, onehot_token_cols)
        ] + [
            (f'handle_binary_text_{tokenType}', binaryPipe, tokenType) 
            for tokenType in binary_token_cols
        ]
    )

    # Construct the entire pre-processing pipeline
    preprocessing_pipeline = Pipeline(
        steps = [
            ('imput', imputPipeline),                       # replace missing values
            ('transformation', columnTransformers),         # encode columns
        ]
    )

    return preprocessing_pipeline


def get_metric_pipeline(preprocessor, max_iter=10000, n_basis=1000):
    metric_pipeline = Pipeline(
        steps = [
            ('scml', PipelineSCML(preprocessor=preprocessor, max_iter=max_iter, 
                                  n_basis=n_basis, verbose=True, output_iter=2000,
                                  ))
        ]
    )
    return metric_pipeline