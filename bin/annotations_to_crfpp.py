import re
import json
import sys
import os

sys.path.append(os.getcwd())

from training import utils


# needs to be a json file
annotations = json.loads(sys.stdin.readline().rstrip())


def addPrefixes(annotations):
    prevTag = None
    newAnnotations = []
    for token, tag in annotations:
        p = "B" if ((prevTag is None) or (tag != prevTag)) else "I"
        newAnnotations.append((token, "%s-%s" % (p, tag)))
        prevTag = tag
    return newAnnotations


for currentAnnotations in annotations:

    if currentAnnotations == []:
        continue

    output = []
    
    if len(currentAnnotations) == 0:
        continue

    bioAnnotations = addPrefixes(currentAnnotations)
    tokens = [taggedToken[0] for taggedToken in currentAnnotations]

    for i, (token, tag) in enumerate(bioAnnotations):
        features = utils.getFeatures(token, i + 1, tokens)
        output.append(utils.joinLine([utils.singularize(token)] + features + [tag]))
    
    sys.stdout.write("\n".join(output))
    sys.stdout.write("\n\n")
