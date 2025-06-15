from typing import Optional, List
import string
import urllib.parse
from card import CardSpec, VendorListing
from vendor_api import VendorAPI
from binderpos_api import BinderPosAPI as bpAPI

class GamesDistrictAPI(VendorAPI):
    STORE_URL = "b48eb9-4f.myshopify.com"
    ORIGIN_URL = "https://thegamesdistrict.com"
    REFERER_URL = "https://thegamesdistrict.com/"

    @staticmethod
    def _fetch_search_data(card_name: str):
        api = bpAPI(
            store_url=GamesDistrictAPI.STORE_URL,
            origin=GamesDistrictAPI.ORIGIN_URL,
            referer=GamesDistrictAPI.REFERER_URL
        )
        response = api.extract_in_stock_variants(api.search_cards(card_name))
        return response

    @staticmethod
    def search_card_name(card_name: str) -> Optional[List[VendorListing]]:#TODO think about where it needs to be async
        search_response = GamesDistrictAPI._fetch_search_data(card_name)
        # print(search_response)
        listings = []
        for card_listing in search_response:
            card_description = f"{card_listing['name']} {card_listing['sku']}"
            if card_name == card_listing['name']:
                punct_to_remove = string.punctuation.replace('-', '')
                trans_table = str.maketrans('', '', punct_to_remove)
                url_suffix = card_listing['title'].translate(trans_table).replace(' ', '-')
                listing_card_spec = CardSpec(
                    name=card_listing['name'],
                    edition_code=card_listing['set-code'].upper(),
                    card_number=card_listing['card-number'],
                    finish=CardSpec.Finish.NON_FOIL if card_listing['foiling'] == 'non-foil' else CardSpec.Finish.FOIL,
                    language="English" if card_listing['language'] == 'English' else "Non English",
                )
                card_listing = VendorListing(
                    card_spec=listing_card_spec,
                    store="Games District",
                    price=float(card_listing['price']),
                    currency="AUD",
                    price_unit="AUD",
                    quantity=card_listing['quantity'],
                    description=card_description,
                    link=f"{GamesDistrictAPI.ORIGIN_URL}/products/{urllib.parse.quote(url_suffix)}?variant={card_listing['variant_id']}"
                )
                listings.append(card_listing)
                # print(listings)
        return listings


