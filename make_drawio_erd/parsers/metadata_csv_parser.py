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
                if col in ['Is_Primary_Key', 'Is_Foreign_Key', 'Column_Order']:
                    df[col] = 0  # Default to 0 for numeric columns
                else:
                    df[col] = ''  # Default empty string for other columns

        # Convert 'Is_Primary_Key', 'Is_Foreign_Key', and 'Column_Order' to integers
        numeric_columns = ['Is_Primary_Key', 'Is_Foreign_Key', 'Column_Order']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        return df
