import argparse
from pathlib import Path
from wishlist_processor import WishlistProcessor

def main(wishlist_csv_path: Path):
    processor = WishlistProcessor()
    wishlist = processor.process_wishlist(wishlist_csv_path)
    print(wishlist['Results'][0][['store','description','finish','price','currency','language','card_number','edition_code']])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process MTG card CSV files and add prices')
    parser.add_argument('-i','--input', help='Input CSV file path', default='testfile.csv')
    args = parser.parse_args()

    assert args.input, "Input CSV file path is required. Use -i or --input to specify the file."
    input_path = Path(args.input)
    main(wishlist_csv_path=input_path)