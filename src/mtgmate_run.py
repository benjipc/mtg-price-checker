from vendor_api.mtgmate import MTGMateAPI

card_name = "Fury"
listings = MTGMateAPI.search_card(card_name)
print(listings)