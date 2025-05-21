from dataclasses import dataclass
from enum import Enum




@dataclass #TODO add requirement for name|(edition_code and card_number)
class Card_Spec:
    class Finish(Enum):
        FOIL = "foil"
        NON_FOIL = "non-foil"
    name: str
    edition_code: str
    card_number: str
    finish: Finish
    language: str = "English"


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

