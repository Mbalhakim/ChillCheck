
class Database:
    import sqlite3

    def __init__(self):
        pass

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def get_connection(self):
        """Get database connection"""
        con = Database.sqlite3.connect("acs.db")
        con.row_factory = Database.sqlite3.Row
        return con
    
    def get_cursor(self, con):
        """Get cursor from connection"""
        cur = con.cursor()
        cur.row_factory = self.dict_factory
        return cur
    
    def find_all(self, table):
        """Get all rows in the table"""
        con = self.get_connection()
        cur = self.get_cursor(con)

        query = f"SELECT * from {table}"
        rows = cur.execute(query).fetchall()
        cur.close()
        con.close()
        return rows

    def find(self, table, column, value):
        """Get table row by column and value"""
        con = self.get_connection()
        cur = self.get_cursor(con)

        query = f"SELECT rowid, * from {table} WHERE {column} = ?;"
        row = cur.execute(query, (value,)).fetchone()
        cur.close()
        con.close()
        return row

    def create(self, query, data):
        """Insert a new row with data into the table"""
        con = self.get_connection()
        cur = self.get_cursor(con)

        cur.execute(query, data)
        con.commit()
        cur.close()
        con.close()

    def delete_by_id(self, table, id_):
        """Delete table row by rowid"""
        con = self.get_connection()
        cur = self.get_cursor(con)
        
        query = f"DELETE FROM {table} WHERE id = ?;"
        cur.execute(query, (id_,))
        con.commit()
        cur.close()
        con.close()
    
    # def create_tables(self):
        # con = self.get_connection()
        # cur = self.get_cursor(con)

        # company_table = "CREATE TABLE Company (id INTEGER PRIMARY KEY, name TEXT NOT NULL, postcode TEXT NOT NULL, address TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);"
        # account_type_table = "CREATE TABLE AccountType (id INTEGER PRIMARY KEY, name TEXT NOT NULL);"
        # user_table = "CREATE TABLE User (id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL, company INTEGER NOT NULL, date_of_birth TEXT DEFAULT CURRENT_TIMESTAMP, account_type INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (company) REFERENCES Company (id), FOREIGN KEY (account_type) REFERENCES AccountType (id));"
        # mlx_data_table = "CREATE TABLE MlxData (id INTEGER PRIMARY KEY, min_temp INTEGER NOT NULL, max_temp INTEGER NOT NULL, avg_temp INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);"
        # sht_data_table = "CREATE TABLE ShtData (id INTEGER PRIMARY KEY, air_quality TEXT NOT NULL, eco2 REAL NOT NULL, tvoc REAL NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);"
        # daily_average_table = "CREATE TABLE DailyAverage (id INTEGER PRIMARY KEY, mlx_avg INTEGER NOT NULL, sht_avg INTEGER NOT NULL, date TEXT DEFAULT CURRENT_TIMESTAMP, day TEXT NOT NULL);"
        
        # room_table = "CREATE TABLE Room (id INTEGER PRIMARY KEY, name TEXT NOT NULL, floor INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);"
        # feedback_slider_table = "CREATE TABLE FeedbackSlider (id INTEGER PRIMARY KEY, text_value TEXT NOT NULL);"
        # feedback_table = "CREATE TABLE Feedback (id INTEGER PRIMARY KEY, room INTEGER NOT NULL, feedback_slider INTEGER NOT NULL, feedback_text TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);"

        # query = sht_data_table
        # print(query)
        # cur.execute(query)