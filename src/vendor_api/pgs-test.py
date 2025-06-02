import requests
import json

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
    'content-type': 'application/json',
    'origin': 'https://progamers.com.au',
    'priority': 'u=1, i',
    'referer': 'https://progamers.com.au/',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
}

json_data = {
    'storeUrl': 'pro-gamers-and-collectables.myshopify.com',
    'game': 'mtg',
    'strict': None,
    'sortTypes': [
        {
            'type': 'price',
            'asc': True,
            'order': 1,
        },
    ],
    'variants': None,
    'title': 'boseiju',
    'priceGreaterThan': 0,
    'priceLessThan': None,
    'instockOnly': True,
    'limit': 18,
    'offset': 0,
    'setNames': [],
    'colors': [],
    'rarities': [],
    'types': [],
}

response = requests.post('https://portal.binderpos.com/external/shopify/products/forStore', headers=headers, json=json_data)

with open('pgs_response.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, indent=2, ensure_ascii=False)

# print(response.json())

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"storeUrl":"pro-gamers-and-collectables.myshopify.com","game":"mtg","strict":null,"sortTypes":[{"type":"price","asc":true,"order":1}],"variants":null,"title":"boseiju","priceGreaterThan":0,"priceLessThan":null,"instockOnly":true,"limit":18,"offset":0,"setNames":[],"colors":[],"rarities":[],"types":[]}'
#response = requests.post('https://portal.binderpos.com/external/shopify/products/forStore', headers=headers, data=data)