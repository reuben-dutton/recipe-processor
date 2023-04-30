import json
import sys
import os

sys.path.append(os.getcwd())

data = json.loads(sys.stdin.readline().rstrip())

for product in data:
    sys.stdout.write(product['name'])
    sys.stdout.write("\n")