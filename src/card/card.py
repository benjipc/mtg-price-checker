from dataclasses import dataclass
from enum import Enum
from typing import Optional
import pandas as pd

@dataclass #TODO add requirement for name|(edition_code and card_number)
class Card_Spec:
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
        assert any([self.name, self.edition_code and self.card_number]), "Card_Spec must have either a name or both edition_code and card_number defined."

@dataclass
class Card_Listing:
    card_spec: Card_Spec
    store: str
    price: int
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



def filter_listings(listings: pd.DataFrame, card_spec: Card_Spec) -> pd.DataFrame:
    """
    Filters the listings DataFrame based on the provided Card_Spec.
    """
    filtered_listings = listings.copy()
    if card_spec.name:
        filtered_listings = filtered_listings[filtered_listings['name'].str.lower() == card_spec.name.lower()]

    if card_spec.edition_code and card_spec.edition_code != "NAN":
        filtered_listings = filtered_listings[filtered_listings['edition_code'].str.lower() == card_spec.edition_code.lower()]

    if card_spec.card_number:
        filtered_listings = filtered_listings[filtered_listings['card_number'].str.lower() == card_spec.card_number.lower()]

    if card_spec.finish and card_spec.finish != Card_Spec.Finish.UNSPECIFIED:
        filtered_listings = filtered_listings[filtered_listings['finish'] == card_spec.finish]

    if card_spec.language:
        filtered_listings = filtered_listings[filtered_listings['language'].str.lower() == card_spec.language.lower()]

    

    return filtered_listings.reset_index(drop=True)

