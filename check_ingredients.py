import json
import pickle

import pandas as pd
import numpy as np


with open("map.json", 'r') as j:
    foodMap = json.load(j)

with open("parsed-ingredients.json", 'r') as j:
    parsedIngredients = json.load(j)

productsCSVPath = "data/coles-products.csv"
productsDF = pd.read_csv(productsCSVPath)


def get_ingr_name(parsedIngredient: dict):
    return " ".join(parsedIngredient.get('NAME', []))

def get_ingr_product_equiv(parsedIngredient: dict):
    ingr_name = get_ingr_name(parsedIngredient)
    return foodMap.get(ingr_name, None)


indexes = []

for item in parsedIngredients:
    productEquiv = get_ingr_product_equiv(item)
    thing = productsDF.loc[productsDF['input'] == productEquiv].index[0]
    indexes.append(thing)

print(indexes)

with open("data/encoding/products-metric.npy", 'rb') as f:
    products_metric = np.load(f, allow_pickle=True)

targets = products_metric[indexes]

print(targets)

with open("data/encoding/neural_train.npy", 'wb') as f:
    np.save(f, np.array(targets))
