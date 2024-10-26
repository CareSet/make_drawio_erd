# make_drawio_erd/parsers/metadata_csv_parser.py

import pandas as pd
from .base_parser import BaseParser

class MetaDataCSVParser(BaseParser):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> pd.DataFrame:
        df = pd.read_csv(self.file_path)
        # Ensure the DataFrame conforms to the expected structure
        expected_columns = [
            'Catalog', 'Database', 'Table', 'Owner', 'Creation_Date',
            'Column', 'Type', 'Column_Order', 'Source_Table',
            'Is_Primary_Key', 'Is_Foreign_Key'
        ]
        # Check for missing columns and add them with default values
        for col in expected_columns:
            if col not in df.columns:
                if col in ['Is_Primary_Key', 'Is_Foreign_Key']:
                    df[col] = 0  # Default to 0 (False)
                else:
                    df[col] = ''  # Default empty string for other columns

        # Convert 'Is_Primary_Key' and 'Is_Foreign_Key' to integers (0 or 1)
        df['Is_Primary_Key'] = df['Is_Primary_Key'].fillna(0).astype(int)
        df['Is_Foreign_Key'] = df['Is_Foreign_Key'].fillna(0).astype(int)

        return df
