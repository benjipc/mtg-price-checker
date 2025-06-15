from functools import cached_property

from typing import List
from pathlib import Path

import pandas as pd

from card import CardSpec

class Wishlist(): # consider sub-classing pd.DataFrame
    @classmethod
    def from_csv(cls, wishlist_csv_path: Path) -> 'Wishlist':
        df = pd.read_csv(wishlist_csv_path)
        return cls(df = df)
    
    def __init__(self, df: pd.DataFrame):
        df = df.copy() # Avoid modifying input dataframe
        required_columns = ['Name', 'Count', 'Edition Code', 'Card Number', 'Language', 'Foil']
        for required_column in required_columns:
            if required_column not in df.columns:
                raise ValueError(f"Required column '{required_column}' not found in the CSV file.")
        df = df[required_columns] # trim input dataframe to just the required columns
        
        # Convert and clean columns
        df['Count'] = df['Count'].astype(int)
        df['Edition Code'] = df['Edition Code'].astype(str).str.upper()
        df['Card Number'] = df['Card Number'].fillna(0).astype('Int64').astype(str).replace('0','')
        df['Language'] = df['Language'].fillna('English')
        df['Foil'] = df['Foil'].astype(str).str.upper().str.strip()

        # Convert foil column to CardSpec.Finish enum values
        foil_normalisations = {
            'FOIL': CardSpec.Finish.FOIL,
            'YES': CardSpec.Finish.FOIL,
            'FOILED': CardSpec.Finish.FOIL,
            'SHINY': CardSpec.Finish.FOIL,
            'TRUE': CardSpec.Finish.FOIL,
            '1': CardSpec.Finish.FOIL,

            'NON-FOIL': CardSpec.Finish.NON_FOIL,
            'NONFOIL': CardSpec.Finish.NON_FOIL,
            'NO': CardSpec.Finish.NON_FOIL,
            'FALSE': CardSpec.Finish.NON_FOIL,
            '0': CardSpec.Finish.NON_FOIL,
            
            '': CardSpec.Finish.UNSPECIFIED,
            'NAN': CardSpec.Finish.UNSPECIFIED,
            'UNSPECIFIED': CardSpec.Finish.UNSPECIFIED,
            'UNKNOWN': CardSpec.Finish.UNSPECIFIED,
            'ANY': CardSpec.Finish.UNSPECIFIED,
            'EITHER': CardSpec.Finish.UNSPECIFIED,
            'BOTH': CardSpec.Finish.UNSPECIFIED,
            '-': CardSpec.Finish.UNSPECIFIED,
            'NA': CardSpec.Finish.UNSPECIFIED,
        }

        df['Foil'] = df['Foil'].replace(foil_normalisations)#.astype(type(CardSpec.Finish))

        self.df = df
    
    @cached_property
    def card_specs(self) -> List[CardSpec]:
        card_specs = []
        for _, row in self.df.iterrows():
            card_spec = CardSpec(
                name=row['Name'],
                edition_code=row['Edition Code'],
                card_number=row['Card Number'],
                finish=row['Foil'],
                language=row['Language']
            )
            card_specs.append(card_spec)
        return card_specs

