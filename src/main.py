import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from api.scryfall import ScryfallAPI as sfapi
from mtgmate.mtgmate import MTGMateAPI as mmapi
from pathlib import Path
from card.card import Card_Spec as cs, Card_Listing as cl
from dacite import from_dict

def main(wishlist_csv_path: Path):
    assert wishlist_csv_path.exists(), f"Input file {args.input} does not exist."
    assert wishlist_csv_path.suffix == '.csv', "Input file must be a CSV file."
    wishlist = pd.read_csv(wishlist_csv_path)
    assert 'Name' in wishlist.columns
    assert 'Count' in wishlist.columns
    wishlist['Count'] = wishlist['Count'].astype(int)
    wishlist['Edition Code'] = wishlist['Edition Code'].astype(str)
    wishlist['Edition Code'] = wishlist['Edition Code'].apply(lambda x: x.upper())
    wishlist['Card Number'] = wishlist['Card Number'].fillna(0).astype('Int64').astype(str).replace('0','')
    print(wishlist['Card Number'])
    wishlist = wishlist[['Count','Name','Edition Code','Card Number','Language','Foil']] # skipped 'Condition'
    wishlist.fillna(value={'Language':'English'}, inplace=True)
    # Normalise foil column
    other_words_for_foil = ['foil', 'yes', 'foiled', 'true', '1']
    other_words_for_nonfoil = ['non-foil', 'no', 'false', '0', 'nonfoil', '', 'nan']
    foil_normalisations = {}
    foil_normalisations.update({old_foil_word: cs.Finish.FOIL for old_foil_word in other_words_for_foil})
    foil_normalisations.update({old_nonfoil_word: cs.Finish.NON_FOIL for old_nonfoil_word in other_words_for_nonfoil})
    wishlist['Foil'] = wishlist['Foil'].astype(str).str.lower().replace(foil_normalisations)
    assert wishlist['Foil'].isin([cs.Finish.FOIL, cs.Finish.NON_FOIL]).all()

    vendors = {
        'MTG Mate' : mmapi,
        # 'MTG Mate 2' : mmapi
        # 'Hareruya' : None #TODO API
    }
    # for vendor_name in vendors.keys():
    #     wishlist[vendor_name] = None

    wishlist['Results'] = None


    for index, row in wishlist.iterrows():
        vrdf_all = pd.DataFrame()
        for vendor_name, vendor_api in vendors.items():
            vendor_results = vendor_api.search_card(row['Name'])
            if vendor_results is not None:
                vrdf = pd.DataFrame(vendor_results)
                vrdf_all = pd.concat([vrdf_all, vrdf], ignore_index=True)

        wishlist['Results'].iat[index] = vrdf_all

            # if vendor_results is not None:
            #     # Filter results based on wishlist criteria
            #     # print(pd.DataFrame(vendor_results))
            #     vendor_results = [
            #         result for result in vendor_results if (
            #             (result.card_spec.edition_code == row['Edition Code'] or row['Edition Code'] == 'NAN') and
            #             (result.card_spec.card_number == row['Card Number'] or row['Card Number'] == '') and
            #             result.card_spec.finish == row['Foil'] and # TODO fix foil check cheapest
            #             result.card_spec.language == row['Language']
            #         )
            #     ]
            #     if vendor_results:
            #         vrdf = pd.DataFrame(vendor_results)
            #         # Sort by price (ascending)
            #         vrdf.sort_values(by='price', ascending=True, inplace=True)
            #         # vrdf.to_dict('records')
            #         # Add the first matching result to the wishlist
            #         vendor_results = vrdf.to_dict('records')[0]
            #         vendor_results = from_dict(data_class=cl, data=vendor_results)
            #     else:
            #         vendor_results = None
            # wishlist[vendor_name].iat[index] = vendor_results

    # print(wishlist.iloc[1]['MTG Mate'])
    # print(wishlist.head())
    print(wishlist['Results'][1])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process MTG card CSV files and add prices')
    parser.add_argument('-i','--input', help='Input CSV file path', default='testfile.csv')
    # parser.add_argument('output', required=False, help='Output CSV file path')
    args = parser.parse_args()

    assert args.input, "Input CSV file path is required. Use -i or --input to specify the file."

    input_path = Path(args.input)
    

    main(wishlist_csv_path=input_path)