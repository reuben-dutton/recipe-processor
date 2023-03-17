import pickle
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

import sys


productsDF = pd.read_csv("data/coles-products.csv")

with open("data/encoding/products-metric.npy", 'rb') as f:
    products_metric = np.load(f, allow_pickle=True)

with open("models/product-space-full.pkl", 'rb') as p:
    tree = pickle.load(p)

query_id = int(sys.argv[1])
dist, ind = tree.query(products_metric[query_id:query_id+1], k=10)
close = [i for (dist, i) in zip(dist[0], ind[0]) if dist < 0.01]
productsDF.loc[ind[0], "dist"] = dist[0]
print(productsDF.iloc[close])

print(products_metric.shape)