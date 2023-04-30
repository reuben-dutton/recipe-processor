import json
import csv
import sys

import pandas as pd

if len(sys.argv) > 2:
    ingredient_name, search_name = sys.argv[1], sys.argv[2]
else:
    ingredient_name, search_name = sys.argv[1], sys.argv[1]


ingredientsDF = pd.read_csv("data/nyt-ingredients-snapshot-2015-filtered.csv")
productsDF = pd.read_csv("data/tagged-products-full.csv")

ingredientsDF['name'].fillna("")
ingredientsDF['lowername'] = ingredientsDF['name'].str.lower()
productsDF['lowerinput'] = productsDF['input'].str.lower()
productsDF['lowername'] = productsDF['name'].str.lower()

with open("data/mappings/map.csv", 'a', newline='') as c1, open("data/mappings/wrong.csv", 'a', newline='') as c2:
    mapwriter = csv.DictWriter(c1, fieldnames=['ingredient', 'product'])
    wrongwriter = csv.DictWriter(c2, fieldnames=['ingredient', 'product'])

    # ingredient_name = "bastard" # fettuccine
    # search_name = "bastard"

    print(ingredient_name)
    containedInInput = productsDF.loc[productsDF['lowerinput'].str.contains(search_name)]
    # containedInNameAndInput = containedInInput.loc[containedInInput['lowername'].isin(ingredient_name.split(" "))]
    # containedInNameAndInput = productsDF.loc[productsDF['lowername'].isin(ingredient_name.split(" "))]
    containedInNameAndInput = containedInInput

    print(containedInNameAndInput.shape)

    if containedInNameAndInput.shape[0] == 0:
        print('no match found')
        print(" ----------------------------- ")
    for i, row in containedInNameAndInput.iterrows():
        product_name = row['input']
        print(i, product_name)
        print(" ----------------------------- ")
        if input("match?: \n") == "y":
            print(ingredient_name)
            mapwriter.writerow({'ingredient': ingredient_name, 'product': product_name})
        else:
            print("no match")
            wrongwriter.writerow({'ingredient': ingredient_name, 'product': product_name})
        print(" ----------------------------- ")