# make_drawio_erd/erd_drawio.py

import pandas as pd
import xml.etree.ElementTree as ET
import html

class ERDGenerator:
    def __init__(
        self,
        df: pd.DataFrame,
        table_width=550,          # Increased default table width
        between_table_width=50,  # Space between tables
        column_font_size=12,      # Font size for column names
        title_font_size=20        # Font size for table titles
    ):
        self.df = df.copy()

        # Fill NaN values in string columns with empty strings
        object_cols = self.df.select_dtypes(include=['object']).columns
        self.df[object_cols] = self.df[object_cols].fillna('')

        # Ensure numeric columns are filled with appropriate default values
        numeric_cols = ['Is_Primary_Key', 'Is_Foreign_Key', 'Column_Order']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0).astype(int)

        self.tables = {}
        self.cells = {}
        self.cell_id = 2  # Starting from 2 because 0 and 1 are reserved in draw.io
        self.mxGraphModel = None
        self.root = None

        # Layout parameters
        self.table_width = table_width
        self.between_table_width = between_table_width
        self.column_font_size = column_font_size
        self.title_font_size = title_font_size

    def generate_drawio_xml(self) -> str:
        self._initialize_xml()
        self._create_tables()
        xml_str = ET.tostring(self.mxGraphModel, encoding='utf-8', method='xml').decode('utf-8')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

    def _initialize_xml(self):
        # Initialize mxGraphModel with default attributes
        self.mxGraphModel = ET.Element('mxGraphModel', {
            'dx': '0',  # Will be updated later
            'dy': '999',  # Keep default height
            'grid': '1',
            'gridSize': '10',
            'guides': '1',
            'tooltips': '1',
            'connect': '1',
            'arrows': '1',
            'fold': '1',
            'page': '1',
            'pageScale': '1',
            'pageWidth': '850',  # Will be updated later
            'pageHeight': '1100',
            'math': '0',
            'shadow': '0'
        })
        root = ET.SubElement(self.mxGraphModel, 'root')

        # Add the first two required cells
        ET.SubElement(root, 'mxCell', {'id': '0'})
        ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

        self.root = root

    def _create_tables(self):
        # Get unique combinations of Catalog, Database, and Table
        tables = self.df[['Catalog', 'Database', 'Table']].drop_duplicates()
        num_tables = len(tables)
        x_offset = 80  # Start with some offset
        y_offset = 40
        x_step = self.table_width + self.between_table_width  # Width of each table plus spacing

        # Calculate total diagram width
        total_width = x_offset + (x_step * num_tables)

        # Update diagram width attributes
        self.mxGraphModel.set('dx', str(total_width))
        self.mxGraphModel.set('pageWidth', str(total_width + 100))  # Add some margin

        for idx, table_row in tables.iterrows():
            catalog = table_row['Catalog']
            database = table_row['Database']
            table_name = table_row['Table']
            full_table_name = f"{catalog}.{database}.{table_name}"
            table_id = str(self.cell_id)
            self.cell_id += 1

            # Get columns for the table
            columns_df = self.df[
                (self.df['Catalog'] == catalog) &
                (self.df['Database'] == database) &
                (self.df['Table'] == table_name)
            ].sort_values('Column_Order')

            num_columns = len(columns_df)

            # Table height adjustments
            row_height = 30
            table_height = 30 + num_columns * row_height  # Header + rows

            # Create table cell (shape=table)
            table_cell = ET.SubElement(self.root, 'mxCell', {
                'id': table_id,
                'value': f'<span style="text-wrap: nowrap;">{html.escape(full_table_name)}</span>',
                'style': f'shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;'
                         f'fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;whiteSpace=wrap;'
                         f'fontSize={self.title_font_size};',
                'vertex': '1',
                'parent': '1'
            })
            table_geometry = ET.SubElement(table_cell, 'mxGeometry', {
                'x': str(x_offset),
                'y': str(y_offset),
                'width': str(self.table_width),
                'height': str(table_height),
                'as': 'geometry'
            })

            y_position = 30  # Start position for rows (after header)

            # Create rows for each column
            for idx2, row in columns_df.iterrows():
                row_id = str(self.cell_id)
                self.cell_id += 1

                # Determine PK/FK indicator
                is_primary_key = int(row.get('Is_Primary_Key', 0) or 0) == 1
                is_foreign_key = int(row.get('Is_Foreign_Key', 0) or 0) == 1

                pk_fk_value = ''
                if is_primary_key:
                    pk_fk_value = 'PK'
                elif is_foreign_key:
                    pk_fk_value = 'FK'

                # Create row cell
                row_cell = ET.SubElement(self.root, 'mxCell', {
                    'id': row_id,
                    'value': '',
                    'style': 'shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;'
                             'fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];'
                             'portConstraint=eastwest;top=0;left=0;right=0;bottom=0;html=1;',
                    'vertex': '1',
                    'parent': table_id
                })
                row_geometry = ET.SubElement(row_cell, 'mxGeometry', {
                    'y': str(y_position),
                    'width': str(self.table_width),
                    'height': str(row_height),
                    'as': 'geometry'
                })

                # PK/FK indicator cell
                indicator_id = str(self.cell_id)
                self.cell_id += 1

                indicator_cell = ET.SubElement(self.root, 'mxCell', {
                    'id': indicator_id,
                    'value': pk_fk_value,
                    'style': 'shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;'
                             'bottom=0;right=0;fontStyle=1;overflow=hidden;html=1;whiteSpace=wrap;',
                    'vertex': '1',
                    'parent': row_id
                })
                indicator_geometry = ET.SubElement(indicator_cell, 'mxGeometry', {
                    'width': '60',
                    'height': str(row_height),
                    'as': 'geometry'
                })
                ET.SubElement(indicator_geometry, 'mxRectangle', {
                    'width': '60',
                    'height': str(row_height),
                    'as': 'alternateBounds'
                })

                # Column name cell
                column_id = str(self.cell_id)
                self.cell_id += 1

                column_name = row['Column']
                data_type = row.get('Type', '')
                column_display = f"{column_name}"  # Optionally include data type

                column_cell = ET.SubElement(self.root, 'mxCell', {
                    'id': column_id,
                    'value': html.escape(column_display),
                    'style': f'shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;'
                             f'bottom=0;right=0;align=left;spacingLeft=6;fontStyle=5;overflow=hidden;'
                             f'html=1;whiteSpace=wrap;fontSize={self.column_font_size};',
                    'vertex': '1',
                    'parent': row_id
                })
                column_geometry = ET.SubElement(column_cell, 'mxGeometry', {
                    'x': '60',
                    'width': str(self.table_width - 60),
                    'height': str(row_height),
                    'as': 'geometry'
                })
                ET.SubElement(column_geometry, 'mxRectangle', {
                    'width': str(self.table_width - 60),
                    'height': str(row_height),
                    'as': 'alternateBounds'
                })

                y_position += row_height  # Move to the next row position

            # Update x_offset for the next table
            x_offset += x_step

    # Relationships are omitted as per your request
