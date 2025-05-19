from .mtgmate import MTGMateAPI

def test_listings_from_html():
    with open('./src/mtgmate/mtgmate_Fury.html', 'r', encoding='utf-8') as file:
        response_text = file.read()
    
    card_name = "Fury"
    listings = MTGMateAPI.listings_from_html(response_text=response_text, search_card_name=card_name)
    assert len(listings) == 9
    assert listings[0].card_spec.name == "Fury"

    printings = [
        ["MH2", 126],
        ["MH2", 313],
        ["H2R", 100],
        ["SPG", 47],
        ["SPG", 52]
    ]

    

    for listing in listings:
        spec = listing.card_spec
        printing = [spec.edition_code, spec.card_number]
        assert printing in printings
        assert listing.store == "MTG Mate"
        assert listing.price_unit == "cents"
        assert listing.currency == "AUD"
        assert listing.card_spec.finish in ["Foil", "Non-Foil"]
        assert listing.link.startswith(MTGMateAPI.BASE_URL)
    # assert (False)


    card_name = "Brainstorm"
    listings = MTGMateAPI.listings_from_html(response_text=response_text, search_card_name=card_name)
    assert len(listings) == 0

    