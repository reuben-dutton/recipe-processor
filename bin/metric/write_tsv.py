import sys
import os

sys.path.append(os.getcwd())

import pandas as pd
import numpy as np

productsDF = pd.read_csv("data/tagged-products-full.csv")

with open("models/metric/encoding/product-space-full.npy", 'rb') as f:
    products_metric = np.load(f, allow_pickle=True)

with open("tsv/data.tsv", 'w') as f1, open("tsv/labels.tsv", 'w') as f2:
    f2.write("\t".join([str(item) for item in productsDF.columns.tolist()]) + '\n')
    for index, row in enumerate(products_metric):
        f1.write("\t".join([str(num) for num in row]) + '\n')
        f2.write("\t".join([str(item) for item in productsDF.iloc[index].tolist()]) + '\n')