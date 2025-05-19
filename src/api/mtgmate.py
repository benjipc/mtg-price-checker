import requests
from bs4 import BeautifulSoup
import json
from typing import Optional
import urllib.parse

class MTGMateAPI:
    BASE_URL = "https://www.mtgmate.com.au"
    SEARCH_SUFFIX = "/cards/search?q="
    
    @staticmethod
    def search_card(card_name: str) -> Optional[float]:
        # Encode the card name for the URL
        encoded_name = urllib.parse.quote(card_name)
        search_url = f"{MTGMateAPI.BASE_URL}{MTGMateAPI.SEARCH_SUFFIX}{encoded_name}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            data_div = soup.find('div', {'data-react-class': 'FilterableTable'})
            
            if data_div and data_div.get('data-react-props'):
                data_react_props = data_div['data-react-props']
                if isinstance(data_react_props, str):
                    props_data = json.loads(data_react_props)
                else:
                    print("data-react-props attribute missing or not a string")
                    return None
                # print(props_data)
                prices = []
                
                if 'cards' in props_data:
                    for card_info in props_data['uuid'].values():
                        card_info_name = card_info['name'].split(' (')[0]
                        search_name = card_name.split(' (')[0]

                        if ('price' in card_info) and (card_info_name == search_name):
                            try:
                                price = int(card_info['price'])
                                uuid = card_info['uuid']
                                name = card_info_name
                                quantity = card_info['quantity']
                                link_path = card_info['link_path']
                                edition_code = card_info['set_code']
                                card_number = link_path.split('/')[-1].split(':')[0]
                                finish = card_info['finish']

                                prices.append((uuid, name, edition_code, card_number, finish, price, quantity, MTGMateAPI.BASE_URL+link_path))
                            except (ValueError, TypeError):
                                continue
                
                if prices:
                    return prices
            
            return None
            
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"Error searching MTGMate for card {card_name}: {e}")
            return None
        
if __name__ == "__main__":
    # Example usage
    card_name = "Ghost Vacuum"
    price = MTGMateAPI.search_card(card_name)
    if price:
        print(f"The lowest price for {card_name} is ${price:.2f}")
    else:
        print(f"No price found for {card_name}")