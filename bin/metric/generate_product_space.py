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
from scipy.spatial.distance import cosine

from training.metrics import pipelines
from training import utils

num_dimensions = int(sys.argv[1])
model_includes = str(sys.argv[2]).split(" ")


productsDF = pd.read_csv("data/tagged-products-full.csv")
productsDF["name"] = productsDF["name"].apply(utils.normalizeTokens)
productsDF["variant"] = productsDF["variant"].apply(utils.normalizeTokens)

with open("data/comparisons/aug-comparison-indexes.npy", 'rb') as f:
    compIndexes = np.load(f, allow_pickle=True)

# print(productsDF.head())


# Construct the preprocessing pipeline
preprocessing_pipeline = pipelines.get_preprocessing_pipeline(num_dims=num_dimensions, categories=model_includes)

# Encode the products dataframe into a numpy array with reduced dimensions
products_trans = preprocessing_pipeline.fit_transform(productsDF)

# Construct the metric learning pipeline using the transformed
# products as a preprocessor
metric_pipeline = pipelines.get_metric_pipeline(preprocessor=products_trans, max_iter=10000)

print(products_trans.shape)


print("Explained variance post-reduction:")
variance = sum(preprocessing_pipeline.named_steps['dimension_reduction'].explained_variance_ratio_)*100
print("%.2f" % variance + "%")

# Fit the metric learner to the given triplets
metric_pipeline.fit(compIndexes)


# transform the encoded products into the metric space
product_metric_trans = metric_pipeline.transform(products_trans)

with open("models/metric/encoding/product-space-full.npy", 'wb') as f:
    np.save(f, product_metric_trans)

# create a nearest neighbours query tree from the metric space
tree = BallTree(product_metric_trans, metric=cosine)

print("saving model")

with open("models/metric/product-encoding-nn.pkl", 'wb') as p:
    pickle.dump(tree, p)

print("saving preprocessing pipeline")

with open("models/metric/encoding/preprocessing-pipeline.pkl", 'wb') as p:
    pickle.dump(preprocessing_pipeline, p)

print("saving metric pipeline")

with open("models/metric/encoding/metric_pipeline.pkl", 'wb') as p:
    pickle.dump(metric_pipeline, p)

print("saving tsv data and labels")

with open("tsv/data.tsv", 'w') as f1, open("tsv/labels.tsv", 'w') as f2:
    f2.write("\t".join([str(item) for item in productsDF.columns.tolist()]) + '\n')
    for index, row in enumerate(product_metric_trans):
        f1.write("\t".join([str(num) for num in row]) + '\n')
        f2.write("\t".join([str(item) for item in productsDF.iloc[index].tolist()]) + '\n')
