import argparse
from pathlib import Path
from typing import Optional
from wishlist_processor import WishlistProcessor
import pandas as pd
from datetime import datetime

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def main(wishlist_csv_path: Path, output_csv_path: Optional[Path] = None):
    processor = WishlistProcessor()
    wishlist = processor.process_wishlist(wishlist_csv_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    all_results = []
    
    for idx, row in wishlist.iterrows():
        if 'Results' in row and isinstance(row['Results'], pd.DataFrame):
            results_df = row['Results'].copy()
            if results_df is not None and not results_df.empty:
                all_results.append(results_df)
    
    if all_results:
        output_df = pd.concat(all_results, ignore_index=True)
        
        if output_df is not None:
            if len(output_df) > 1:
                output_df = output_df.iloc[1:]
            
            if output_csv_path:
                output_df.to_csv(output_csv_path.with_stem(f"{output_csv_path.stem}_{timestamp}"), index=False, sep='\t', encoding='utf-8-sig')
                print(f"Results saved to {output_csv_path.with_stem(f"{output_csv_path.stem}_{timestamp}")}")
            
            return output_df
    
    return pd.DataFrame()  # Return empty DataFrame if no results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process MTG card CSV files and add prices')
    parser.add_argument('-i', '--input', help='Input CSV file path', default='testfile.csv')
    parser.add_argument('-o', '--output', help='Output CSV file path', default='testoutfile.csv')
    args = parser.parse_args()

    assert args.input, "Input CSV file path is required. Use -i or --input to specify the file."
    input_path = Path(args.input)
    
    output_path = Path(args.output) if args.output else input_path.with_stem(f"{input_path.stem}_processed")
    
    main(wishlist_csv_path=input_path, output_csv_path=output_path)