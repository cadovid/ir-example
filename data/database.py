import duckdb
import struct


class Database:
    
    def __init__(self, db_path, verbose):
        self.db_path = db_path
        self.connection = duckdb.connect(db_path)
        self.verbose = verbose
        self._check_database_storage_version()

    def close_connection(self):
        self.connection.close()
    
    def _check_database_storage_version(self):
        pattern = struct.Struct('<8x4sQ')

        with open(self.db_path, 'rb') as fh:
            print(f"Database Storage version: {pattern.unpack(fh.read(pattern.size))[1]}")
    
    def show_table(self, table_name, limit=5):
        if self.verbose:
            if isinstance(table_name, str):
                self.connection.table(table_name).limit(limit).show()
            else:
                table_name.limit(limit).show()

    def show_all_tables(self):
        if self.verbose:
            tables = ["categories", "podcasts", "reviews"]
            for table in tables:
                self.show_table(table)

    def filter_podcasts(self):
        # Filtering out rows where average_rating or scraped_at is NULL
        filtered_podcasts = self.connection.table("podcasts").filter("average_rating IS NOT NULL AND scraped_at IS NOT NULL")
        if self.verbose:
            self.show_table(filtered_podcasts)
        return filtered_podcasts

    def join_and_select(self, table1, table2, primary_key, columns_table1, columns_table2, min_filter=None, max_filter=None):
        # Check if table1 and table2 are strings (table names) or DuckDBPyRelation objects
        if isinstance(table1, str):
            table1 = self.connection.table(table1)
        if isinstance(table2, str):
            table2 = self.connection.table(table2)
        
        # Perform the select operation on each table
        selected_table1 = table1.project(", ".join(columns_table1))
        
        if min_filter is None and max_filter is None:
            selected_table2 = table2.project(", ".join(columns_table2))
        elif min_filter is not None and max_filter is None:
            selected_table2 = table2.project(", ".join(columns_table2)).filter(f"average_rating >= {min_filter}")
        elif min_filter is None and max_filter is not None:
            selected_table2 = table2.project(", ".join(columns_table2)).filter(f"average_rating <= {max_filter}")
        else:
            selected_table2 = table2.project(", ".join(columns_table2)).filter(f"average_rating >= {min_filter} AND average_rating <= {max_filter}")
        
        # Perform the join operation
        joined_table = selected_table1.join(selected_table2, primary_key)
        
        # Display the result
        if self.verbose:
            self.show_table(joined_table)

        return joined_table

    def add_composed_column(self, table, columns, new_column_name):
        # Generate the expression to concatenate all the specified columns, ignoring NULL values
        coalesce_columns = [f"COALESCE({col}, '')" for col in columns]
        concat_expression = " || ' ' || ".join(coalesce_columns)
        
        # Add a new column composed of the concatenation of the specified columns
        # Project all columns except the ones to be concatenated
        all_columns = [col for col in table.columns]
        remaining_columns = [col for col in all_columns if col not in columns]
        
        # Add a new column composed of the concatenation of the specified columns
        if remaining_columns:
            remaining_columns_expression = ", ".join(remaining_columns)
            composed_table = table.project(f"{remaining_columns_expression}, {concat_expression} AS {new_column_name}")
        else:
            composed_table = table.project(f"*, {concat_expression} AS {new_column_name}")
        
        # Display the result
        if self.verbose:
            self.show_table(composed_table)

        return composed_table

    def fetch_column_records(self, table_name, columns):
        # Ensure columns is a list
        if isinstance(columns, str):
            columns = [columns]
        
        # Check if table_name is a string or a DuckDBPyRelation
        if isinstance(table_name, str):
            # Get the specified column from the table
            column_records = self.connection.table(table_name).project(", ".join(columns)).fetchall()
        elif isinstance(table_name, duckdb.DuckDBPyRelation):
            # Get the specified column from the DuckDBPyRelation
            column_records = table_name.project(", ".join(columns)).fetchall()
        else:
            raise ValueError("table_name must be either a string or a DuckDBPyRelation")
        
        # Return the list of records
        return column_records
