import re
import json
import sys
import os



crfLines = [x.rstrip() for x in sys.stdin.readlines()]

unigramLocs = [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (0, 3), (0, 5),
            (-2, 4), (-1, 4), (0, 4), (1, 4), (2, 4)]

bigramLocs = [((0, 0), (0, 2)), ((0, 1), (0, 2)),
           ((0, 0), (0, 3)), ((0, 0), (0, 4)), 
           ((0, 0), (0, 1)), ((0, 0), (0, 5))]

def getUnigram(seriesArray, tokenIndex, unigramLoc):
    if tokenIndex + unigramLoc[0] < 0:
        return None
    try:
        return seriesArray[tokenIndex+unigramLoc[0]][unigramLoc[1]]
    except:
        return None

seriesData = []
seriesArr = []

for line in crfLines:
    if line.strip() == "":
        seriesData.append(seriesArr)
        seriesArr = []
        continue
    seriesArr.append(line.strip().split("\t"))


for seriesArray in seriesData:
    for tokenIndex, tokenArray in enumerate(seriesArray):
        output = [tokenArray[-1]]
        for unigramLoc in unigramLocs:
            unigram = getUnigram(seriesArray, tokenIndex, unigramLoc)
            if unigram:
                output.append(f"{str(unigramLoc)}={unigram}")
        for bigramLoc in bigramLocs:
            bigramA = getUnigram(seriesArray, tokenIndex, bigramLoc[0])
            bigramB = getUnigram(seriesArray, tokenIndex, bigramLoc[1])
            if bigramA and bigramB:
                output.append(f"{str(bigramLoc[0])}|{str(bigramLoc[1])}={bigramA}|{bigramB}")
    
        if tokenIndex == 0:
            output.append("__BOS__")
        elif tokenIndex == len(seriesArray) - 1:
            output.append("__EOS__")

        sys.stdout.write("\t".join(output))
        sys.stdout.write("\n")
    sys.stdout.write("\n")
sys.stdout.flush()