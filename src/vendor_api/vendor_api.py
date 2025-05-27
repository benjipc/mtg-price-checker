from abc import ABC, abstractmethod
from typing import Optional, List
from card.card import Card_Listing

class VendorAPI(ABC):

    @staticmethod
    @abstractmethod
    def search_card(card_name: str) -> Optional[List[Card_Listing]]:
        ...

