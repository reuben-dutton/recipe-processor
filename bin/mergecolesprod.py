import json
import os
import sys
import argparse

sys.path.append(os.getcwd())


def main(args):

    with open(args.product_file, 'r', encoding='utf-8') as j:
        prices = json.load(j)

    tokens = json.loads(sys.stdin.readline().rstrip())

    newData = []

    for i, item in enumerate(prices):
        priceDict = item.copy()
        tokenDict = tokens[i].copy()

        newDict = dict(priceDict, **tokenDict)
        newDict['input'] = newDict['name']
        del newDict['name']
        newData.append(newDict)
        
    sys.stdout.write(json.dumps(newData))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Ingredient Phrase Tagger',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--product-file', required=True)
    main(parser.parse_args())

