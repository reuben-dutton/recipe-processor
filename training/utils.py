import re

from nltk.tokenize import word_tokenize, regexp_tokenize
import inflect

p = inflect.engine()

# match any non-whitespace character with  . - \ '  inbetween them
# also match punctuation
token_pattern = r'''(?x)\w+(?:[-\/\.\']\w+)*\.?|[][&.,;"'?():-_`]'''

def tokenize(sentence: str):
    return regexp_tokenize(clumpFractions(cleanUnicodeFractions(sentence)), token_pattern)

# used for ingredients, not products (Brand names will be incorrectly singularized)
def singularize(word: str):
    if word.endswith("'s"):
        return word
    if not p.singular_noun(word):
        return word
    return p.singular_noun(word)

def replace_unit_abbreviations(text: str):
    """
    Replace unit abbreviations with the proper respective measurement.
    """
    text = re.sub(r'(\d+) ?g ', r'\1 grams ', text)
    text = re.sub(r'(\d+) ?oz ', r'\1 ounces ', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?l ', r'\1 litres ', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?ml ', r'\1 millilitres ', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?tsp\.?', r'\1 teaspoons', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+) ?tbsp\.?', r'\1 tablespoons', text, flags=re.IGNORECASE)
    return text

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