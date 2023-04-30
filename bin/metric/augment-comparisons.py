import csv
import sys
import os
import itertools as it

sys.path.append(os.getcwd())

import pandas as pd
import numpy as np


ALT_DENSITY = int(sys.argv[1])
RANDOM_DENSITY = int(sys.argv[2])


# read ingredient->product map
# and the non-map
mapCsvPath = "data/mappings/map.csv"
wrongCsvPath = "data/mappings/wrong.csv"
ingrMap = pd.read_csv(mapCsvPath)
notIngrMap = pd.read_csv(wrongCsvPath)

# read current products
productsCsvPath = "data/tagged-products-full.csv"
products = pd.read_csv(productsCsvPath)

ingrMap = ingrMap.drop_duplicates()
notIngrMap = notIngrMap.drop_duplicates()

uniqueIngredients = pd.unique(ingrMap['ingredient'])

def get_random_product_names(productdf, density):
    randomProducts = productdf.sample(n=min(productdf.shape[0], density))
    return randomProducts[['input']].index


comparison_indexes = []

for ingr in uniqueIngredients:

    # get products that map to the current ingredient
    sameName = ingrMap[ingrMap['ingredient'] == ingr]
    count = sameName.shape[0]

    randDens = (25 - count) * RANDOM_DENSITY

    # get products that map to a different ingredient
    differentName = ingrMap[~(ingrMap['ingredient'] == ingr)]
    
    altDens = (25 - count) * ALT_DENSITY
    differentName = differentName.sample(n=min(differentName.shape[0], altDens))

    # get products that DO NOT map to the current ingredient
    sameNameNotProduct = notIngrMap[notIngrMap['ingredient'] == ingr]

    # remove instances of similiar and almost similiar products
    inverseProducts = products[~products['input'].isin(sameName['product'])]
    inverseProducts = inverseProducts[~inverseProducts['input'].isin(sameNameNotProduct['product'])]

    # # combinations of products that map to the current ingredient
    combs = [comb for comb in it.combinations(sameName[['product']].index, 2)]

    almostSimiliar = sameNameNotProduct[['product']].index
    diffIngredient = differentName[['product']].index

    differentProds = [prod for prod in it.product(combs, diffIngredient)]
    similiarProds = [prod for prod in it.product(combs, almostSimiliar)]
    randomProds = []
    # # similiar product 1, similiar product 2, almost similiar product triplets

    for comb in combs:
        randomProducts = get_random_product_names(inverseProducts, randDens)
        randomProds.extend([prod for prod in it.product([comb], randomProducts)])

    simTriplets = [[prod[0][0], prod[0][1], prod[1]] for prod in similiarProds]
    randTriplets = [[prod[0][0], prod[0][1], prod[1]] for prod in randomProds]
    diffTriplets = [[prod[0][0], prod[0][1], prod[1]] for prod in differentProds]

    comparison_indexes.extend(simTriplets)
    comparison_indexes.extend(randTriplets)
    comparison_indexes.extend(diffTriplets)

with open("data/comparisons/comparison-indexes.npy", 'rb') as f:
    unAugmentedIndexes = np.load(f, allow_pickle=True).astype(np.uint16)

augmentedIndexes = np.concatenate((unAugmentedIndexes, comparison_indexes))

with open("data/comparisons/aug-comparison-indexes.npy", 'wb') as f:
    np.save(f, np.array(augmentedIndexes, dtype=np.uint16)) # unsigned int16, increase as needed
    # np.save(f, np.array(comparison_indexes, dtype=np.uint32)) # unsigned int16, increase as needed

print(augmentedIndexes.shape)
# comparisons.to_csv("data/comparisons/aug-product-comparisons.csv", encoding='utf-8')
        