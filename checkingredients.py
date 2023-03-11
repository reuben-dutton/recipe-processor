import json
import re
import difflib


parsedIngredientsPath = "parsed-ingredients.json"
colesProductsPath = "data/coles-products.json"

class ProductNotFoundError(Exception):
    pass

with open(parsedIngredientsPath, 'r', encoding="utf-8") as j:
    parsedIngredients = json.load(j)

with open(colesProductsPath, 'r', encoding='utf-8') as j:
    colesProducts = json.load(j)

def find_products(ingredientData, productData):
    ingredient_name = " ".join(ingredientData.get("NAME", []))
    ingredient_variant = " ".join(ingredientData.get("VARIANT", []))
    productMatches = []
    for product in productData:
        if " ".join(product.get('NAME', [])).lower() != ingredient_name.lower():
            continue
        if ingredient_variant.lower() not in " ".join(product.get('VARIANT', [])).lower():
            continue
        productMatches.append(product)
    if productMatches == []:
        raise ProductNotFoundError
    productMatches = sorted(productMatches, key=lambda product: len(product.get("PREP", "")))
    # productMatches = sorted(productMatches, key=lambda product: product["pricePer"])
    return productMatches


if __name__ == "__main__":
    for ingredient in parsedIngredients:
        try:
            matches = find_products(ingredient, colesProducts)
        except ProductNotFoundError:
            print(f"{ingredient['NAME']} - ingredient not found")
            continue
        for match in matches[0:1]:
            print(ingredient['NAME'], ": - ", match['input'].rstrip(), f"({match['pricePer']})")
