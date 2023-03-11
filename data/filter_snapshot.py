import pandas as pd
import re

'''
Filters the nyt ingredients snapshot (removes empty entries, poor annotations,
inspecific ingredient listings and stray HTML markup)
'''

filepath = "nyt-ingredients-snapshot-2015.csv"
editedFilepath = "nyt-ingredients-snapshot-2015-edited.csv"

with open(filepath, 'r', encoding='utf-8') as f:
    df = pd.read_csv(f)


dfSize = df.shape[0]

nullIndexes = df[df['input'].isnull()].index
df = df.drop(nullIndexes)

print(f'Null entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]

nullNameIndexes = df[df['name'].isnull()].index
df = df.drop(nullNameIndexes)

print(f'Null names - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]

# nullQtyIndexes = df[df['qty'] == 0.0].index
# df = df.drop(nullQtyIndexes)

# print(f'Zero quantities - {dfSize - df.shape[0]} removed')
# dfSize = df.shape[0]

orIndexes = df[df['input'].str.contains(" or ")].index
df = df.drop(orIndexes)

print(f'Dual food ("or") entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]

andIndexes = df[df['input'].str.contains(" and ")].index
df = df.drop(andIndexes)

print(f'Dual food ("and") entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]

andorIndexes = df[df['input'].str.contains(" and/or ")].index
df = df.drop(andorIndexes)

print(f'Dual food ("and/or") entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]

hrefIndexes = df[df['input'].str.contains("href")].index
df = df.drop(hrefIndexes)

print(f'Bad HTML entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]


ind = df[df['comment'].isnull()].index

badIndexes = []

for index, row in df.loc[ind].iterrows():
    try:
        unitLength = len(row['unit'])
    except:
        unitLength = 0
    try:
        commentLength = len(row['comment'])
    except:
        commentLength = 0
    try:
        qtyLength = len(str(row['qty']))
    except:
        qtyLength = 0
    try:
        rangeLength = len(str(row['range_end']))
    except:
        rangeLength = 0
    if "of" in row['input'] or "to" in row['input']:
        if len(row['input']) > len(row['name']) + unitLength + commentLength + qtyLength + rangeLength + 6:
            # print(row)
            badIndexes.append(index)
    else:
        if len(row['input']) > len(row['name']) + unitLength + commentLength + qtyLength + rangeLength + 3:
            # print(row)
            badIndexes.append(index)

df = df.drop(badIndexes)

print(f'Dual measurement / incorrect comment entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]

incorrectNameIndexes = df[df['name'].str.contains(",")].index
df = df.drop(incorrectNameIndexes)
incorrectNameIndexes = df[df['name'].str.contains("\(")].index
df = df.drop(incorrectNameIndexes)
incorrectNameIndexes = df[df['name'].str.contains("\)")].index
df = df.drop(incorrectNameIndexes)

print(f'"Comment included in name" entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]


badIndexes = []

for index, row in df.iterrows():
    match = re.search(r'(\d+)', row['input'])
    if match and row['qty'] == 0:
        badIndexes.append(index)

df = df.drop(badIndexes)

print(f'"Qty included in comment" entries - {dfSize - df.shape[0]} removed')
dfSize = df.shape[0]




print(f"Total # entries: {dfSize}")


df.to_csv(editedFilepath, index=False)