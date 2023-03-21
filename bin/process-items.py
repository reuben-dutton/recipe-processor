import sys
import os

sys.path.append(os.getcwd())

from training import utils

# Reads ingredient lines from stdin and outputs text corresponding to:
# - tokens of that line
# - attributes of that line
# - "NoTag" which is a placeholder for the token's ingredient tag

# Example input:
# 250g smoked salmon

# Example output:
# 250   I1  L4  NoCap   NoParen NoTag
# gram  I2  L4  NoCap   NoParen NoTag
# smoked    I3  L4  NoCap   NoParen NoTag
# salmon    I4  L4  NoCap   NoParen NoTag

# This output is compatible with CRF++, but not with CRFSuite
# It is intended for use in tagging/testing, not for training

# Read stdin
raw_ingredient_lines = [x.rstrip() for x in sys.stdin.readlines() if x]

for raw_ingredient_line in raw_ingredient_lines:
    # Format
    formatted_line = utils.replace_unit_abbreviations(raw_ingredient_line)
    # Split into tokens
    tokens = utils.tokenize(formatted_line)

    # Get features for each token and write to stdout
    for i, token in enumerate(tokens):
        features = utils.getFeatures(token, i + 1, tokens)
        sys.stdout.write(utils.joinLine([utils.normalizeToken(token)] + features + ["NoTag"]))
        sys.stdout.write("\n")
    sys.stdout.write("\n")
sys.stdout.flush()