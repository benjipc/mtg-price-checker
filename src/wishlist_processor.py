import pandas as pd
from vendor_api.vendor_api import VendorAPI
from vendor_api.mtgmate import MTGMateAPI as mmapi
from vendor_api.hareruya import HareruyaAPI as hrapi
from vendor_api.pgs import PGSAPI as pgsapi
from vendor_api.gamesdistrict import gamesdistrictAPI as gdaapi
from pathlib import Path
from card.card import Card_Spec as cs, filter_listings
import requests
from datetime import datetime, timedelta

class WishlistProcessor:
    def __init__(self):
        self.vendors = {
            'MTG Mate': mmapi,
            'PGS': pgsapi,
            'Games District': gdaapi,
            'Hareruya': hrapi
        }
        # Replace CurrencyRates with our own exchange rate handling
        self.exchange_rates = {}
        self.last_update = None
        self.fallback_rates = {
            'JPY': 0.0101,  # 1 JPY to AUD
            'USD': 1.52,    # 1 USD to AUD
        }

    def process_wishlist(self, wishlist_csv_path: Path) -> pd.DataFrame:
        wishlist = self._load_and_validate_csv(wishlist_csv_path)
        wishlist = self._prepare_wishlist(wishlist)
        wishlist = self._process_card_listings(wishlist)
        return wishlist

    def _load_and_validate_csv(self, wishlist_csv_path: Path) -> pd.DataFrame:
        assert wishlist_csv_path.exists(), f"Input file {wishlist_csv_path} does not exist."
        assert wishlist_csv_path.suffix == '.csv', "Input file must be a CSV file."
        wishlist = pd.read_csv(wishlist_csv_path)
        assert 'Name' in wishlist.columns
        assert 'Count' in wishlist.columns
        return wishlist

    def _prepare_wishlist(self, wishlist: pd.DataFrame) -> pd.DataFrame:
        # Create a copy to avoid chained assignment warnings
        df = wishlist.copy()
        
        # Convert and clean columns
        df['Count'] = df['Count'].astype(int)
        df['Edition Code'] = df['Edition Code'].astype(str).str.upper()
        df['Card Number'] = df['Card Number'].fillna(0).astype('Int64').astype(str).replace('0','')
        df['Language'] = df['Language'].fillna('English')
        df['Foil'] = df['Foil'].astype(object)
        
        df = df[['Count', 'Name', 'Edition Code', 'Card Number', 'Language', 'Foil']]
        df.loc[:, 'Foil'] = self._normalize_foil_column(df['Foil']).astype(object)
        df.loc[:, 'Card Spec'] = self._create_card_specs(df)
        df.loc[:, 'Results'] = None
        
        return df

    def _normalize_foil_column(self, foil_column: pd.Series) -> pd.Series:
        other_words_for_foil = ['foil', 'yes', 'foiled', 'true', '1']
        other_words_for_nonfoil = ['non-foil', 'no', 'false', '0', 'nonfoil']
        other_words_for_unspecified = ['', 'nan', 'unspecified', 'unknown', 'any', 'either', 'both']
        
        foil_normalisations = {}
        foil_normalisations.update({word: cs.Finish.FOIL for word in other_words_for_foil})
        foil_normalisations.update({word: cs.Finish.NON_FOIL for word in other_words_for_nonfoil})
        foil_normalisations.update({word: cs.Finish.UNSPECIFIED for word in other_words_for_unspecified})
        
        normalized = foil_column.astype(str).str.lower().replace(foil_normalisations)
        assert normalized.isin([v for v in cs.Finish]).all()
        return normalized

    def _create_card_specs(self, wishlist: pd.DataFrame) -> list:
        return [
            cs(
                name=row['Name'],
                edition_code=row['Edition Code'],
                card_number=row['Card Number'],
                finish=row['Foil'],
                language=row['Language']
            )
            for _, row in wishlist.iterrows()
        ]

    def _update_exchange_rates(self) -> None:
        now = datetime.now()
        # Update rates only once per hour
        if self.last_update and (now - self.last_update) < timedelta(hours=1):
            return

        try:
            response = requests.get('https://api.exchangerate-api.com/v4/latest/AUD', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.exchange_rates = {
                    'JPY': 1/data['rates']['JPY'],
                    'USD': 1/data['rates']['USD']
                }
                self.last_update = now
            else:
                raise Exception(f"API returned status code {response.status_code}")
        except Exception as e:
            print(f"Warning: Using fallback exchange rates due to: {e}")
            self.exchange_rates = self.fallback_rates.copy()

    def _normalize_price(self, price: float, currency: str, price_unit: str) -> float:
        # Update rates if needed
        self._update_exchange_rates()

        try:
            # Convert string price to float
            price = float(price)

            # Convert to AUD based on currency
            if currency == 'JPY':
                price = price * self.exchange_rates['JPY']
            elif currency == 'USD':
                price = price * self.exchange_rates['USD']
            elif currency == 'AUD':
                if price_unit == 'AUCents':
                    price = price / 100.0

            return round(price, 2)
        except Exception as e:
            print(f"Warning: Failed to convert price from {currency}: {e}")
            return price

    def _process_card_listings(self, wishlist: pd.DataFrame) -> pd.DataFrame:
        for index, row in wishlist.iterrows():
            vrdf_all = pd.DataFrame()
            for vendor_name, vendor_api in self.vendors.items():
                vendor_results = vendor_api.search_card(row['Name'])
                if vendor_results and len(vendor_results) > 0:
                    try:
                        vrdf = pd.concat([result.to_dataframe() for result in vendor_results], ignore_index=True)
                        
                        # Normalize prices before concatenating
                        vrdf['price'] = vrdf.apply(
                            lambda x: self._normalize_price(x['price'], x['currency'], x['price_unit']), 
                            axis=1
                        )
                        vrdf['currency'] = 'AUD'  # Set all currencies to AUD after conversion
                        vrdf['price_unit'] = 'dollars'  # Set all units to dollars
                        
                        vrdf_all = pd.concat([vrdf_all, vrdf], ignore_index=True)
                    except ValueError as e:
                        print(f"Warning: No valid results from {vendor_name} for {row['Name']}")
                        continue
                else:
                    print(f"No results from {vendor_name} for {row['Name']}")

            if vrdf_all.empty:
                print(f"Warning: No results found for {row['Name']} ({row['Edition Code']} {row['Card Number']})")
                continue

            vrdf_all = filter_listings(vrdf_all, row['Card Spec'])
            wishlist['Results'].iat[index] = vrdf_all.sort_values(by='price', ascending=True).reset_index(drop=True)
        
        return wishlist