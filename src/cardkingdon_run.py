from vendor_api.cardkingdom import CardKingdomAPI

card_name = "Golgari Guildgate"
listings = CardKingdomAPI.search_card_name(card_name)
print(listings)