import csv
import sys
import os
import itertools as it
import random
import math

sys.path.append(os.getcwd())

import pandas as pd
import numpy as np

# read ingredient->product map
# and the non-map
mapCsvPath = "data/mappings/map.csv"
wrongCsvPath = "data/mappings/wrong.csv"
ingrMap = pd.read_csv(mapCsvPath)
notIngrMap = pd.read_csv(wrongCsvPath)

# read current comparisons and products
comparisonCsvPath = "data/comparisons/product-comparisons.csv"
productsCsvPath = "data/tagged-products-full.csv"
comparisons = pd.read_csv(comparisonCsvPath)
products = pd.read_csv(productsCsvPath)

ingrMap = ingrMap.drop_duplicates()
notIngrMap = notIngrMap.drop_duplicates()

uniqueIngredients = pd.unique(ingrMap['ingredient'])

POSITIVE_PER = 0.5 # should range from 0.1 to 0.5
NEGATIVE_PER = 0.2 # should range from 0.05 to 0.2
SECTION_ADDITIONS = 100 # should range from 10 to 320

POSITIVE_PER = float(sys.argv[1])
NEGATIVE_PER = float(sys.argv[2])
SECTION_ADDITIONS = int(sys.argv[3])

def sampleGenerator(gen, frac=None, n=None):
    if frac == None and n == None:
        raise ValueError("One of frac or n must be specified")
    if frac != None and n != None:
        raise ValueError("Only one of frac or n should be specified")
    if frac != None and type(frac) is not float:
        raise TypeError("frac must be of type float, not {}".format(type(frac)))
    if n != None and type(n) is not int:
        raise TypeError("n must be of type int, not {}".format(type(n)))
    if n != None and not n >= 0:
        raise ValueError("n must be greater than 0")
    if frac != None and not frac >= 0.0 and not frac <= 1.0:
        raise ValueError("frac must be between 0.0 and 1.0")
        
    genList = list(gen)
    if frac != None:
        n = math.floor(frac*len(genList))
    return random.sample(genList, k=min(n, len(genList)))


# # do something with the current ingredient name and available data
# def example(ingredient_name, data):
#     products, ingrMap, notIngrMap = data
#     # do something
#     return triplets
# # return triplet comparisons for that ingredient

def sameIngredient(ingredient_name, data):
    products, ingrMap, notIngrMap = data
    # get indexes for entries where the ingredient name matches
    sameIngredientIndexes = ingrMap['ingredient'] == ingredient_name
    # get ingredient->product mappings where the ingredient matches
    sameIngrProducts = ingrMap[sameIngredientIndexes]
    # get ingredient->product mappings where the ingredient doesn't match
    notSameIngrProducts = ingrMap[~sameIngredientIndexes]

    # get all possible pairs of product names that are the same ingredient
    # get the indexes, not the names
    combsIt = it.combinations(sameIngrProducts[['product']].index, 2)
    combs = sampleGenerator(combsIt, frac=POSITIVE_PER)

    # get triplets where we have:
    # index 0, index 1 = product indexes which map to the same ingredient
    # index 2 = product index which do not map to the same ingredient
    prodsIt = it.product(combs, notSameIngrProducts[['product']].index)
    prods = sampleGenerator(prodsIt, frac=NEGATIVE_PER)

    # reformat to triplets
    triplets = [[prod[0][0], prod[0][1], prod[1]] for prod in prods]

    return triplets

