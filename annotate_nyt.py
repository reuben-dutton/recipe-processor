import decimal
import re
import json

import pandas as pd

from training import utils

altUnitPattern = r'^(\d+\s+\d\/\d|\d+|\d+\/\d)\s+([A-z]+)(\/ ?| )\(?(\d+\s+\d\/\d|\d+|\d+\/\d)\s+([A-z]+)\)?'

def unclump(s):
    """
    Replaces _'s with spaces. The reverse of clumpFractions.
    """
    return re.sub(r'\_', " ", s)

def _parseNumbers(s):
    """
    Parses a string that represents a number into a decimal data type so that
    we can match the quantity field in the db with the quantity that appears
    in the display name. Rounds the result to 2 places.
    """
    ss = unclump(s)

    m3 = re.match('^\d+$', ss)
    if m3 is not None:
        return decimal.Decimal(round(float(ss), 2))

    m1 = re.match(r'(\d+)\s+(\d)/(\d)', ss)
    if m1 is not None:
        num = int(m1.group(1)) + (float(m1.group(2)) / float(m1.group(3)))
        return decimal.Decimal(str(round(num, 2)))

    m2 = re.match(r'^(\d)/(\d)$', ss)
    if m2 is not None:
        num = float(m2.group(1)) / float(m2.group(2))
        return decimal.Decimal(str(round(num, 2)))

    return None

def _matchUp(token, labels):
    """
    Returns our best guess of the match between the tags and the
    words from the display text.

    This problem is difficult for the following reasons:
        * not all the words in the display name have associated tags
        * the quantity field is stored as a number, but it appears
          as a string in the display name
        * the comment is often a compilation of different comments in
          the display name

    """
    ret = []

    # strip parens from the token, since they often appear in the
    # display_name, but are removed from the comment.
    token = utils.normalizeToken(token)
    decimalToken = _parseNumbers(token)

    # Iterate through the labels in descending order of label importance.
    for label_key in ['name', 'unit', 'qty', 'comment']:
        label_value = labels[label_key]
        if label_value == "":
            continue
        if isinstance(label_value, str):
            for n, vt in enumerate(utils.tokenize(label_value)):
                if utils.normalizeToken(vt) == token:
                    ret.append(label_key.upper())

        elif decimalToken is not None:
            # some decimals are rounded incorrectly compared to the
            # annotated values (e.g. 5/6 -> 0.84 or 0.83)
            # in order to capture these correctly, we need some leeway
            if abs(decimal.Decimal(label_value) - decimalToken) < 0.011:
                ret.append(label_key.upper())

    return ret

def _bestTag(tags):
    if len(tags) == 1:
        return tags[0]
    elif len(tags) > 1:
        for t in tags:
            if t != "COMMENT":
                return t
    return "OTHER"

def _getAltLines(text: str):
    match = re.match(altUnitPattern, text)
    if match:
        americanUnits = match.group(1) + ' ' + match.group(2)
        metricUnits = match.group(4) + ' ' + match.group(5)
        american = re.sub(altUnitPattern, americanUnits, text)
        metric = re.sub(altUnitPattern, metricUnits, text)
        return [american, metric]
    return [text]


if __name__ == "__main__":
    ingredientsCSVPath = "data/nyt-ingredients-snapshot-2015-edited.csv"
    df = pd.read_csv(ingredientsCSVPath)

    df = df.fillna("")

    annotations = []

    for index, row in df.iterrows():

        # get both metric and american ingredient lines (if both units are given)
        altLines = _getAltLines(row.input)

        currentAnnotation = []
        # for the american line, do as normal
        tokens = utils.tokenize(altLines[0])
        for token in tokens:
            annotatedToken = (token, _bestTag(_matchUp(token, row)))
            if token == "self-rising":
                annotatedToken = ("self-raising", "NAME")
            elif token == "plain":
                annotatedToken = ("plain", "NAME")
            currentAnnotation.append(annotatedToken)
        annotations.append(currentAnnotation)
        if len(altLines) > 1:
            currentAnnotation = []
            # do the metric line, but this time the first token is qty and second is unit
            tokens = utils.tokenize(altLines[1])
            for i, token in enumerate(tokens):
                annotatedToken = (token, _bestTag(_matchUp(token, row)))
                if i == 0:
                    annotatedToken = (token, 'QTY')
                if i == 1:
                    annotatedToken = (token, 'UNIT')
                # correcting the Great American Mistake #129204
                if token == "self-rising":
                    annotatedToken = ("self-raising", "NAME")
                # plain is part of the name (flour, yoghurt, etc)
                elif token == "plain":
                    annotatedToken = ("plain", "NAME")
                currentAnnotation.append(annotatedToken)
            annotations.append(currentAnnotation)

    with open("data/annotations/annotated-nyt-ingredient.json", 'w') as j:
        json.dump(annotations, j)