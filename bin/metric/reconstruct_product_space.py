import os
import sys

sys.path.append(os.getcwd())

import numpy as np
import pandas as pd
import pickle
from sklearn.neighbors import BallTree
from scipy.spatial.distance import cosine



productsDF = pd.read_csv("data/tagged-products-full.csv")


with open("models/metric/encoding/preprocessing-pipeline.pkl", 'rb') as p:
    preprocessing_pipeline = pickle.load(p)

with open("models/metric/encoding/metric_pipeline.pkl", 'rb') as p:
    metric_pipeline = pickle.load(p)

# Encode the products dataframe into a numpy array with reduced dimensions
products_trans = preprocessing_pipeline.transform(productsDF)

# transform the encoded products into the metric space
product_metric_trans = metric_pipeline.transform(products_trans)

print("Saving encoded product metric space..")

with open("models/metric/encoding/product-space-full.npy", 'wb') as f:
    np.save(f, product_metric_trans)

# create a nearest neighbours query tree from the metric space
tree = BallTree(product_metric_trans, metric=cosine)

print("Saving nearest neighbours model..")

with open("models/metric/product-encoding-nn.pkl", 'wb') as p:
    pickle.dump(tree, p)

