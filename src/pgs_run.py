from vendor_api.pgs import PGSAPI

card_name = "Mox Jasper"
listings = PGSAPI.search_card(card_name)
print(listings)