import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime

from card import CardSpec, VendorListing
from wishlist import Wishlist
from vendor_apis import vendor_apis, VendorAPI, VendorListingsT

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)



    # Replace CurrencyRates with our own exchange rate handling
    # self.exchange_rates = {}
    # self.last_update = None
    # self.fallback_rates = {
    #     'JPY': 0.0101,  # 1 JPY to AUD
    #     'USD': 1.52,    # 1 USD to AUD
    # }


# def _update_exchange_rates(self) -> None:
#     now = datetime.now()
#     # Update rates only once per hour
#     if self.last_update and (now - self.last_update) < timedelta(hours=1):
#         return

#     try:
#         response = requests.get('https://api.exchangerate-api.com/v4/latest/AUD', timeout=5)
#         if response.status_code == 200:
#             data = response.json()
#             self.exchange_rates = {
#                 'JPY': 1/data['rates']['JPY'],
#                 'USD': 1/data['rates']['USD']
#             }
#             self.last_update = now
#         else:
#             raise Exception(f"API returned status code {response.status_code}")
#     except Exception as e:
#         print(f"Warning: Using fallback exchange rates due to: {e}")
#         self.exchange_rates = self.fallback_rates.copy()

# def _normalize_price(self, price: float, currency: str, price_unit: str) -> float:
#     self._update_exchange_rates()

#     try:
#         price = float(price)
#         if currency == 'JPY':
#             price = price * self.exchange_rates['JPY']
#         elif currency == 'USD':
#             price = price * self.exchange_rates['USD']
#         elif currency == 'AUD':
#             if price_unit == 'AUCents':
#                 price = price / 100.0

#         return round(price, 2)
#     except Exception as e:
#         print(f"Warning: Failed to convert price from {currency}: {e}")
#         return price

# def _process_card_listings(self, wishlist: pd.DataFrame) -> pd.DataFrame:
#     for index, row in tqdm(wishlist.iterrows(), total=wishlist.shape[0]):
#         vrdf_all = pd.DataFrame()
#         for vendor_name, vendor_api in self.vendors.items():
#             vendor_results = vendor_api.search_card_name(row['Name'])
#             if vendor_results and len(vendor_results) > 0:
#                 try:
#                     vrdf = pd.concat([result.to_dataframe() for result in vendor_results], ignore_index=True)
                    
#                     # Normalize prices before concatenating
#                     vrdf['price'] = vrdf.apply(
#                         lambda x: self._normalize_price(x['price'], x['currency'], x['price_unit']), 
#                         axis=1
#                     )
#                     vrdf['currency'] = 'AUD'  # Set all currencies to AUD after conversion
#                     vrdf['price_unit'] = 'dollars'  # Set all units to dollars
                    
#                     vrdf_all = pd.concat([vrdf_all, vrdf], ignore_index=True)
#                 except ValueError as e:
#                     print(f"Warning: No valid results from {vendor_name} for {row['Name']}")
#                     continue
#             else:
#                 # print(f"No results from {vendor_name} for {row['Name']}")
#                 tqdm.write(f"No results from {vendor_name} for {row['Name']}")
                

#         if vrdf_all.empty:
#             print(f"Warning: No results found for {row['Name']} ({row['Edition Code']} {row['Card Number']})")
#             continue

#         vrdf_all = filter_listings(vrdf_all, row['Card Spec'])
#         vrdf_all = vrdf_all[vrdf_all['quantity'] > 0]
#         wishlist['Results'].iat[index] = vrdf_all.sort_values(by='price', ascending=True).reset_index(drop=True)
    
#     return wishlist



# def standardise_listing(messy_listing: VendorListing) -> VendorListing:
#     cleaned_listing = VendorListing()
#     return cleaned_listing



SearchResponsesT = Tuple[CardSpec, VendorListingsT]
SearchResultsT = List[SearchResponsesT]



def listings_to_dataframe(listings: VendorListingsT) -> Optional[pd.DataFrame]:
    """
    Convert a list of VendorListing objects to a single DataFrame.
    """
    if listings is None:
        return None
    return pd.concat([listing.to_dataframe() for listing in listings], ignore_index=True)

def main(wishlist_csv_path: Path) -> pd.DataFrame:
    def search_vendors(card_specs: List[CardSpec], vendor_apis: Dict[str, VendorAPI]) -> SearchResultsT:
        # TODO: make this async
        results = []
        for card_spec in card_specs:
            for vendor_name, vendor_api in vendor_apis.items():
                listings = vendor_api.filtered_listings(card_spec=card_spec)
                if listings:
                    results.append((card_spec, listings))
                    # results.append(listings)
        return results

    # Make Wishlist object from wishlist on disk.
    wishlist = Wishlist.from_csv(wishlist_csv_path=wishlist_csv_path)
    # print(wishlist.df)

    # Search for each card in the wishlist across all vendors; collecting all results
    all_vendor_results = search_vendors(card_specs=wishlist.card_specs, vendor_apis=vendor_apis)
    # for card_spec, listings in all_vendor_results:
    #     print(f"Found {len(listings)} listings for {card_spec} from {listings[0].store if listings else 'No Vendor'}")
    # print(wishlist_all_vendors)
    # yield results asynchronously


    # list_of_listings_to_dataframe = lambda searches: pd.DataFrame([listing.to_dataframe() for listing in listings for _, listings in searches])
    # # list_of_listings_to_dataframe(all_wishlist_listings)

    # # Combine all filtered results into a single DataFrame
    # vrdf_all = pd.concat(list_of_listings_to_dataframe(wishlist_all_vendors), ignore_index=True)

    # Return Single dataframe of results
    listings = [listing for _, listings in all_vendor_results for listing in listings]
    return listings_to_dataframe(listings)

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description='Process MTG card CSV files and add prices')
    parser.add_argument('-i', '--input', help='Input CSV file path', default='testfile.csv')
    # parser.add_argument('-o', '--output', help='Output CSV file path', default='testoutfile.csv')
    parser.add_argument('-o', '--output', help='Output CSV file path')
    args = parser.parse_args()

    assert args.input, "Input CSV file path is required. Use -i or --input to specify the file."

    # handle file input
    input_path = Path(args.input)
    assert input_path.exists(), f"{args.input} does not exist."
    assert input_path.suffix == '.csv', "Wishlist must be a CSV file."

    #run main and capture result
    output_df = main(wishlist_csv_path=input_path)

    #handle file output
    output_path = Path(args.output) if args.output else input_path.with_stem(f"{input_path.stem}_results")
    timestamp = datetime.now().strftime("%Y%m%d_%H")
    output_df.to_csv(output_path.with_stem(f"{output_path.stem}_{timestamp}"), index=False, sep='\t', encoding='utf-8-sig')
    print(f"Results saved to {output_path.with_stem(f"{output_path.stem}_{timestamp}")}")
