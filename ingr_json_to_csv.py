import json
import csv


with open("parsed-ingredients.json", 'r') as j:
    data = json.load(j)

column_names = ['QTY', 'UNIT', 'NAME', 
                'COMMENT']

token_column_names = ['QTY', 'UNIT', 'NAME', 
                'COMMENT']

output_path = "parsed-ingredients.csv"

def convert_to_csv_entry(data):
    new_data = data.copy()
    for column_name in token_column_names:
        if column_name.upper() in new_data:
            tokens = new_data.get(column_name.upper(), [])
            joined_tokens = " ".join(tokens)
            del new_data[column_name.upper()]
            new_data[column_name] = joined_tokens
        else:
            new_data[column_name] = ""
    del new_data['prob']
    return new_data
        

with open(output_path, 'w', newline='') as c:
    writer = csv.DictWriter(c, fieldnames=column_names)
    writer.writeheader()
    for product in data:
        writer.writerow(convert_to_csv_entry(product))