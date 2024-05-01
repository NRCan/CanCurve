'''
Created on Apr. 30, 2024

@author: cef
'''

import sqlite3

def get_table_names(conn):
    """Retrieves a list of all tables (excluding default tables) from a SQLite database connection.

    Args:
        conn: A connection object to the SQLite database.

    Returns:
        A list of table names (excluding default tables).
    """

    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    table_names = [row[0] for row in cursor.fetchall()]
    return table_names
    