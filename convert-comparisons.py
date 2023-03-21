import csv
import sys
import os

import pandas as pd
import numpy as np

''' Converts triplets in the csv ('name 1', 'name 2', 'name 3')
    to indexes in a numpy array (the indexes corresponding to their
    position in the coles-products.csv file)
'''

comparisonCsvPath = "data/annotations/product-comparisons.csv"
productsCsvPath = "data/coles-products.csv"

comparisons = pd.read_csv(comparisonCsvPath)
products = pd.read_csv(productsCsvPath)

compIndexes = []

def find_product_index(productName):
    ''' Find the indexes of products that have the same name
        as argument productName.
    '''
    sub = products.index[products.input == productName].tolist()
    # if no matches are found, return -1
    if sub == []:
        return -1
    # if matches are found, return the first one
    return sub[0]

for index, comparison in comparisons.iterrows():
    index1 = find_product_index(comparison['product'])
    index2 = find_product_index(comparison['alt1'])
    index3 = find_product_index(comparison['alt2'])
    # if any of the named products do not exist, then discard this
    # comparison (nothing we can do about this)
    if -1 in [index1, index2, index3]:
        continue
    compIndexes.append([index1, index2, index3])

# print how many comparisons there are
print(len(compIndexes))

with open("data/encoding/comparison-indexes.npy", 'wb') as f:
    np.save(f, np.array(compIndexes))
