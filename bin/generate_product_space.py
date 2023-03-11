import json
import os
import sys

sys.path.append(os.getcwd())

import numpy as np
import scipy.sparse
import pandas as pd
import pickle
from sklearn.neighbors import BallTree
from sklearn.pipeline import Pipeline

from training.metrics import pipelines


productsDF = pd.read_csv("data/coles-products.csv")
comparisonsDF = pd.read_csv("data/product-comparisons.csv")

with open("data/encoding/comparison-indexes.npy", 'rb') as f:
    compIndexes = np.load(f, allow_pickle=True)

# print(productsDF.head())


# Construct the preprocessing pipeline
preprocessing_pipeline = pipelines.get_preprocessing_pipeline(num_dims=900)

# Encode the products dataframe into a numpy array with reduced dimensions
products_trans = preprocessing_pipeline.fit_transform(productsDF)


# Construct the metric learning pipeline using the transformed
# products as a preprocessor
metric_pipeline = pipelines.get_metric_pipeline(preprocessor=products_trans)


print("Explained variance post-reduction:")
variance = sum(preprocessing_pipeline.named_steps['dimension_reduction'].explained_variance_ratio_)*100
print("%.2f" % variance + "%")

# Fit the metric learner to the given triplets
metric_pipeline.fit(compIndexes)


# transform the encoded products into the metric space
product_metric_trans = metric_pipeline.transform(products_trans)

# create a nearest neighbours query tree from the metric space
tree = BallTree(product_metric_trans)


query_id = 100
dist, ind = tree.query(product_metric_trans[query_id:query_id+1], k=10)
print(productsDF.iloc[ind[0]])

with open("data/encoding/product-space-balltree.pkl", 'wb') as p:
    pickle.dump(tree, p)
