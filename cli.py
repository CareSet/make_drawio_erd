# make_drawio_erd/cli.py

import argparse
import sys
import logging
from make_drawio_erd.parsers.metadata_csv_parser import MetaDataCSVParser
from make_drawio_erd.erd_drawio import ERDGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate draw.io ERD diagrams from a metadata CSV file.')
    parser.add_argument('input_csv', help='Path to the input metadata CSV file')
    parser.add_argument('output_drawio', help='Path to the output draw.io diagram file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    parser.add_argument('--matching', help='Unix-style glob pattern to match table names')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    logger = logging.getLogger(__name__)

    try:
        logger.info('Parsing the CSV file...')
        # Parse the CSV file
        csv_parser = MetaDataCSVParser(args.input_csv)
        df = csv_parser.parse()

        # Filter tables based on the pattern if provided
        if args.matching:
            logger.info(f"Filtering tables using pattern: {args.matching}")
            df = filter_tables_by_pattern(df, args.matching)

        logger.info('Generating the ERD diagram...')
        # Generate the ERD diagram
        erd_generator = ERDGenerator(df)
        drawio_xml = erd_generator.generate_drawio_xml()

        logger.info('Saving the ERD diagram to the output file...')
        # Save the XML to a file
        with open(args.output_drawio, 'w', encoding='utf-8') as f:
            f.write(drawio_xml)

        print(f"ERD diagram has been generated and saved to {args.output_drawio}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

def filter_tables_by_pattern(df, pattern):
    import fnmatch

    # Create a new column with the full table name
    df['full_table_name'] = df['Catalog'] + '.' + df['Database'] + '.' + df['Table']

    # Use fnmatch to filter the full_table_name based on the pattern
    matched_tables = df['full_table_name'].apply(lambda x: fnmatch.fnmatch(x, pattern))

    # Filter the DataFrame
    filtered_df = df[matched_tables].copy()

    if filtered_df.empty:
        raise ValueError(f"No tables match the pattern '{pattern}'.")

    # Remove the 'full_table_name' column before returning
    filtered_df.drop(columns=['full_table_name'], inplace=True)

    return filtered_df

if __name__ == "__main__":
    main()
