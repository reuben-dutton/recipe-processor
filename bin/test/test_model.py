import os
import sys
import pickle
import subprocess
from typing import List


sys.path.append(os.getcwd())

import pandas as pd
import numpy as np

from training import utils

INGR_CRF_MODEL="models/crf/ingredients.crf"
parsedIngredientsPath = "parsed-ingredients.csv"


def process_ingredient_list(list_path: str) -> pd.DataFrame:
    parsedIngredients = pd.read_csv(list_path)
    parsedIngredients['NAME'] = parsedIngredients['NAME'].apply(utils.normalizeTokens)
    parsedIngredients['NAME'] = parsedIngredients['NAME'].apply(lambda s: str(s))
    parsedIngredients['NAME'] = parsedIngredients['NAME'].apply(lambda s: s.lower())
    return parsedIngredients

def load_models():
    # Unpickle the ingredient encoding pipeline
    with open("models/metric/encoding/ingr_preprocess_pipeline.pkl", 'rb') as p:
        ingr_pipeline = pickle.load(p)

    # Unpickle the regressive neural network model
    with open("models/metric/space-regressor.pkl", 'rb') as p:
        regressor = pickle.load(p)

    # Retrieve the tagged products list
    productsDF = pd.read_csv("data/tagged-products-full.csv")

    # Unpickle the nearest neighbours model for the product space
    with open("models/metric/product-encoding-nn.pkl", 'rb') as p:
        tree = pickle.load(p)

    return (ingr_pipeline, regressor, productsDF, tree)

# returns the overlap between ingredient name and product name
# the higher proportion of tokens overlap, the higher the result
#
# this is a poor measure but it's the best thing I can think of without manually checking
# multiple tests
def get_product_correctness(ingredient_name: str, product_name: str):
    ingr_tokens = set(utils.normalizeTokens(ingredient_name.lower()).split(" "))
    product_tokens = set(utils.normalizeTokens(product_name.lower()).split(" "))
    return 2 * len(ingr_tokens.intersection(product_tokens)) / (len(ingr_tokens) + len(product_tokens))


# get a representative value of the "correctness" of the product guesses made by
# the model
# ideally, we want values with lower distance to have higher "correctness"
#
# this is INCREDIBLY bad statistics and BAD math
# PLEASE change it whenever possible
def process_vals(vals: List[float]) -> float:
    s = 0
    # if the correctness is greater when distance is lower, then add 1
    for i in range(len(vals) - 1):
        s += (vals[i] >= vals[i+1] - 0.1)
    # average the 1s to obtain a value between 0 and 1
    num_nonzero = len([val for val in vals if val != 0])
    if num_nonzero == 0:
        return 0
    return s / (num_nonzero)

def process_vals_avg(vals: List[float]) -> float:
    num_nonzero = len([val for val in vals if val != 0])
    if num_nonzero == 0:
        return 0
    return (sum(vals) / len(vals)) / (sum([val for val in vals if val != 0]) / num_nonzero)

def test_ingredient_list(list_path: str, models):
    ingr_pipeline, regressor, productsDF, tree = models

    # Retrieve a dataframe containing parsed ingredients (using the CRF models)
    parsedIngredients = process_ingredient_list(list_path)

    # encode the ingredient names using the ingredient encoding pipeline
    encodedIngredients = ingr_pipeline.transform(parsedIngredients[['NAME']])

    # get the positions in the product space for those ingredients
    results = regressor.predict(encodedIngredients)

    num_neighbours = 1

    # query the tree for the 10 closest products to the mapped ingredients
    dist, ind = tree.query(results, k=num_neighbours)

    # distance and product index for the 10 closest products for each ingredient
    # if the distance is within (x) of the ingredient
    close = [[(dist, i) for (dist, i) in zip(dist[n], ind[n]) if dist < 1] for n in range(len(results))]

    evaluation = 0

    # iterate over the closest products
    for n, c in enumerate(close):
        # distances as a standalone list
        distances = [item[0] for item in c]
        # indexes as a standalone list
        indexes = [item[1] for item in c]
        # get a dataframe containing only the closest products
        similiarProducts = productsDF.iloc[indexes]

        ingredient_name = parsedIngredients.iloc[n].NAME
        # print('---- ' + ingredient_name)
        vals = []
        for m in range(len(similiarProducts)):
            productName = similiarProducts.iloc[m].input
            dist = distances[m]
            correctness = get_product_correctness(ingredient_name, productName)
            vals.append(correctness)
            # print(productName, correctness)
        
        # print('---- ' + str(process_vals_avg(vals)))
        evaluation += process_vals_avg(vals)

    return evaluation/len(close)
        




if __name__ == "__main__":
    models = load_models()
    recipes_dir = "data/processed_recipes"
    avg_eval = 0
    for recipe_filename in os.listdir(recipes_dir):
    # for recipe_filename in ['blackforestcake.txt']:
        recipe_path = os.path.join(recipes_dir, recipe_filename)
        val = test_ingredient_list(recipe_path, models)
        avg_eval += val
    print(avg_eval/len(os.listdir(recipes_dir)))

    