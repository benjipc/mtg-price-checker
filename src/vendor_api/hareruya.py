import requests
import re
from bs4 import BeautifulSoup
import json
from typing import Optional, List
import pandas as pd
import urllib.parse
from card.card import Card_Spec, Card_Listing
from vendor_api.vendor_api import VendorAPI

class HareruyaAPI(VendorAPI):
    BASE_URL = "https://www.hareruyamtg.com/en"
    SEARCH_SUFFIX = "/products/search?suggest_type=all&product="
    PRODUCT_SUFFIX = "/products/detail/"
    
    @staticmethod
    def _get_html(search_url: str, headers: dict[str, str]) -> str:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        return response.text
    
    @staticmethod
    def _parse_search_results(response_text: str):
        hr_ids = []
        soup = BeautifulSoup(response_text, 'html.parser')
        
        ul_elements = soup.find_all('ul', class_='itemListLine itemListLine--searched')
        for ul in ul_elements:
            if ul.get('data-product'):
                data = json.loads(ul['data-product'])
                # Extract id from each dict in the data header
                if isinstance(data, list):
                    hr_ids.extend(item['id'] for item in data if 'id' in item)
        
        return hr_ids

    @staticmethod
    def _listings_from_html(
        hr_product_ids: List[str]
    ) -> Optional[List[Card_Listing]]:
        sell_info_divs = []
        
        for ids in hr_product_ids:
            product_url = f"{HareruyaAPI.BASE_URL}{HareruyaAPI.PRODUCT_SUFFIX}{ids}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response_text = HareruyaAPI._get_html(search_url=product_url, headers=headers) 
            soup = BeautifulSoup(response_text, "html.parser")
            
            sell_info = soup.find("div", {"class": "sell_info"})
            # print(f"Sell info: {sell_info}")
            if sell_info:
                sell_info_divs.append(sell_info) 

        listings = []
        for sell_info in sell_info_divs:
            card_description = sell_info.find("h2", {"class": "goods_name_"})
            full_description = card_description.text.strip()
                      
            card_name_match = re.search(r'《(.+?)》', full_description)
            edition_code_match = re.search(r'\[([^\]]+)\]', full_description) 
            card_number_match = re.search(r'\((\d+)\)', full_description)
            
            if card_name_match:
                card_name = card_name_match.group(1)
                edition_code = edition_code_match.group(1) if edition_code_match else None
                card_number = card_number_match.group(1) if card_number_match else None
            
            for lang in ["JP", "EN"]:
                price_table = sell_info.find("div", {"id": f"priceTable-{lang}"})
                if price_table:
                    rows = price_table.select("div.row.not-first.ng-star-inserted")
                    for row in rows[1:]:
                        condition_element = row.select_one("div.col-xs-2 strong")
                        if not condition_element or condition_element.text.strip() != "NM":
                            continue
                            
                        price_element = row.select_one("div.col-xs-3")
                        quantity_element = row.find_all("div", {"class": "col-xs-2"})[1]
                        
                        if all([price_element, quantity_element]):
                            price_text = price_element.text.strip().split()[0]
                            price = int(price_text.replace(',', ''))
                            quantity = int(quantity_element.text.strip())
                            
                            card_spec = Card_Spec(
                                name=card_name,
                                edition_code=edition_code,
                                card_number=card_number,
                                language="Japanese" if lang == "JP" else "English"
                            )

                            listing = Card_Listing(
                                card_spec=card_spec,
                                store="Hareruya",
                                price=price,
                                price_unit="Yen",
                                currency="JPY",
                                quantity=quantity,
                                description=full_description,
                                link=f"{HareruyaAPI.BASE_URL}{HareruyaAPI.PRODUCT_SUFFIX}{hr_product_ids}"
                            )
                            listings.append(listing)

        # print(listings)
        return listings

    @staticmethod
    def search_card(card_name: str) -> Optional[List[Card_Listing]]:
        # Encode the card name for the URL
        encoded_name = urllib.parse.quote(card_name)
        search_url = f"{HareruyaAPI.BASE_URL}{HareruyaAPI.SEARCH_SUFFIX}{encoded_name}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response_text = HareruyaAPI._get_html(search_url=search_url, headers=headers)
        hr_product_ids = HareruyaAPI._parse_search_results(
            response_text=response_text
        )
        listings = HareruyaAPI._listings_from_html(hr_product_ids=hr_product_ids)

        return listings

        
if __name__ == "__main__":
    # Example usage
    card_name = "Ghost Vacuum"
    hareruya_data = HareruyaAPI.search_card(card_name)
    if hareruya_data:
        print("There is data")
    else:
        print(f"No price found for {card_name}")