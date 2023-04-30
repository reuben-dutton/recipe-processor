import pickle
import os
import sys
from decimal import Decimal as Dec

sys.path.append(os.getcwd())

import pandas as pd
import numpy as np

from sklearn.neural_network import MLPRegressor
from training import utils


# change later, these are inaccurate for most ingredients
# 50g each, 1g/ml for all items
conversion = {
              ("kg", None): 20,
              ("kg", "grams"): 1000,
              ("kg", "ml"): 1000,
              ("L", None): 20,
              ("L", "grams"): 1000,
              ("L", "ml"): 1000,
              ("bunch", None): 10,
              ("bunch", "grams"): 500,
              ("bunch", "ml"): 500,
              ("g", None): 0.02,
              ("g", "grams"): 1,
              ("g", "ml"): 1,
              ("mL", None): 0.02,
              ("mL", "grams"): 1,
              ("mL", "ml"): 1,
              ("each", None): 1,
              ("each", "grams"): 50,
              ("each", "ml"): 50,
            }

def get_scale_factor(inputUnit, outputUnit):
    return conversion[(inputUnit, outputUnit)]



def match_ingredient(parsedIngredient, similiarProducts, distances):
    unit = parsedIngredient.UNIT
    if pd.isna(parsedIngredient.QTY):
        amount = 0
    else:
        amount = utils.parseNumbers(parsedIngredient.QTY)
    if pd.isna(unit):
        unit = None
    elif 'tablespoon' in unit:
        unit = 'ml'
        amount *= 20
    elif 'teaspoon' in unit:
        unit = 'ml'
        amount *= 6
    elif 'cup' in unit:
        unit = 'ml'
        amount *= 250
    elif 'stalk' in unit:
        unit = None
    elif 'clove' in unit:
        unit = None
    elif 'stick' in unit:
        unit = None
    elif 'pinch' in unit:
        unit = None

    if (similiarProducts.shape[0] > 0):
        bestMatch = similiarProducts.iloc[0]
    else:
        return (None, None)

    scale = get_scale_factor(bestMatch.productSizeUnits, unit)
    pricePerUnit = Dec(bestMatch.priceTotal) / (Dec(bestMatch.productSize)*Dec(scale))
    ingredientCost = pricePerUnit*amount
    print(parsedIngredient.NAME, amount, unit, pricePerUnit)
    return (bestMatch.input, ingredientCost)




parsedIngredientsPath = "parsed-ingredients.csv"
parsedIngredients = pd.read_csv(parsedIngredientsPath)
parsedIngredients['NAME'] = parsedIngredients['NAME'].apply(utils.normalizeTokens)
parsedIngredients['NAME'] = parsedIngredients['NAME'].apply(lambda s: s.lower())


with open("models/metric/encoding/ingr_preprocess_pipeline.pkl", 'rb') as p:
    ingr_pipeline = pickle.load(p)

with open("models/metric/space-regressor.pkl", 'rb') as p:
    regressor = pickle.load(p)


encodedIngredients = ingr_pipeline.transform(parsedIngredients[['NAME']])

results = regressor.predict(encodedIngredients)


productsDF = pd.read_csv("data/tagged-products-full.csv")

with open("models/metric/product-encoding-nn.pkl", 'rb') as p:
    tree = pickle.load(p)


# query the tree for the 10 closest products to the mapped ingredients
dist, ind = tree.query(results, k=5)

# distance and product index for the 10 closest products for each ingredient
# if the distance is within (x) of the ingredient
close = [[(dist, i) for (dist, i) in zip(dist[n], ind[n]) if dist < 0.2] for n in range(len(results))]

totalCost = 0
# iterate over the closest products
for n, c in enumerate(close):
    # distances as a standalone list
    distances = [item[0] for item in c]
    # indexes as a standalone list
    indexes = [item[1] for item in c]
    # get a dataframe containing only the closest products
    similiarProducts = productsDF.iloc[indexes]

    parsedIngredient = parsedIngredients.iloc[n]
    similiarProducts
    distances

    matchedName, matchedCost = match_ingredient(parsedIngredient, similiarProducts, distances)
    print(matchedName, matchedCost)
    totalCost += (matchedCost, 0)[not matchedCost]

print("---- TOTAL COST ----")
print(totalCost)
print("---- COST PER SERVING ----")
print(totalCost/4)