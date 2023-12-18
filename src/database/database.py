"""
Class for SQLite Database

Date:
    27-10-2023

"""

import sqlite3
from typing import Any

NAME = "database.db"
EXPECTED_TABLE_CONTENT = {
    'settings': [('address', 'text'),
                 ('city', 'text'),
                 ('postal', 'text'),
                 ('country', 'text'),
                 ('price_area', 'text'),
                 ('solar_strategy', 'text'),
                 ('solcast_key', 'text'),
                 ('solcast_ids', 'text'),
                 ('tariff_company', 'text'),
                 ('provider', 'text'),
                 ('basis', 'text'),
                 ('prices', 'text'),
                 ('capacity', 'text'),
                 ('effectivity', 'text'),
                 ('threshold', 'text'),
                 ('max_rate', 'text'),
                 ('model', 'text')],

    'plan': [('Time', 'text'),
             ('Action', 'text'),
             ('SolarSurplus', 'float'),
             ('ElNetCharge', 'float'),
             ('BatteryDelta', 'float'),
             ('BatteryExpected', 'float'),
             ('SolarExport', 'float'),
             ('ActionReason', 'text'),
             ('Price', 'float'),
             ('SpotPrice', 'float'),
             ('Power', 'int'),
             ('ExpectedConsumption', 'float')],
}
EXPECTED_TABLES = list(EXPECTED_TABLE_CONTENT.keys())

class Database:
    """ Class for handling Database transactions with an open connection """
    def __init__(self):
        self.conn = sqlite3.connect(NAME)

    def __del__(self):
        self.conn.close()

    def create_missing_tables(self) -> None:
        """ Check current tables in database and create missing tables """
        current_tables = self.get_all_table_names()
        missing_tables = [table for table in EXPECTED_TABLES if table not in current_tables]

        if missing_tables:
            sql_str_start = """CREATE TABLE IF NOT EXISTS """

            for table in missing_tables:
                table_content = EXPECTED_TABLE_CONTENT[table]
                sql_str = sql_str_start + f"{table} ("

                for content in table_content:
                    sql_str += f"{content[0]} {content[1]},"
                sql_str = sql_str[:-1] + ')'

                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(sql_str)


    def get_all_table_names(self) -> Any:
        """ Get a list of current table names in database 
        
        Returns:
            List with all table names or an empty list if no tables in database

        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name""")
            result = cursor.fetchall()
        
        if result:
            return [res[0] for res in result]
        return []
    

    def check_for_empty_table(self, table_name: str) -> bool:
        """ Check if specified table in database is empty

        Args:
            table_name: Name of table in database to check

        Returns:
            True/False if table exists or not in database

        """
        sql_str = f"""SELECT CASE WHEN EXISTS (SELECT 1 FROM {table_name})
                      THEN 0 ELSE 1 END AS IsEmpty"""
        
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_str)
            result = cursor.fetchone()[0]

        if result == 1:
            return True
        return False


    def insert_into_table(self, table_name: str, table_content: tuple) -> None: # type: ignore
        """ Inserts content into specified table in database

        Args:
            table_name: Name of table in database to insert into
            table_content: Data to insert into table

        """
        sql_str = f"INSERT INTO {table_name} VALUES ("

        for _ in range(len(table_content)):
            sql_str += '?,'
        sql_str = sql_str[:-1] + ')'

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_str, table_content)


    def update_table(self, table_name: str, table_content: tuple) -> None: # type: ignore
        """ Update specified table in database

        Args:
            table_name: Name of table in database to update
            table_content: Data to be updated in table

        """
        table_to_update = [table for table in EXPECTED_TABLES if table == table_name]

        if not table_to_update:
            # Error! Do something ...
            pass
        table_columns = [column[0] for column in EXPECTED_TABLE_CONTENT[table_to_update[0]]]
        
        set_list = []
        for column, value in zip(table_columns, table_content):
            if str(value):      # Not an empty string!
                set_list.append(f"{column} = '{value}'")
            elif value == 0:    # If value is an integer 0
                set_list.append(f"{column} = '{value}'")
            else:               # An empty string!
                set_list.append(f"{column} = ''")
        set_clause = ', '.join(set_list)
        sql_str = f"""UPDATE {table_to_update[0]} SET {set_clause} WHERE rowid=1"""

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_str)


    def load_settings(self) -> dict[str, str]:
        """ Loads user settings from database into application memory

        Returns:
            Dict with saved user profile settings from database

        """
        sql_str = "SELECT * FROM settings"
        
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_str)
            description = cursor.description
            result = cursor.fetchall()[0]

        return {column[0]:value for (column, value) in zip(description, result)}
    

    def load_plan(self) -> dict[str, str]:
        """ Loads saved plan from database into application memory
        
        Returns:
            Dict with saved plan from database

        """
        sql_str = "SELECT * FROM plan"

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(sql_str)
            description = cursor.description
            result = cursor.fetchall()[0]

        return {column[0]:value for (column, value) in zip(description, result)}