def sameIngredientBroad(ingredient_name, data):
    products, ingrMap, notIngrMap = data

    # get unique ingredient names
    ingrNames = pd.unique(ingrMap['ingredient'])
    sameBroadIngredientNames = []
    split_ingredient_name = ingredient_name.split(" ")
    # for each unique ingredient name
    for ingrName in ingrNames:
        # get the set of tokens that exist in the given ingredient_name and the 
        # current ingrName
        splitIngrName = ingrName.split(" ")
        if splitIngrName[-2:] == split_ingredient_name[-2:]:
            sameBroadIngredientNames.append(ingrName)
        elif splitIngrName[-1] == split_ingredient_name[-1]:
            if splitIngrName[-1] not in ["powder", "egg", "eggs", "slices"]:
                sameBroadIngredientNames.append(ingrName)
        elif len(splitIngrName) >= 3 and len(split_ingredient_name) >= 3 and splitIngrName[-2] == split_ingredient_name[-2]:
            if splitIngrName[-2] not in []:
                sameBroadIngredientNames.append(ingrName)
        elif splitIngrName[0] == split_ingredient_name[0]:
            if splitIngrName[0] not in ["black", "red", "white", "green", "yellow", "sweet", "plain", "sliced"]:
                sameBroadIngredientNames.append(ingrName)
    
    # get indexes for entries where the ingredient name matches
    sameIngredientIndexes = ingrMap['ingredient'].isin(sameBroadIngredientNames)
    # get ingredient->product mappings where the ingredient matches
    sameIngrProducts = ingrMap[sameIngredientIndexes]
    # get ingredient->product mappings where the ingredient doesn't match
    notSameIngrProducts = ingrMap[~sameIngredientIndexes]

    # get all possible pairs of product names that are the same ingredient
    # get the indexes, not the names
    combsIt = it.combinations(sameIngrProducts[['product']].index, 2)
    combs = sampleGenerator(combsIt, frac=POSITIVE_PER)

    # get triplets where we have:
    # index 0, index 1 = product indexes which map to the same ingredient
    # index 2 = product index which do not map to the same ingredient
    prodsIt = it.product(combs, notSameIngrProducts[['product']].index)
    prods = sampleGenerator(prodsIt, frac=NEGATIVE_PER)

    # reformat to triplets
    triplets = [[prod[0][0], prod[0][1], prod[1]] for prod in prods]

    return triplets

def notSameIngredient(ingredient_name, data):
    products, ingrMap, notIngrMap = data
    # get indexes for entries where the ingredient name matches
    sameIngredientIndexes = ingrMap['ingredient'] == ingredient_name
    sameIngredientIndexesNot = notIngrMap['ingredient'] == ingredient_name
    # get ingredient->product mappings where the ingredient matches
    sameIngrProducts = ingrMap[sameIngredientIndexes]
    # get ingredient->product mappings where the ingredient doesn't match
    sameIngredientNotProducts = notIngrMap[sameIngredientIndexesNot]

    # get all possible pairs of product names that are the same ingredient
    # get the indexes, not the names
    combsIt = it.combinations(sameIngrProducts[['product']].index, 2)
    combs = sampleGenerator(combsIt, frac=POSITIVE_PER)

    # get triplets where we have:
    # index 0, index 1 = product indexes which map to the same ingredient
    # index 2 = product index which do not map to the same ingredient
    prodsIt = it.product(combs, sameIngredientNotProducts[['product']].index)
    prods = sampleGenerator(prodsIt, frac=NEGATIVE_PER)

    # reformat to triplets
    triplets = [[prod[0][0], prod[0][1], prod[1]] for prod in prods]

    return triplets



def sameSection(data):
    products, ingrMap, notIngrMap = data

    prods = []
    
    sectionNames = pd.unique(products["section"])
    for sectionName in sectionNames:
        sameSectionIndexes = products['section'] == sectionName
        # get ingredient->product mappings where the ingredient matches
        sameSectionProducts = products[sameSectionIndexes]
        # get ingredient->product mappings where the ingredient doesn't match
        diffSectionProducts = products[~sameSectionIndexes]
        
        prodInd = list(sameSectionProducts[['input']].index)
        diffInd = list(diffSectionProducts[['input']].index)

        for i in range(SECTION_ADDITIONS):
            # match up random shufflings of products
            currentProds = zip(random.sample(prodInd, k=len(prodInd)), 
                            random.sample(prodInd, k=len(prodInd)),
                            random.sample(diffInd, k=len(prodInd)))
            prods.extend(currentProds)

    # reformat to triplets
    triplets = prods

    return triplets




comparison_indexes = []
data = (products, ingrMap, notIngrMap)

for ingr in uniqueIngredients:
    comparison_indexes.extend(sameIngredient(ingr, data))
    comparison_indexes.extend(sameIngredientBroad(ingr, data))
    comparison_indexes.extend(notSameIngredient(ingr, data))

comparison_indexes.extend(sameSection(data))


with open("data/comparisons/comparison-indexes.npy", 'rb') as f:
    unAugmentedIndexes = np.load(f, allow_pickle=True).astype(np.uint16)

augmentedIndexes = np.concatenate((unAugmentedIndexes, comparison_indexes))

with open("data/comparisons/aug-comparison-indexes.npy", 'wb') as f:
    np.save(f, np.array(augmentedIndexes, dtype=np.uint16)) # unsigned int16, increase as needed
    # np.save(f, np.array(comparison_indexes, dtype=np.uint32)) # unsigned int16, increase as needed

print(augmentedIndexes.shape)
