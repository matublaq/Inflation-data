import sqlite3 as sql

def InflationDB_scheme():
    conn = sql.connect('InflationDB.db') # Connect or create if that not exist
    cursor = conn.cursor()

    # On FK (foreign keys)
    cursor.execute("PRAGMA foreign_keys = ON")


    # Create countries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS countries (
                   country_code TEXT PRIMARY KEY, 
                   country_name TEXT NOT NULL UNIQUE
    )
''')
    
    # Create years table
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS years (
                   year integer PRIMARY KEY
    )
''')
    
    # Create inflation table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inflation_data (
                   country_code TEXT,   
                   year INTEGER, 
                   inflation_rate REAL, 
                   PRIMARY KEY (country_code, year), 
                   FOREIGN KEY (country_code) REFERENCES countries (country_code), 
                   FOREIGN KEY (year) REFERENCES years (year)
    )
''')
    
    # Save changes and close connection
    conn.commit()
    conn.close()
