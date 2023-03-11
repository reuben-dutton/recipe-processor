import csv
import sys
import os

import pandas as pd
import numpy as np

comparisonCsvPath = "data/product-comparisons.csv"
productsCsvPath = "data/coles-products.csv"

comparisons = pd.read_csv(comparisonCsvPath)
products = pd.read_csv(productsCsvPath)

compIndexes = []

def find_product_index(productName):
    sub = products.index[products.input == productName].tolist()
    if sub == []:
        return -1
    return sub[0]

for index, comparison in comparisons.iterrows():
    index1 = find_product_index(comparison['product'])
    index2 = find_product_index(comparison['alt1'])
    index3 = find_product_index(comparison['alt2'])
    if -1 in [index1, index2, index3]:
        continue
    compIndexes.append([index1, index2, index3])

with open("data/encoding/comparison-indexes.npy", 'wb') as f:
    np.save(f, np.array(compIndexes))
