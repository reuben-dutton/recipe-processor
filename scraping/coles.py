from typing import Tuple
import re
import os
import sys
import decimal
import simplejson

import requests
from bs4 import BeautifulSoup

sys.path.append(os.getcwd())

from enums import Ingredient, ProductPricing, ProductUnit



baseurl = "https://www.coles.com.au/browse/"
categories = ['meat-seafood', 'fruit-vegetables', 'dairy-eggs-fridge', 'bakery',
              'deli', 'pantry', 'drinks', 'frozen', 'liquor']

matcheach = r'(per 1ea)'
matchweight = r'(per 1kg)'
# match the '1 each' or 'approx 400g' at the end of product names
matchsize = r'(?<=\| )([\d\.]+ ?[A-z]+)|(?<=\| )((?:approx\.?)? *?(?:[\d\.]+) ?k?g)|(?<=\| )((?:per)? ?k?g)|(?<=\| )([A-z]+)'
matchname = r'.+(?= \|)'
matchvalue = r'(?<=\$)(\d+.\d+)'


class ProductUnavailableError(Exception):
    pass

class SaffronProductError(Exception):
    pass


def parse_product_size(size: str) -> Tuple[decimal.Decimal, ProductUnit]:
    productSizeUnits = ProductUnit("none")
    try:
        amount = decimal.Decimal(re.search(r'(\d+\.?\d+)|(\d+)', size).group(0))
    except:
        amount = 0
        return (amount, productSizeUnits)
    
    if 'pack' in size or 'Pack' in size:
        productSizeUnits = ProductUnit("pack")
    elif 'bunch' in size or 'Bunch' in size:
        productSizeUnits = ProductUnit("bunch")
    elif 'piece' in size or 'Piece' in size:
        productSizeUnits = ProductUnit("piece")
    elif 'each' in size or 'Each' in size:
        productSizeUnits = ProductUnit("each")
    elif 'kg' in size or "Kg" in size:
        productSizeUnits = ProductUnit("kg")
    elif 'g' in size:
        productSizeUnits = ProductUnit("g")
    elif 'ml' in size or 'mL' in size:
        productSizeUnits = ProductUnit("mL")
    elif 'l' in size or 'L' in size:
        productSizeUnits = ProductUnit("L")
    else:
        print(size)
        raise NotImplementedError
    
    return (amount, productSizeUnits)

def parse_product_price(pricetext: str) -> Tuple[decimal.Decimal, ProductPricing]:
    try:
        dollarval = decimal.Decimal(re.search(matchvalue, pricetext).group(0))
    except:
        raise SaffronProductError
    producePricing = ProductPricing("per 1ea")
    if '1ea' in pricetext:
        producePricing = ProductPricing("per 1ea")
    elif '10ea' in pricetext:
        producePricing = ProductPricing("per 10ea")
    elif '100ea' in pricetext:
        producePricing = ProductPricing("per 100ea")
    elif '10kg' in pricetext:
        producePricing = ProductPricing("per 10kg")
    elif '1kg' in pricetext:
        producePricing = ProductPricing("per 1kg")
    elif '100g' in pricetext:
        producePricing = ProductPricing("per 100g")
    elif '10g' in pricetext:
        producePricing = ProductPricing("per 10g")
    elif '1g' in pricetext:
        producePricing = ProductPricing("per 1g")
    elif '1L' in pricetext:
        producePricing = ProductPricing("per 1L")
    elif '100mL' in pricetext:
        producePricing = ProductPricing("per 100mL")
    elif '10mL' in pricetext:
        producePricing = ProductPricing("per 10mL")
    else:
        print(pricetext)
        raise NotImplementedError
    
    return (dollarval, producePricing)


def get_product_image_url(productLink: str) -> str:
    resp = requests.get(f"https://www.coles.com.au{productLink}")
    if not resp.ok:
        raise Exception("Product page not available")
    
    soup = BeautifulSoup(resp.content, features="html.parser")

    productImage = soup.find(attrs={"data-testid": "product-image-0"})
    return productImage['src']


def construct_ingredient(productTile) -> Ingredient:
    producttitle = productTile.find(class_='product__title').text
    try:
        pricingtotaltext = productTile.find(class_='price__value').text
    except:
        # Product is currently unavailable - no price listed
        raise ProductUnavailableError
    priceTotal = decimal.Decimal(re.search(matchvalue, pricingtotaltext).group(0))
    try:
        pricingtext = productTile.find(class_="price__calculation_method").text
    except:
        raise ProductUnavailableError

    if pricingtext == "" or producttitle == "":
        raise ProductUnavailableError

    try:
        productLink = productTile.find(class_="product__link")['href']
        productImageURL = get_product_image_url(productLink)
    except:
        print("image URL unavailable")
        productImageURL = ""


    productnametext = re.search(matchname, producttitle).group(0)
    productsizetext = re.search(matchsize, producttitle, flags=re.IGNORECASE).group(0)

    price, pricing = parse_product_price(pricingtext)
    productSize, productSizeUnits = parse_product_size(productsizetext)
    

    return Ingredient(productnametext.strip(), pricing, price, priceTotal, productSizeUnits, productSize, productImageURL=productImageURL)

def retrieve_page(category: str, pageindex: int = 1):
    ingredientList = []
    finalurl = baseurl + f'{category}?page={pageindex}'
    resp = requests.get(finalurl)

    if not resp.ok:
        raise Exception('Connection failed')

    soup = BeautifulSoup(resp.content, features="html.parser")

    producttiles = soup.find_all(attrs={"data-testid": "product-tile"})

    for producttile in producttiles:
        try:
            ingredientList.append(construct_ingredient(producttile))
        except NotImplementedError:
            print('Not implemented')
            continue
        except ProductUnavailableError:
            continue
        except SaffronProductError:
            continue
        except:
            print('messed up here')

    return ingredientList
    


if __name__ == "__main__":
    allIngredients = []
    for category in categories:
        currPageNum = 1
        newList = retrieve_page(category, currPageNum)
        while len(newList) > 0:
            print(category, currPageNum)
            currPageNum += 1
            allIngredients.extend(newList)
            newList = retrieve_page(category, currPageNum)
            with open('data/products.json', 'w') as j:
                simplejson.dump([ing.serialize() for ing in allIngredients], j, use_decimal=True)
