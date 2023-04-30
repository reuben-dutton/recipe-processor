import json
import csv
import os
import sys
import argparse

sys.path.append(os.getcwd())

column_names = ['QTY', 'UNIT', 'NAME', 
                'COMMENT']

token_column_names = ['QTY', 'UNIT', 'NAME', 
                'COMMENT']


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


def main(args):
    data = json.loads(sys.stdin.readline().rstrip())
    with open(args.output_file, 'w', newline='') as c:
        writer = csv.DictWriter(c, fieldnames=column_names)
        writer.writeheader()
        for product in data:
            writer.writerow(convert_to_csv_entry(product))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Ingredient Phrase Tagger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-o', '--output-file', required=True)
    main(parser.parse_args())