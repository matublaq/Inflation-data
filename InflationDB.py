import sqlite3
import os

##################################################################
# Define absolute path of database
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Project root directoriy
DB_PATH = os.path.join(BASE_DIR, 'InflationDB.db') # full path of the data base file

def get_db_connection():
    ''' Get and return the connection with data-base '''
    print(f'Connecting to database at: {DB_PATH}')
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON") # Foreign keys activate
    return conn
##################################################################


def InflationDB_scheme():
    
    #conn = sqlite3.connect('InflationDB.db') # Connect or create if that not exist
    conn = get_db_connection()
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

def insert_data_into_inflationDB(df):
    # Data-base connect
    conn = sqlite3.connect('InflationDB.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON') # Activate foreign keys


    # Insert countries with your codes
    countries = df[['country_code', 'country_name']].drop_duplicates().values.tolist()
    cursor.executemany('INSERT OR IGNORE INTO countries (country_code, country_name) VALUES (?, ?)', countries)

    # Insert years
    years = df['year'] # years columns
    cursor.executemany('INSERT OR IGNORE INTO years (year) VALUES (?)', years)

    # Transform al load inflation rates
    inflation_data = df[['country_code', 'year', 'inflation_rate']].values.tolist()
    cursor.executemany('INSERT OR IGNORE INTO inflation_data (country_code, year, inflation_rate) VALUES (?, ?, ?)', inflation_data)

    conn.commit()
    conn.close()