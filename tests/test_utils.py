import unittest
import os
import sys

sys.path.append(os.getcwd())

from training import utils

class UtilsTest(unittest.TestCase):
    
    def test_replace_unit_abbreviations(self):
        # replaces g abbreviation
        self.assertEqual(utils.replace_unit_abbreviations("5g flour"), "5 grams flour")
        # works with 0s
        self.assertEqual(utils.replace_unit_abbreviations("10g flour"), "10 grams flour")
        self.assertEqual(utils.replace_unit_abbreviations("0g flour"), "0 grams flour")

        # replaces teaspoons
        self.assertEqual(utils.replace_unit_abbreviations("20tsp. flour"), "20 teaspoons flour")
        # different conditions
        self.assertEqual(utils.replace_unit_abbreviations("20 Tsp flour"), "20 teaspoons flour")

        # replaces millilitres
        self.assertEqual(utils.replace_unit_abbreviations("20mL flour"), "20 millilitres flour")
        self.assertEqual(utils.replace_unit_abbreviations("20 ml flour"), "20 millilitres flour")

        # replaces litres
        self.assertEqual(utils.replace_unit_abbreviations("1L flour"), "1 litres flour")
        self.assertEqual(utils.replace_unit_abbreviations("1.1 l flour"), "1.1 litres flour")

        # replaces ounces
        self.assertEqual(utils.replace_unit_abbreviations("20oz flour"), "20 ounces flour")
        self.assertEqual(utils.replace_unit_abbreviations("12 oz flour"), "12 ounces flour")

    def test_singularize(self):
        words = ["cups", "bulbs", "teaspoons", "ounces", "litres", "milligrams"]
        singles = ['cup', 'bulb', 'teaspoon', 'ounce', 'litre', 'milligram']
        for i in range(len(words)):
            self.assertEqual(utils.singularize(words[i]), singles[i])

