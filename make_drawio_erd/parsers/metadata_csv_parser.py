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
                    df[col] = 0  # Default to 0 for numeric columns
                elif col == 'Column_Order':
                    df[col] = pd.NA  # Use NA for missing Column_Order
                else:
                    df[col] = ''  # Default empty string for other columns

        # Convert 'Is_Primary_Key' and 'Is_Foreign_Key' to integers
        numeric_columns = ['Is_Primary_Key', 'Is_Foreign_Key']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # Convert 'Column_Order' to numeric, but do not fill missing values yet
        df['Column_Order'] = pd.to_numeric(df['Column_Order'], errors='coerce')

        # Generate sequential numbers within each group (table)
        df['Row_Number'] = df.groupby(['Catalog', 'Database', 'Table']).cumcount() + 1

        # Fill missing 'Column_Order' with 'Row_Number'
        df['Column_Order'] = df['Column_Order'].fillna(df['Row_Number'])

        # Convert 'Column_Order' to integers
        df['Column_Order'] = df['Column_Order'].astype(int)

        # Drop the temporary 'Row_Number' column
        df.drop(columns=['Row_Number'], inplace=True)

        return df
