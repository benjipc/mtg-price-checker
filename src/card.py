from dataclasses import dataclass
from enum import Enum
from typing import Optional
import pandas as pd

@dataclass(frozen=True) #TODO add requirement for name|(edition_code and card_number)
class CardSpec:
    class Finish(Enum):
        FOIL = "foil"
        NON_FOIL = "non-foil"
        UNSPECIFIED = "unspecified"

    name: Optional[str] = None
    edition_code: Optional[str] = None
    card_number: Optional[str] = None
    finish: Optional[Finish] = Finish.UNSPECIFIED
    language: Optional[str] = "English"

    def __post_init__(self):
        assert any([self.name, self.edition_code and self.card_number]), "CardSpec must have either a name or both edition_code and card_number defined."

@dataclass(frozen=True)
class VendorListing:
    card_spec: CardSpec
    store: str
    price: float
    price_unit: str
    currency: str
    quantity: int
    description: str
    link: str

    def to_dataframe(self) -> pd.DataFrame: #TODO have the function refernce the class variables iteratively instead of hardcoding them
        return pd.DataFrame({
            "name": [self.card_spec.name],
            "edition_code": [self.card_spec.edition_code],
            "card_number": [self.card_spec.card_number],
            "finish": [self.card_spec.finish],
            "language": [self.card_spec.language],
            "store": [self.store],
            "price": [self.price],
            "price_unit": [self.price_unit],
            "currency": [self.currency],
            "quantity": [self.quantity],
            "description": [self.description],
            "link": [self.link]
        })

