import requests
from bs4 import BeautifulSoup
import json
from typing import Optional
import urllib.parse

class HareruyaAPI:
    BASE_URL = "https://www.hareruyamtg.com/en"
    SEARCH_SUFFIX = "/products/search?suggest_type=all&product="
    
    @staticmethod
    def search_card(card_name: str) -> Optional[float]:
        # Encode the card name for the URL
        encoded_name = urllib.parse.quote(card_name).replace('%20', '+')
        # print(f"{HareruyaAPI.BASE_URL}{HareruyaAPI.SEARCH_SUFFIX}{encoded_name}")
        search_url = f"{HareruyaAPI.BASE_URL}{HareruyaAPI.SEARCH_SUFFIX}{encoded_name}"
        # search_url = 'https://www.hareruyamtg.com/en/products/detail/166662?lang=EN'
        # line 666 contains english stuff
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            with open('hareruya.html', 'w', encoding='utf-8') as file:
                file.write(soup.prettify())
            card_items = soup.find('class', class_='autopagerize_page_element')
            print(card_items)
            
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"Error searching Hareruya for card {card_name}: {e}")
            return None
        
if __name__ == "__main__":
    # Example usage
    card_name = "Ghost Vacuum"
    hareruya_data = HareruyaAPI.search_card(card_name)
    if hareruya_data:
        print("There is data")
    else:
        print(f"No price found for {card_name}")