from typing import Dict

from vendor_api import VendorAPI, VendorListingsT

from .cardkingdom import CardKingdomAPI
from .gamesdistrict import GamesDistrictAPI
from .hareruya import HareruyaAPI
from .mtgmate import MTGMateAPI
from .pgs import PGSAPI

vendor_apis : Dict [str, VendorAPI] = {
    "Card Kingdom": CardKingdomAPI,
    # "Games District": GamesDistrictAPI,
    # "Hareruya": HareruyaAPI,
    "MTG Mate": MTGMateAPI,
    # "PGS": PGSAPI
}