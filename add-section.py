import pandas as pd
import numpy as np


productsDF = pd.read_csv("data/tagged-products-full.csv")


marks = [2, 576, 1249, 3114, 3740, 4008, 11216, 12163, 13248, 14910]
marks = [mark - 2 for mark in marks]
names = ["meat-seafood", "fruit-veg", "dairy-eggs-fridge", 
         "bakery", "deli", "pantry", "drinks", "frozen", "liquor"]

sectionData = []
for n in range(len(marks) - 1):
    mark1, mark2 = marks[n:n+2]
    sectionData.extend([names[n] for i in range(mark1, mark2)])

print(len(sectionData))


productsDF['section'] = pd.Series(sectionData, index=productsDF.index)

productsDF.to_csv("data/tagged-products-full.csv", index=False)