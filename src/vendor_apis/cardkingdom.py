import requests
from bs4 import BeautifulSoup
import json
from typing import Optional, List
import urllib.parse
from card import CardSpec, VendorListing
from vendor_api import VendorAPI

class CardKingdomAPI(VendorAPI):
    BASE_URL = "https://www.cardkingdom.com/"
    SEARCH_SUFFIX_NF = "/catalog/search?&filter[tab]=mtg_card&filter%5Bname%5D="
    SEARCH_SUFFIX_F = "/catalog/search?filter[tab]=mtg_foil&filter%5Bname%5D="
    URL_SUFFIX = '&search=header'

    @staticmethod
    def _get_html(card_name) -> str:
        response = []
        cookies = {
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=mox+jasper',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"136.0.7103.114"',
            'sec-ch-ua-full-version-list': '"Chromium";v="136.0.7103.114", "Google Chrome";v="136.0.7103.114", "Not.A/Brand";v="99.0.0.0"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"19.0.0"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }

        params = {
            'search': 'header',
            'filter[name]': card_name,
        }

        response.append(requests.get('https://www.cardkingdom.com/catalog/search', params=params, cookies=cookies, headers=headers))
        response.append(requests.get('https://www.cardkingdom.com/catalog/search?filter[tab]=mtg_foil', params=params, cookies=cookies, headers=headers))
        return '\n'.join(r.text for r in response)
    

    @staticmethod
    def _listings_from_html(
        response_text: str, search_card_name: str
    ) -> Optional[list[VendorListing]]:
        product_data = []
        soup = BeautifulSoup(response_text, 'html.parser')
        product_items = soup.find_all('div', class_='productItemWrapper')

        for item in product_items:
            name_elem = item.find('span', class_='productDetailTitle').find('a')
            card_name = name_elem.text.strip().split(" (")[0]  # Get the card name before any additional info in parentheses)
            set_info = item.find('div', class_='productDetailSet')
            collector_number = set_info.find('div', class_='collector-number')
            collector_number = collector_number.text.replace('Collector #:', '').strip() if collector_number else "Unknown"
            
            # Get edition code from image alt text
            card_wrapper = item.find('div', class_='mtg-card-static-wrapper')
            if card_wrapper:
                # Find mtg-card-image tag and get its alt attribute
                mtg_card = card_wrapper.find('mtg-card-image')
                if mtg_card and mtg_card.has_attr('alt'):
                    edition_code = mtg_card['alt'].split(':')[0][:3]
                else:
                    edition_code = "Unknown"
            else:
                edition_code = "Unknown"
            
            condition_items = item.find_all('li', class_='itemAddToCart')
            for condition in condition_items:
                # Skip if out of stock
                if condition.find('div', class_='outOfStockNotice'):
                    continue

                # Get condition grade
                condition_grade = condition.find('input', {'name': 'style[0]'})['value'] #TODO implement later
                foil_elem = condition.find('input', {'name': 'model'})['value']
                if foil_elem == 'mtg_foil':
                    finish = CardSpec.Finish.FOIL
                elif foil_elem == 'mtg_card':
                    finish = CardSpec.Finish.NON_FOIL
                else:
                    finish = CardSpec.Finish.UNSPECIFIED
                
                
                # Get price and quantity
                price_elem = condition.find('span', class_='stylePrice')
                quantity_elem = condition.find('span', class_='styleQty')
                if price_elem and quantity_elem:
                    price = float(price_elem.text.strip().replace('$', '').strip())
                    quantity = int(quantity_elem.text.strip())

                    if card_name.lower() == search_card_name.lower():
                        # TODO fix time spiral reprint of endurance not making it past the filter due to mismatched set ID but matching number.
                        # print(f"Found card: {card_name}, Edition: {edition_code}, Collector Number: {collector_number}, Price: {price}, Quantity: {quantity}, Finish: {finish}")
                        card_spec = CardSpec(
                            name=card_name,
                            edition_code=edition_code,
                            card_number=collector_number,
                            finish=finish,
                            language="English"
                        )
                        
                        listing = VendorListing(
                            card_spec=card_spec,
                            store="Card Kingdom",
                            price=price,
                            currency="USD",
                            price_unit="USD",
                            quantity=quantity,
                            description=name_elem.text.strip(),
                            link=f"https://www.cardkingdom.com{name_elem.get('href', '')}"
                        )
                        product_data.append(listing)
                    else:
                        pass
        # print(product_data)
        return product_data

    @staticmethod
    def search_card_name(card_name: str) -> Optional[List[VendorListing]]:#TODO think about where it needs to be async
        # search_url = f"{CardKingdomAPI.BASE_URL}{CardKingdomAPI.SEARCH_SUFFIX_NF}{encoded_name}{CardKingdomAPI.URL_SUFFIX}"

        try: 
            response_text = CardKingdomAPI._get_html(card_name=card_name)
            listings = CardKingdomAPI._listings_from_html(
                response_text=response_text, search_card_name=card_name
            )

            return listings

        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"Error searching Card Kingdom for card {card_name}: {e}")
            return None
