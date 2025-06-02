import requests
import json
from typing import Optional, List, Dict, Any

class BinderPosAPI:
    def __init__(self, store_url: str, origin: str, referer: str):
        self.store_url = store_url
        self.base_url = 'https://portal.binderpos.com/external/shopify/products/forStore'
        self.headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': origin,
            'referer': referer,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }

    def search_cards(
        self,
        title: str,
        instock_only: bool = True,
        price_greater_than: float = 0,
        price_less_than: Optional[float] = None,
        limit: int = 18,
        offset: int = 0,
        set_names: Optional[List[str]] = None,
        sort_ascending: bool = True
    ) -> Dict[str, Any]:
        
        json_data = {
            'storeUrl': self.store_url,
            'game': 'mtg',
            'strict': None,
            'sortTypes': [
                {
                    'type': 'price',
                    'asc': sort_ascending,
                    'order': 1,
                },
            ],
            'variants': None,
            'title': title,
            'priceGreaterThan': price_greater_than,
            'priceLessThan': price_less_than,
            'instockOnly': instock_only,
            'limit': limit,
            'offset': offset,
            'setNames': set_names or [],
            'colors': [],
            'rarities': [],
            'types': [],
        }

        response = requests.post(self.base_url, headers=self.headers, json=json_data)
        response.raise_for_status()
        
        return response.json()

    def extract_in_stock_variants(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        in_stock_variants = []
        
        for product in response_data.get('products', []):
            for variant in product.get('variants', []):
                if variant.get('quantity', 0) > 0:
                    in_stock_variants.append({
                        'variant_id': variant.get('shopifyId'),
                        'name': product.get('cardName'),
                        'title': product.get('title'),
                        'sku': variant.get('sku'),
                        'price': variant.get('price'),
                        'quantity': variant.get('quantity'),
                        'condition': variant.get('title'),
                        'foiling': 'foil' if 'foil' in variant.get('title', '').lower() else 'non-foil',
                        'set': product.get('set'),
                        'card-number': product.get('collectorNumber'),
                        'set-code': product.get('setCode'),
                        'language': 'Non English' if 'non english' in variant.get('title', '').lower() else 'English',
                    })
                    
        return in_stock_variants

if __name__ == "__main__":
    api = BinderPosAPI(
        store_url="pro-gamers-and-collectables.myshopify.com",
        origin="https://progamers.com.au",
        referer="https://progamers.com.au/"
    )
    
    results = api.search_cards("boseiju")
    
    in_stock = api.extract_in_stock_variants(results)
    
    for variant in in_stock:
        print(f"{variant['name']} ({variant['foiling']}) ({variant['set-code']}) ({variant['card-number']}) ({variant['condition']}): ${variant['price']} - {variant['quantity']} in stock")
