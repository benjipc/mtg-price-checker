import requests
from typing import Optional

class ScryfallAPI:
    BASE_URL = "https://api.scryfall.com"
    
    

    @staticmethod
    def search_card(card_name: str) -> Optional[dict]:
        """
        Search for a card by name using Scryfall API
        """
        endpoint = f"{ScryfallAPI.BASE_URL}/cards/named"
        params = {"fuzzy": card_name}
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error searching for card: {e}")
            return None