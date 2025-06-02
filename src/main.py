import argparse
import pandas as pd
from vendor_api.vendor_api import VendorAPI
from vendor_api.mtgmate import MTGMateAPI as mmapi
from vendor_api.hareruya import HareruyaAPI as hrapi
from vendor_api.pgs import PGSAPI as pgsapi
from vendor_api.gamesdistrict import gamesdistrictAPI as gdaapi
from pathlib import Path
from card.card import Card_Spec as cs, filter_listings

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
    # print(wishlist['Card Number'])
    wishlist = wishlist[['Count','Name','Edition Code','Card Number','Language','Foil']] # skipped 'Condition'
    wishlist.fillna(value={'Language':'English'}, inplace=True)
    # Normalise foil column
    other_words_for_foil = ['foil', 'yes', 'foiled', 'true', '1']
    other_words_for_nonfoil = ['non-foil', 'no', 'false', '0', 'nonfoil']
    other_words_for_unspecified = ['', 'nan', 'unspecified', 'unknown', 'any', 'either', 'both']
    foil_normalisations = {}
    foil_normalisations.update({old_foil_word: cs.Finish.FOIL for old_foil_word in other_words_for_foil})
    foil_normalisations.update({old_nonfoil_word: cs.Finish.NON_FOIL for old_nonfoil_word in other_words_for_nonfoil})
    foil_normalisations.update({old_unspecified_word: cs.Finish.UNSPECIFIED for old_unspecified_word in other_words_for_unspecified})
    wishlist['Foil'] = wishlist['Foil'].astype(str).str.lower().replace(foil_normalisations)
    assert wishlist['Foil'].isin([v for v in cs.Finish]).all()

    # print(wishlist.head())

    vendors:dict[str, type[VendorAPI]] = {
        'MTG Mate' : mmapi,
        'PGS' : pgsapi,
        'Games District' : gdaapi,
        'Hareruya' : hrapi
    }

    wishlist['Card Spec'] = [
        cs(
            name=row['Name'],
            edition_code=row['Edition Code'],
            card_number=row['Card Number'],
            finish=row['Foil'],
            language=row['Language']
        )
        for _, row in wishlist.iterrows()
    ]
    # print(wishlist['Card Spec'][0])
    wishlist['Results'] = None


    for index, row in wishlist.iterrows():
        vrdf_all = pd.DataFrame()
        for vendor_name, vendor_api in vendors.items():
            vendor_results = vendor_api.search_card(row['Name'])
            if vendor_results and len(vendor_results) > 0:  # Check if results exist and not empty
                try:
                    vrdf = pd.concat([result.to_dataframe() for result in vendor_results], ignore_index=True)
                    vrdf_all = pd.concat([vrdf_all, vrdf], ignore_index=True)
                except ValueError as e:
                    print(f"Warning: No valid results from {vendor_name} for {row['Name']}")
                    continue
            else:
                print(f"No results from {vendor_name} for {row['Name']}")

        if vrdf_all.empty:
            print(f"Warning: No results found for {row['Name']} ({row['Edition Code']} {row['Card Number']})")
            continue  # Skip to next card if no results found
        
        vrdf_all = filter_listings(vrdf_all, row['Card Spec'])
        wishlist['Results'].iat[index] = vrdf_all.sort_values(by='price', ascending=True).reset_index(drop=True)

    print(wishlist['Results'][0][['store','description','finish','price','currency','language','card_number','edition_code']])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process MTG card CSV files and add prices')
    parser.add_argument('-i','--input', help='Input CSV file path', default='testfile.csv')
    # parser.add_argument('output', required=False, help='Output CSV file path')
    args = parser.parse_args()

    assert args.input, "Input CSV file path is required. Use -i or --input to specify the file."

    input_path = Path(args.input)
    

    main(wishlist_csv_path=input_path)