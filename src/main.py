import argparse
import pandas as pd
from datetime import datetime
from api.scryfall import ScryfallAPI as sfapi
from mtgmate.mtgmate import MTGMateAPI as mmapi
from pathlib import Path
from card import Card_Spec as cs, Card_Listing as cl

def main(wishlist_csv_path: Path):
    assert wishlist_csv_path.exists(), f"Input file {args.input} does not exist."
    assert wishlist_csv_path.suffix == '.csv', "Input file must be a CSV file."
    wishlist = pd.read_csv(wishlist_csv_path)
    assert 'Name' in wishlist.columns
    assert 'Count' in wishlist.columns
    wishlist['Count'] = wishlist['Count'].astype(int)
    # Normalise foil column
    other_words_for_foil = ['foil', 'yes', 'foiled', 'true', '1']
    other_words_for_nonfoil = ['non-foil', 'no', 'false', '0', 'nonfoil', '', 'nan']
    foil_normalisations = {}
    foil_normalisations.update({old_foil_word: cs.Finish.FOIL for old_foil_word in other_words_for_foil})
    foil_normalisations.update({old_nonfoil_word: cs.Finish.NON_FOIL for old_nonfoil_word in other_words_for_nonfoil})
    wishlist['Foil'] = wishlist['Foil'].astype(str).str.lower().replace(foil_normalisations)
    print (wishlist['Foil'])
    assert wishlist['Foil'].isin([cs.Finish.FOIL, cs.Finish.NON_FOIL]).all()


    vendors = {
        'MTG Mate' : mmapi,
        'Hareruya' : None #TODO API
    }

    for _, row in wishlist.iterrows():
        card_name = row['Name']
        # Normalise card name
        card_data = sfapi.search_card(card_name)
        
        if card_data:
            result = {
                'Name': card_name,
                'Count': row['Count'],
                'Set': row.get('Edition Code', 'N/A'),
                'Collector Number': row.get('Card Number', 'N/A'),
                'Foil': row.get('Foil', 'No'),
                'MTG Mate Price': None,
                'MTG Mate Quantity': None,
                'MTG Mate Link': None
            }
            
            # Search MTGMate
            mtgmate_data = mmapi.search_card(card_name)
            # print(f"{card_name}:", mtgmate_data)
            if isinstance(mtgmate_data, list) and mtgmate_data:
                # If set code and collector number are provided, find matching card
                if result['Set'] != 'N/A' and result['Collector Number'] != 'N/A':
                    matching_card = next(
                        (card for card in mtgmate_data 
                         if card[2] == result['Set'] and card[3] == result['Collector Number']
                         and card[6] > 0),  # Check quantity > 0
                        None
                    )
                    
                    # If no matching card found, get cheapest with quantity > 0
                    if not matching_card:
                        matching_card = min(
                            (card for card in mtgmate_data if card[6] > 0),
                            key=lambda x: x[5],
                            default=None
                        )
                else:
                    # Get cheapest available card
                    matching_card = min(
                        (card for card in mtgmate_data if card[6] > 0),
                        key=lambda x: x[5],
                        default=None
                    )
                
                if matching_card:
                    result['MTG Mate Quantity'] = matching_card[6]
                    result['MTG Mate Price'] = matching_card[5]
                    result['MTG Mate Link'] = matching_card[7]
            
            results.append(result)
        else:
            print(f"Could not find data for card: {card_name}")
    df_results = pd.DataFrame(results)
    
    # Display results
    print("\nResults:")
    print(df_results[['Name', 'Count', 'Set', 'Collector Number', 'MTG Mate Price', 'MTG Mate Quantity', 'MTG Mate Link']])
    
    # Generate filename with date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f'output_{timestamp}.csv'
    
    # Export to CSV
    df_results.to_csv(output_path, index=False)
    print(f"\nResults exported to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process MTG card CSV files and add prices')
    parser.add_argument('-i','--input', help='Input CSV file path', default='testfile.csv')
    # parser.add_argument('output', required=False, help='Output CSV file path')
    args = parser.parse_args()

    assert args.input, "Input CSV file path is required. Use -i or --input to specify the file."

    input_path = Path(args.input)
    

    main(wishlist_csv_path=input_path)