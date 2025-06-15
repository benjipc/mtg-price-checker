from abc import ABC, abstractmethod
from typing import Optional, List, Callable, Protocol

from card import CardSpec, VendorListing

VendorListingsT = Optional[List[VendorListing]]
FilterFnT = Callable[[CardSpec, CardSpec], bool]

# def filter_fn_none(card_spec: CardSpec, listing: CardSpec) -> bool:
#     """
#     Default filter function that returns True for all listings.
#     This can be used when no specific filtering is required.
#     """
#     return True

def filter_fn_default(spec: CardSpec, listing: CardSpec) -> bool:
    """
    Default filter function that checks if the listing matches the card specification.
    This can be used when a basic match is required.
    """

    name_good = not spec.name or listing.name.lower() == spec.name.lower()
    
    edition_good = not spec.edition_code or spec.edition_code.lower() == "nan" or listing.edition_code.lower() == spec.edition_code.lower()

    sets_without_card_numbers = ['LEA', 'LEB', '2ED', '3ED', '4ED', '5ED', 'ARN', 'ATQ', 'LEG', 'DRK', 'FEM', 'ICE', 'HML', 'ALL', 'MIR', 'VIS', 'WTH', 'TMP', 'STH']
    card_number_good = not spec.card_number or listing.card_number == spec.card_number or spec.edition_code.upper() in sets_without_card_numbers

    finish_good = not spec.finish or spec.finish == CardSpec.Finish.UNSPECIFIED or listing.finish == spec.finish
    language_good = not spec.language or listing.language.lower() == spec.language.lower()
    # print(name_good, edition_good, card_number_good, finish_good, language_good)
    return (
        name_good and
        edition_good and
        card_number_good and
        finish_good and
        language_good
    )

class VendorAPI(ABC):
    @property
    def name(self):
        return self.__class__.__name__

    @staticmethod
    @abstractmethod
    def search_card_name(card_name: str) -> VendorListingsT:
        ...

    @classmethod
    def filtered_listings(cls, card_spec: CardSpec, filter_fn: FilterFnT = filter_fn_default) -> VendorListingsT:
        unfiltered_listings = cls.search_card_name(card_spec.name)
        if unfiltered_listings is None:
            return None
        return [
            listing for listing in unfiltered_listings
            if filter_fn(card_spec, listing.card_spec)
        ]


# class VendorAPI_P(Protocol):
#     @property
#     def name(self) -> str:
#         ...

#     @staticmethod
#     def search_card_name(card_name: str) -> VendorListingsT:
#         ...
