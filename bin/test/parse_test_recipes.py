import os
import sys
import pickle
import subprocess

sys.path.append(os.getcwd())

import pandas as pd


from training import utils


INGR_CRF_MODEL="models/crf/ingredients.crf"
parsedIngredientsPath = "parsed-ingredients.csv"


def process_ingredient_list(list_path: str) -> pd.DataFrame:
    subprocess.run("bin/parse-ingredients {} {} {}".format(INGR_CRF_MODEL, list_path, parsedIngredientsPath), shell=True)
    parsedIngredients = pd.read_csv(parsedIngredientsPath)
    return parsedIngredients


if __name__ == "__main__":
    recipes_dir = "data/recipes"
    for recipe_filename in os.listdir(recipes_dir):
    # for recipe_filename in ['blackforestcake.txt']:
        recipe_path = os.path.join(recipes_dir, recipe_filename)
        parsedIngredients = process_ingredient_list(recipe_path)
        parsedIngredients.to_csv(os.path.join("data/processed_recipes", recipe_filename.replace(".txt", ".csv")), index=False)