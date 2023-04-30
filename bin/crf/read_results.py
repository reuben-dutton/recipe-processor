import sys
import os
import json
import re
import argparse

sys.path.append(os.getcwd())

from training import utils


def main(args):
    lines = [x.rstrip() for x in sys.stdin.readlines() if x]

    tag_data = []

    ingredient = {}
    ingredient['tags'] = []

    for line in lines:
        if line == "":
            tag_data.append(ingredient)
            ingredient = {}
            ingredient['tags'] = []
            continue

        if line[0:2] == "@s":
            continue
        elif line[0:2] == "@p":
            ingredient['prob'] = float(re.search(r"[\d\.]+", line).group(0))
        else:
            ingredient['tags'].append(line)

    with open(args.ingredient_file, 'r', encoding="utf-8") as f:
        raw_ingredient_lines = f.readlines()


    ingredient_data = []

    for i, raw_ingredient_line in enumerate(raw_ingredient_lines):
        # Format
        formatted_line = utils.replace_unit_abbreviations(raw_ingredient_line)
        # Split into tokens
        tokens = utils.tokenize(formatted_line)

        ingredient_data.append({"prob": tag_data[i]['prob']})

        for j, tag in enumerate(tag_data[i]['tags']):
            
            # tags are in the form B-TAGNAME or I-TAGNAME
            tag_name = tag[2:]
            if tag_name == "OTHER":
                continue

            ### if each entry is to be a single string
            # if tag.startswith("B"):
            #     if not ingredient_data[i].get(tag_name, None):
            #         ingredient_data[i][tag_name] = tokens[j]
            #     else:
            #         ingredient_data[i][tag_name] += ", " + tokens[j]
            # elif tag.startswith("I"):
            #     if not ingredient_data[i].get(tag_name, None):
            #         ingredient_data[i][tag_name] = tokens[j]
            #     else:
            #         ingredient_data[i][tag_name] += " " + tokens[j]

            ## if each entry is an array of tokens
            if not ingredient_data[i].get(tag_name, None):
                ingredient_data[i][tag_name] = [tokens[j]]
            else:
                ingredient_data[i][tag_name].append(tokens[j])
    
    sys.stdout.write(json.dumps(ingredient_data))
    sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Ingredient Phrase Tagger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--ingredient-file', required=True)
    main(parser.parse_args())