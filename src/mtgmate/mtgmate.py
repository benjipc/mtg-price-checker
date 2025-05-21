import requests
from bs4 import BeautifulSoup
import json
from typing import Optional
import urllib.parse
from card.card import Card_Spec, Card_Listing

class MTGMateAPI:
    BASE_URL = "https://www.mtgmate.com.au"
    SEARCH_SUFFIX = "/cards/search?q="

    @staticmethod
    def get_html(search_url: str, headers: dict[str, str]) -> str:

        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        return response.text

    @staticmethod
    def listings_from_html(
        response_text: str, search_card_name: str
    ) -> Optional[list[Card_Listing]]:
        # def listings_from_html(response_text: str, search_card_spec: Card_Spec) -> Optional[list[Card_Listing]]:
        listings = []

        soup = BeautifulSoup(response_text, "html.parser")
        data_div = soup.find("div", {"data-react-class": "FilterableTable"})
        data_react_props = data_div["data-react-props"]
        props_data = json.loads(data_react_props)
        for card_listing in props_data["uuid"].values():
            card_description = card_listing["name"]
            listing_card_name = card_description.split(" (")[0]

            if listing_card_name == search_card_name:  # search_card_spec
                finish = Card_Spec.Finish.NON_FOIL if card_listing["finish"] == "Nonfoil" else Card_Spec.Finish.FOIL
                listing_card_spec = Card_Spec(
                    name=listing_card_name,
                    edition_code=card_listing["set_code"].upper(),
                    card_number=card_listing["link_path"].split("/")[-1].split(":")[0],
                    finish=finish,
                    language="English",
                )
                card_listing = Card_Listing(
                    card_spec=listing_card_spec,
                    store="MTG Mate",
                    price=int(card_listing["price"]),
                    currency="AUD",
                    price_unit="cents",
                    quantity=card_listing["quantity"],
                    description=card_description,
                    link=MTGMateAPI.BASE_URL + card_listing["link_path"],
                )
                listings.append(card_listing)

        return listings

    @staticmethod
    def search_card(card_name: str) -> Optional[list[Card_Listing]]:
        # Encode the card name for the URL
        encoded_name = urllib.parse.quote(card_name)
        search_url = f"{MTGMateAPI.BASE_URL}{MTGMateAPI.SEARCH_SUFFIX}{encoded_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response_text = MTGMateAPI.get_html(search_url=search_url, headers=headers)
            # Save the HTML response to a file for debugging
            # with open(f'mtgmate_{encoded_name}.html', 'w', encoding='utf-8') as file:
            #     file.write(response_text)
            listings = MTGMateAPI.listings_from_html(
                response_text=response_text, search_card_name=card_name
            )

            return listings

        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"Error searching MTGMate for card {card_name}: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    card_name = "Fury"
    listings = MTGMateAPI.search_card(card_name)
    print(listings)
