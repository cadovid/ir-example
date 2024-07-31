import struct

import duckdb

from utils.common import LOGGER


class Database:
    """
    A class to interact with an SQLite database using DuckDB.

    This class provides methods to connect to a database, check its version,
    display tables, filter data, join tables, add composed columns, and fetch records.

    Attributes:
        db_path (str): Path to the SQLite database file.
        connection (duckdb.DuckDBPyConnection): Connection object to the database.
        verbose (bool): Flag to control the verbosity of output.
    """

    def __init__(self, db_path, verbose):
        """
        Initializes the Database instance.

        Args:
            db_path (str): Path to the SQLite database file.
            verbose (bool): Flag to enable verbose output.
        """
        self.db_path = db_path
        self.connection = duckdb.connect(db_path)
        self.verbose = verbose
        self._check_database_storage_version()

    def close_connection(self):
        """
        Closes the connection to the database.
        """
        self.connection.close()

    def _check_database_storage_version(self):
        """
        Checks and logs the storage version of the database.

        The version is read from the database file header.
        """
        pattern = struct.Struct("<8x4sQ")

        with open(self.db_path, "rb") as fh:
            LOGGER.info(
                f"Database Storage version: {pattern.unpack(fh.read(pattern.size))[1]}"
            )

    def show_table(self, table_name, limit=5):
        """
        Displays the contents of a specified table.

        Args:
            table_name (str or duckdb.DuckDBPyRelation): The name of the table or DuckDBPyRelation object.
            limit (int): The number of rows to display. Default is 5.
        """
        if self.verbose:
            if isinstance(table_name, str):
                self.connection.table(table_name).limit(limit).show()
            else:
                table_name.limit(limit).show()

    def show_all_tables(self):
        """
        Displays the contents of all predefined tables ("categories", "podcasts", "reviews").

        This method is called only if verbose output is enabled.
        """
        if self.verbose:
            tables = ["categories", "podcasts", "reviews"]
            for table in tables:
                self.show_table(table)

    def filter_podcasts(self):
        """
        Filters the "podcasts" table to remove rows where `average_rating` or `scraped_at` is NULL.

        Returns:
            duckdb.DuckDBPyRelation: Filtered DuckDBPyRelation object containing non-null podcasts.
        """
        # Filtering out rows where average_rating or scraped_at is NULL
        filtered_podcasts = self.connection.table("podcasts").filter(
            "average_rating IS NOT NULL AND scraped_at IS NOT NULL"
        )
        if self.verbose:
            self.show_table(filtered_podcasts)
        return filtered_podcasts

    def join_and_select(
        self,
        table1,
        table2,
        primary_key,
        columns_table1,
        columns_table2,
        min_filter=None,
        max_filter=None,
        min_date=None,
        max_date=None,
    ):
        """
        Joins two tables on a specified primary key and selects specific columns.

        Args:
            table1 (str or duckdb.DuckDBPyRelation): The first table or DuckDBPyRelation object.
            table2 (str or duckdb.DuckDBPyRelation): The second table or DuckDBPyRelation object.
            primary_key (str): The column name to join on.
            columns_table1 (list of str): List of column names from the first table.
            columns_table2 (list of str): List of column names from the second table.
            min_filter (Optional[float]): Minimum value for filtering the `average_rating` column.
            max_filter (Optional[float]): Maximum value for filtering the `average_rating` column.
            min_date (Optional[str]): Minimum date for filtering the `scraped_at` column.
            max_date (Optional[str]): Maximum date for filtering the `scraped_at` column.

        Returns:
            duckdb.DuckDBPyRelation: Joined and filtered DuckDBPyRelation object.
        """
        # Check if table1 and table2 are strings (table names) or DuckDBPyRelation objects
        if isinstance(table1, str):
            table1 = self.connection.table(table1)
        if isinstance(table2, str):
            table2 = self.connection.table(table2)

        # Perform the select operation on each table
        selected_table1 = table1.project(", ".join(columns_table1))

        # Build the filter condition for table2
        filters = []
        if min_filter is not None:
            filters.append(f"average_rating >= {min_filter}")
        if max_filter is not None:
            filters.append(f"average_rating <= {max_filter}")
        if min_date is not None:
            filters.append(f"scraped_at >= '{min_date}'")
        if max_date is not None:
            filters.append(f"scraped_at <= '{max_date}'")

        # Apply the filters to table2
        if filters:
            filter_condition = " AND ".join(filters)
            selected_table2 = table2.project(", ".join(columns_table2)).filter(
                filter_condition
            )
        else:
            selected_table2 = table2.project(", ".join(columns_table2))

        # Perform the join operation
        joined_table = selected_table1.join(selected_table2, primary_key)

        # Display the result
        if self.verbose:
            self.show_table(joined_table)

        return joined_table

    def add_composed_column(self, table, columns, new_column_name):
        """
        Adds a new column to a table that is a concatenation of the specified columns.

        Args:
            table (duckdb.DuckDBPyRelation): The DuckDBPyRelation object to modify.
            columns (list of str): List of column names to concatenate.
            new_column_name (str): The name of the new composed column.

        Returns:
            duckdb.DuckDBPyRelation: Modified DuckDBPyRelation object with the new column.
        """
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
            composed_table = table.project(
                f"{remaining_columns_expression}, {concat_expression} AS {new_column_name}"
            )
        else:
            composed_table = table.project(
                f"*, {concat_expression} AS {new_column_name}"
            )

        # Display the result
        if self.verbose:
            self.show_table(composed_table)

        return composed_table

    def fetch_column_records(self, table_name, columns):
        """
        Fetches records of specified columns from a table.

        Args:
            table_name (str or duckdb.DuckDBPyRelation): The name of the table or DuckDBPyRelation object.
            columns (str or list of str): Column name(s) to fetch. If a single column, can be a string.

        Returns:
            list of tuple: List of records from the specified columns.

        Raises:
            ValueError: If `table_name` is not a string or DuckDBPyRelation, or `columns` is not a list or string.
        """
        # Ensure columns is a list
        if isinstance(columns, str):
            columns = [columns]

        # Check if table_name is a string or a DuckDBPyRelation
        if isinstance(table_name, str):
            # Get the specified column from the table
            column_records = (
                self.connection.table(table_name).project(", ".join(columns)).fetchall()
            )
        elif isinstance(table_name, duckdb.DuckDBPyRelation):
            # Get the specified column from the DuckDBPyRelation
            column_records = table_name.project(", ".join(columns)).fetchall()
        else:
            raise ValueError("table_name must be either a string or a DuckDBPyRelation")

        # Return the list of records
        return column_records
