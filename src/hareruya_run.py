from vendor_api.hareruya import HareruyaAPI

card_name = "Currency Converter"
listings = HareruyaAPI.search_card(card_name)
# print(listings)