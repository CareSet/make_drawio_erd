#!/usr/bin/env python3

import argparse
import sys
import logging
from make_drawio_erd.parsers.csv_data_parser import CSVDataParser
from make_drawio_erd.erd_drawio import ERDGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate draw.io ERD diagram from a CSV data file.')
    parser.add_argument('input_csv', help='Path to the input CSV data file')
    parser.add_argument('output_drawio', help='Path to the output draw.io diagram file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    parser.add_argument('--sample-size', type=int, default=10000, help='Number of rows to sample for data type inference (default: 10000)')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    logger = logging.getLogger(__name__)

    try:
        logger.info('Parsing the CSV data file...')
        # Parse the CSV data file using CSVDataParser
        parser_instance = CSVDataParser(args.input_csv, sample_size=args.sample_size)
        df = parser_instance.parse()

        logger.info('Generating the ERD diagram...')
        # Generate the ERD diagram using ERDGenerator
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

if __name__ == "__main__":
    main()
