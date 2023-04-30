import json
import pickle
import os
import sys

sys.path.append(os.getcwd())

import pandas as pd
import numpy as np


ingredientMapPath = "data/mappings/map.csv"
ingredientMapDF = pd.read_csv(ingredientMapPath)
ingredientMapDF = ingredientMapDF.drop_duplicates()

productsCSVPath = "data/tagged-products-full.csv"
productsDF = pd.read_csv(productsCSVPath)


indexes = []

for i, row in ingredientMapDF.iterrows():
    ingredientName, productEquiv = row['ingredient'], row['product']
    thing = productsDF.loc[productsDF['input'] == productEquiv].index[0]
    indexes.append(thing)

# print(indexes)

with open("models/metric/encoding/product-space-full.npy", 'rb') as f:
    products_metric = np.load(f, allow_pickle=True)

targets = products_metric[indexes]

# print(targets)

with open("models/metric/encoding/ingredient_targets.npy", 'wb') as f:
    np.save(f, np.array(targets))
