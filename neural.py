import pickle

import pandas as pd
import numpy as np

from sklearn.neural_network import MLPRegressor

from training.metrics import pipelines


ingredientsDF = pd.read_csv("parsed-ingredients.csv")

with open("data/encoding/neural_train.npy", 'rb') as f:
    y_train = np.load(f, allow_pickle=True)

ingr_pipeline = pipelines.get_ingr_pipeline()

x_train = ingr_pipeline.fit_transform(ingredientsDF)

regressor = MLPRegressor()

regressor.fit(x_train, y_train)

results = regressor.predict(x_train)


productsDF = pd.read_csv("data/coles-products.csv")

with open("models/product-space-full.pkl", 'rb') as p:
    tree = pickle.load(p)

dist, ind = tree.query(results, k=3)
close = [[i for (dist, i) in zip(dist[n], ind[n]) if dist < 0.03] for n in range(len(results))]
for i, c in enumerate(close):
    # productsDF.loc[ind[i], "dist"] = dist[i]
    similiarProducts = productsDF.iloc[c]
    print(" ---- ", ingredientsDF.iloc[i].NAME, ' ---- ')
    for n in range(len(similiarProducts)):
        print(similiarProducts.iloc[n].input)
    print("------------------")