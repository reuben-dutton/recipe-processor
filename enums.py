from dataclasses import dataclass
from typing import Dict
from enum import Enum


class ProductPricing(Enum):
    EACH = "per 1ea"
    EACHX = "per 10ea"
    EACHXX = "per 100ea"
    PERKGX = "per 10kg"
    PERKG = "per 1kg"
    PERGXX = "per 100g"
    PERGX = "per 10g"
    PERG = "per 1g"
    PERL = "per 1L"
    PERMLXX = "per 100mL"
    PERMLX = "per 10mL"
    PERML = "per 1mL"
    

class ProductUnit(Enum):
    NONE = "none"
    EACH = "each"
    PACK = "pack"
    PIECE = "piece"
    BUNCH = "bunch"
    GRAMS = "g"
    KILOGRAMS = "kg"
    MILLILITRES = "mL"
    LITRES = "L"


@dataclass
class Ingredient:
    name: str
    pricingPer: ProductPricing
    pricePer: float
    priceTotal: float
    productSizeUnits: ProductUnit
    productSize: float
    productImageURL: str = ""

    def serialize(self):
        return {'name': self.name,
                'pricingPer': self.pricingPer.value,
                'pricePer': self.pricePer,
                'priceTotal': self.priceTotal,
                'productSizeUnits': self.productSizeUnits.value,
                'productSize': self.productSize,
                'productImageURL': self.productImageURL}
    
    @staticmethod
    def _fromJson(data: Dict):
        return Ingredient(data['name'], data['pricingPer'], data['pricePer'],
            data['priceTotal'], data['productSizeUnits'], data['productSize'])
        

