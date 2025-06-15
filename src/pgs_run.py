from vendor_api.pgs import PGSAPI

card_name = "Mox Jasper"
listings = PGSAPI.search_card_name(card_name)
print(listings)