import re
import decimal

from nltk.tokenize import word_tokenize, regexp_tokenize
from nltk.stem import WordNetLemmatizer

wnl = WordNetLemmatizer()

# match any non-whitespace character with  . - \ '  inbetween them
# also match punctuation
token_pattern = r'''(?x)\w+(?:[-\/\.\']\w+)*\.?|[][&.,;"'?():-_`]'''

americanized = {"milliliters": "millilitres",
                "liters": "litres"}

def tokenize(sentence: str):
    return regexp_tokenize(clumpFractions(cleanUnicodeFractions(sentence)), token_pattern)

def normalizeTokens(string: str):
    if not type(string) is str:
        return string
    return " ".join([normalizeToken(token) for token in string.split(" ")])

def normalizeToken(word: str):
    return singularize(unamericanize(word))

def singularize(word: str):
    return wnl.lemmatize(word)

def replace_unit_abbreviations(text: str):
    """
    Replace unit abbreviations with the proper respective measurement.
    """
    text = cleanUnicodeFractions(text)
    text = re.sub(r'(\d+) ?g ', r'\1 grams ', text)
    text = re.sub(r'(\d+) ?kg ', r'\1 kilograms ', text)
    text = re.sub(r'(\d+) ?oz ', r'\1 ounces ', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?l ', r'\1 litres ', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?ml ', r'\1 millilitres ', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?tsp\.?', r'\1 teaspoons', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?tbsp\.?', r'\1 tablespoons', text, flags=re.IGNORECASE)
    return text

def decompose_units(text: str):
    required_units = [
        'cup', 'tablespoon', 'teaspoon', 'gram', 'kilogram', 'millilitre', 'litre'
    ]
    # The following removes slashes following American units and replaces it with a space.
    for unit in required_units:
        text = text.replace(unit + '/', unit + ' ')
        text = text.replace(unit + 's/', unit + 's ')

    # replace '\n' and '\t' with spaces
    text = re.sub(r'(\\n)|(\\t)+', ' ', text)

    return text

def unamericanize(word: str):
    # return the proper spelling if it's incorrectly spelled,
    # otherwise return the original word
    return americanized.get(word, word)

def getFeatures(token, index, tokens):
    """
    Returns a list of features for a given token.
    """
    length = len(tokens)

    return [("I%s" % index), ("L%s" % lengthGroup(length)),
            ("Yes" if isCapitalized(token) else "No") + "CAP",
            ("Yes" if insideParenthesis(token, tokens) else "No") + "PAREN",
            ("Yes" if containsDigits(token) else "No") + "DIGIT"]

def clumpFractions(s):
    """
    Replaces the whitespace between the integer and fractional part of a quantity
    with an underscore, so it's interpreted as a single token. The rest of the
    string is left alone.

        clumpFractions("aaa 1 2/3 bbb")
        # => "aaa 1_2/3 bbb"
    """

    return re.sub(r'(\d+)\s+(\d)/(\d)', r'\1_\2/\3', s)

def unclump(s):
    return re.sub(r'\_', ' ', s)


def cleanUnicodeFractions(s):
    """
    Replace unicode fractions with ascii representation, preceded by a
    space.

    "1\x215e" => "1 7/8"
    """

    fractions = {
        '\x215b': '1/8',
        '\x215c': '3/8',
        '\x215d': '5/8',
        '\x215e': '7/8',
        '\x2159': '1/6',
        '\x215a': '5/6',
        '\x2155': '1/5',
        '\x2156': '2/5',
        '\x2157': '3/5',
        '\x2158': '4/5',
        '\xbc': ' 1/4',
        '\xbe': '3/4',
        '\x2153': '1/3',
        '\x2154': '2/3',
        '\xbd': '1/2',
    }

    for f_unicode, f_ascii in fractions.items():
        s = s.replace(f_unicode, ' ' + f_ascii)

    return s

def joinLine(columns):
    return "\t".join(columns)


def isCapitalized(token):
    """
    Returns true if a given token starts with a capital letter.
    """
    return re.match(r'^[A-Z]', token) is not None


def lengthGroup(actualLength):
    """
    Buckets the length of the ingredient into 6 buckets.
    """
    for n in [4, 8, 12, 16, 20]:
        if actualLength < n:
            return str(n)

    return "X"


def insideParenthesis(token, tokens):
    """
    Returns true if the word is inside parenthesis in the phrase.
    """
    if token in ['(', ')']:
        return True
    else:
        line = " ".join(tokens)
        return re.match(r'.*\(.*' + re.escape(token) + '.*\).*',
                        line) is not None

def containsDigits(token):
    """
    Returns true if the token contains numerals
    """
    return not not re.search(r"\d", token)


def parseNumbers(s):
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