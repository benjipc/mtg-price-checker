from vendor_api.hareruya import HareruyaAPI

card_name = "War Room"
listings = HareruyaAPI.search_card_name(card_name)
# print(listings)